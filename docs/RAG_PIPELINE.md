# RAG Pipeline Specification — Memory Module

This document specifies how Aetherion's Memory module ingests, stores, retrieves, and uses institutional knowledge. Claude Code should reference this when building any part of the retrieval-augmented generation pipeline.

## Overview

Memory is the institutional knowledge graph. It captures product rules, regulatory content, internal policies, playbooks, precedent decisions, and expert knowledge. When the Reasoner generates a recommendation, it retrieves relevant knowledge from Memory to ground its output in evidence.

## Ingestion Pipeline

### Supported Input Formats
- PDF (product brochures, regulatory documents, policy manuals)
- Word documents (.docx — internal playbooks, process guides)
- Markdown / plain text (manual knowledge entries)
- Structured data (CSV/JSON — product comparison tables, fee schedules)

### Processing Steps

1. **Upload & classify**: User uploads document, selects category (product_rule, internal_policy, regulatory_requirement, playbook, precedent, faq, process_guide)
2. **Extract text**: Parse document content. Use python-docx for Word, PyMuPDF or pdfplumber for PDF.
3. **Chunk**: Split into semantically meaningful chunks.
4. **Enrich**: Add metadata (source document, page number, section heading, category, effective date).
5. **Embed**: Generate vector embeddings for each chunk.
6. **Store**: Save chunk text + metadata + embedding to PostgreSQL (KnowledgeItem table + pgvector).

### Chunking Strategy

Use a hybrid approach:
- **Primary:** Split by document structure (headings, sections). Respect natural document boundaries.
- **Fallback:** If no clear structure, use recursive character splitting with 800 token chunks and 100 token overlap.
- **Special handling for tables:** Keep tables intact as single chunks. Don't split rows across chunks.
- **Max chunk size:** 1000 tokens. If a section exceeds this, split at paragraph boundaries.

Each chunk becomes a KnowledgeItem record.

### Embedding Model

- **Model:** text-embedding-3-small (OpenAI) or Cohere embed-v3 — evaluate cost vs. quality
- **Dimensions:** 1536 (OpenAI) or 1024 (Cohere)
- **pgvector column:** `embedding vector(1536)` on KnowledgeItem table
- **Index:** Create HNSW index for fast approximate nearest neighbor search

```sql
CREATE INDEX ON knowledge_items USING hnsw (embedding vector_cosine_ops);
```

## Retrieval Pipeline

### When Retrieval Happens

The Reasoner calls Memory retrieval at these points:
1. **Case preparation**: When an advisor opens a case, retrieve relevant product rules, policies, and precedent for the client's pension type and situation.
2. **Recommendation generation**: When generating a recommendation, retrieve evidence to support or challenge each reasoning step.
3. **Compliance check**: When Control validates a recommendation, retrieve relevant regulatory requirements and internal policies.
4. **Knowledge search**: When a user explicitly searches for institutional knowledge through the Workbench.

### Retrieval Strategy

Use a two-stage retrieval approach:

**Stage 1 — Candidate retrieval (fast, broad)**
- Semantic search: Embed the query, find top-K nearest neighbors via pgvector (K=20)
- Metadata filter: Scope to the user's organization, active items only, relevant categories
- Optional: Keyword filter if the query contains specific product names or regulatory references

```python
async def retrieve_candidates(
    query: str,
    organization_id: UUID,
    categories: list[str] | None = None,
    top_k: int = 20
) -> list[KnowledgeItem]:
    query_embedding = await embed(query)
    # pgvector cosine similarity search with metadata filters
    ...
```

**Stage 2 — Reranking (accurate, narrow)**
- Take top-20 candidates from Stage 1
- Rerank using cross-encoder or LLM-based relevance scoring
- Return top-5 most relevant chunks to the Reasoner

For MVP, Stage 2 can be skipped. Start with Stage 1 only (top-5 from semantic search) and add reranking when retrieval quality needs improvement.

### Query Construction

Don't just embed the raw user query. Construct a retrieval query that includes context:

```python
def build_retrieval_query(case: Case, question: str) -> str:
    return f"""
    Client situation: {case.case_type}, collective agreement: {case.client.collective_agreement}
    Question: {question}
    """
```

This gives the embedding model richer context for better matches.

## Integration with Reasoner

When the Reasoner generates a recommendation, it should:

1. Formulate retrieval queries based on the case context and each reasoning step
2. Retrieve relevant knowledge items
3. Include retrieved content in the LLM prompt as grounding context
4. Cite specific knowledge items in the reasoning chain (by KnowledgeItem ID)
5. Create Evidence records linking retrieved items to the Recommendation

### Prompt Pattern

```
You are a pension advisory assistant. Use the following institutional knowledge
to support your recommendation. Cite sources by their ID.

## Relevant Knowledge
{retrieved_chunks_with_ids}

## Case Context
{case_details}

## Task
{recommendation_task}

For each point in your recommendation, cite the knowledge items that support it.
If you cannot find supporting evidence for a claim, flag it as unsupported.
```

## Knowledge Freshness

- Knowledge items have optional `effective_date` and `expiry_date` fields
- Retrieval should filter out expired items by default
- When product rules or regulations change, the old item should be marked inactive and a new version created (not edited in place, for audit trail)
- Include a "last reviewed" indicator so organizations know which knowledge items may be stale

## Metrics to Track

- Retrieval latency (P50, P95)
- Number of chunks retrieved per query
- Citation rate (what percentage of recommendations cite at least one knowledge item)
- Knowledge coverage (which categories have the most/least content)
- User feedback on retrieval relevance (thumbs up/down on cited evidence)

## MVP Scope

For the first working version, implement:
1. Document upload (PDF and Word)
2. Text extraction and chunking
3. Embedding and storage in pgvector
4. Basic semantic search retrieval (Stage 1 only, top-5)
5. Integration with Reasoner prompts
6. Evidence record creation linking retrievals to recommendations

Defer to later:
- Reranking (Stage 2)
- Structured table extraction
- Knowledge versioning and freshness management
- Advanced query construction
- Retrieval analytics dashboard
