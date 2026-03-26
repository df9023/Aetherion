import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Approximate: 1 token ≈ 0.75 words for Swedish text
WORDS_PER_TOKEN = 0.75
TARGET_MIN_TOKENS = 500
TARGET_MAX_TOKENS = 800
MAX_TOKENS = 1000
OVERLAP_SENTENCES = 2

# Swedish regulatory reference patterns — never split across these
_REGULATORY_REF = re.compile(
    r'(?:'
    r'\d+\s+kap\.\s+\d+\s*§'           # "3 kap. 2 §"
    r'|FFFS\s+\d{4}:\d+'                # "FFFS 2018:10"
    r'|SFS\s+\d{4}:\d+'                 # "SFS 2010:2043"
    r'|\d+\s*§\s*\d*\s*(?:st|mom)\.'    # "5 § 2 st." or "5 § 3 mom."
    r'|FRL\s+\d+'                        # "FRL 12"
    r'|LFV\s+\d+'                        # "LFV 3"
    r')',
)


def _word_count(text: str) -> int:
    return len(text.split())


def _approx_tokens(text: str) -> int:
    return int(_word_count(text) / WORDS_PER_TOKEN)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling Swedish abbreviations and regulatory refs.

    Never splits in the middle of regulatory references like "3 kap. 2 §".
    """
    # Protect regulatory references by replacing their periods temporarily
    protected = text
    placeholders: list[tuple[str, str]] = []
    for i, m in enumerate(_REGULATORY_REF.finditer(text)):
        placeholder = f"\x00REF{i}\x00"
        placeholders.append((placeholder, m.group()))
        protected = protected.replace(m.group(), placeholder, 1)

    # Also protect common Swedish abbreviations with periods
    abbrevs = ['t.ex.', 'bl.a.', 'dvs.', 'd.v.s.', 's.k.', 'resp.', 'etc.', 'fr.o.m.', 't.o.m.', 'kap.', 'st.', 'mom.']
    abbrev_placeholders: list[tuple[str, str]] = []
    for j, abbr in enumerate(abbrevs):
        placeholder = f"\x00ABBR{j}\x00"
        if abbr in protected:
            abbrev_placeholders.append((placeholder, abbr))
            protected = protected.replace(abbr, placeholder)

    # Split on sentence-ending punctuation followed by whitespace and a capital letter
    parts = re.split(r'(?<=[.!?])\s+(?=[A-ZÅÄÖ])', protected)

    # Restore placeholders
    restored: list[str] = []
    for part in parts:
        for placeholder, original in placeholders:
            part = part.replace(placeholder, original)
        for placeholder, original in abbrev_placeholders:
            part = part.replace(placeholder, original)
        s = part.strip()
        if s:
            restored.append(s)

    return restored


def _detect_sections(text: str) -> list[tuple[str | None, str]]:
    """Split text into (heading, body) pairs by detecting logical sections."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    heading_pattern = re.compile(
        r'^(?:'
        r'(?:\d+\.[\d.]*)\s+.{3,80}$'       # "1.2 Section Name"
        r'|[A-ZÅÄÖ][A-ZÅÄÖ\s\-:]{5,80}$'    # "ALL CAPS HEADING"
        r'|(?:Kapitel|Avsnitt|Artikel|Section|Chapter)\s+.{1,80}$'  # Swedish/English markers
        r')',
        re.MULTILINE,
    )

    sections: list[tuple[str | None, str]] = []
    blocks = re.split(r'\n{2,}', text)

    current_heading: str | None = None
    current_body_parts: list[str] = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if heading_pattern.match(block) and _word_count(block) <= 15:
            if current_body_parts:
                body = '\n\n'.join(current_body_parts)
                sections.append((current_heading, body))
                current_body_parts = []
            current_heading = block
        else:
            current_body_parts.append(block)

    if current_body_parts:
        sections.append((current_heading, '\n\n'.join(current_body_parts)))

    if not sections:
        sections = [(None, text)]

    return sections


@dataclass
class DocumentChunk:
    content: str
    section_heading: str | None
    chunk_index: int
    source_location: dict = field(default_factory=dict)  # {"start_char": int, "end_char": int}
    metadata: dict = field(default_factory=dict)


class ChunkerService:
    """Splits extracted document text into chunks suitable for embedding."""

    def __init__(
        self,
        target_min_tokens: int = TARGET_MIN_TOKENS,
        target_max_tokens: int = TARGET_MAX_TOKENS,
        max_tokens: int = MAX_TOKENS,
        overlap_sentences: int = OVERLAP_SENTENCES,
    ):
        self.target_min_tokens = target_min_tokens
        self.target_max_tokens = target_max_tokens
        self.max_tokens = max_tokens
        self.overlap_sentences = overlap_sentences

    def chunk_document(
        self,
        text: str,
        source_title: str,
        metadata: dict | None = None,
    ) -> list[DocumentChunk]:
        """Split document text into semantically meaningful chunks.

        Strategy:
        1. Split by logical sections (headings, numbered paragraphs, double newlines)
        2. If a section is too long, split by sentences within the section
        3. Include overlap sentences between adjacent chunks
        4. Track character offsets for source_location
        """
        base_metadata = metadata or {}
        sections = _detect_sections(text)
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for heading, body in sections:
            # Find the character offset of this section body in the original text
            section_start = text.find(body)
            if section_start == -1:
                section_start = 0

            section_chunks = self._chunk_section(body, heading)
            for content in section_chunks:
                # Find offset of this chunk within the original text
                chunk_start = text.find(content, section_start)
                if chunk_start == -1:
                    chunk_start = section_start
                chunk_end = chunk_start + len(content)

                chunk_meta = {
                    **base_metadata,
                    "source_title": source_title,
                    "chunk_index": chunk_index,
                }
                if heading:
                    chunk_meta["section_heading"] = heading

                source_location = {
                    "start_char": chunk_start,
                    "end_char": chunk_end,
                }

                chunks.append(DocumentChunk(
                    content=content,
                    section_heading=heading,
                    chunk_index=chunk_index,
                    source_location=source_location,
                    metadata=chunk_meta,
                ))
                chunk_index += 1

        logger.info(
            "Chunked document '%s' into %d chunks",
            source_title, len(chunks),
        )
        return chunks

    def _chunk_section(self, text: str, heading: str | None) -> list[str]:
        """Split a section into target-sized chunks with sentence overlap.

        Never splits mid-sentence — always breaks at sentence boundaries.
        """
        tokens = _approx_tokens(text)

        # If within target range, return as single chunk
        if tokens <= self.target_max_tokens:
            return [text.strip()] if text.strip() else []

        # Split into sentences and group into chunks
        sentences = _split_sentences(text)
        if not sentences:
            return [text.strip()] if text.strip() else []

        chunks: list[str] = []
        current_sentences: list[str] = []
        current_tokens = 0

        for sentence in sentences:
            sent_tokens = _approx_tokens(sentence)

            # If adding this sentence exceeds max, flush current chunk
            if current_tokens + sent_tokens > self.max_tokens and current_sentences:
                chunk_text = ' '.join(current_sentences).strip()
                if chunk_text:
                    chunks.append(chunk_text)

                # Overlap: keep last N sentences for context continuity
                overlap = current_sentences[-self.overlap_sentences:]
                current_sentences = list(overlap)
                current_tokens = sum(_approx_tokens(s) for s in overlap)

            current_sentences.append(sentence)
            current_tokens += sent_tokens

        # Flush remaining
        if current_sentences:
            chunk_text = ' '.join(current_sentences).strip()
            if chunk_text:
                # If this is very small and we have a previous chunk, merge
                if chunks and _approx_tokens(chunk_text) < self.target_min_tokens // 2:
                    combined = chunks[-1] + ' ' + chunk_text
                    if _approx_tokens(combined) <= self.max_tokens:
                        chunks[-1] = combined
                    else:
                        chunks.append(chunk_text)
                else:
                    chunks.append(chunk_text)

        return chunks
