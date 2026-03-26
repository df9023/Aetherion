import hashlib
import logging
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.knowledge_item import KnowledgeItem
from app.models.base import KnowledgeCategory

logger = logging.getLogger(__name__)


def _fake_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """Deterministic pseudo-embedding from text content.

    Uses overlapping hash windows so semantically related content
    (sharing words/phrases) produces closer vectors than unrelated content.
    Good enough for dev/test without an API key.
    """
    words = text.lower().split()
    vec = [0.0] * dimensions

    for i, word in enumerate(words):
        h = hashlib.sha256(word.encode()).digest()
        for j in range(0, min(32, len(h)), 2):
            idx = int.from_bytes(h[j : j + 2], "big") % dimensions
            vec[idx] += 1.0

        if i + 1 < len(words):
            bigram = f"{word} {words[i + 1]}"
            h2 = hashlib.sha256(bigram.encode()).digest()
            for j in range(0, min(32, len(h2)), 2):
                idx = int.from_bytes(h2[j : j + 2], "big") % dimensions
                vec[idx] += 0.5

    magnitude = sum(v * v for v in vec) ** 0.5
    if magnitude > 0:
        vec = [v / magnitude for v in vec]

    return vec


class MemoryService:
    """RAG over institutional knowledge."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self._voyage_client = None
        self._openai_client = None
        self._provider: str = "hash"

        # Priority: Voyage > OpenAI > hash fallback
        if self.settings.voyage_api_key:
            import voyageai

            self._voyage_client = voyageai.Client(
                api_key=self.settings.voyage_api_key,
            )
            self._provider = "voyage"
            logger.info("Using Voyage AI (voyage-3) for embeddings (dim=1024)")
        elif self.settings.openai_api_key:
            from openai import AsyncOpenAI

            self._openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            self._provider = "openai"
            logger.info("Using OpenAI (text-embedding-3-small) for embeddings (dim=1536)")
        else:
            logger.warning(
                "No embedding API key set — using hash-based fake embeddings. "
                "Set VOYAGE_API_KEY or OPENAI_API_KEY for real semantic search."
            )

    @property
    def embedding_dimensions(self) -> int:
        """Return the dimension for the current embedding provider."""
        if self._provider == "voyage":
            return 1024
        if self._provider == "openai":
            return 1536
        return self.settings.embedding_dimensions

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for *text*.

        Uses Voyage AI voyage-3 when VOYAGE_API_KEY is configured,
        OpenAI text-embedding-3-small when OPENAI_API_KEY is configured,
        or falls back to a deterministic hash-based embedding (dev mode).
        """
        if self._voyage_client is not None:
            result = self._voyage_client.embed(
                [text], model="voyage-3",
            )
            return result.embeddings[0]

        if self._openai_client is not None:
            response = await self._openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding

        return _fake_embedding(text, self.embedding_dimensions)

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts efficiently."""
        if self._voyage_client is not None:
            # Voyage supports batch embedding natively
            result = self._voyage_client.embed(
                texts, model="voyage-3",
            )
            return result.embeddings

        if self._openai_client is not None:
            response = await self._openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts,
            )
            return [d.embedding for d in response.data]

        return [_fake_embedding(t, self.embedding_dimensions) for t in texts]

    async def create_knowledge_item(
        self,
        organization_id: UUID,
        created_by: UUID,
        title: str,
        content: str,
        category: KnowledgeCategory,
        source: str,
        tags: list[str] = None,
        effective_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
        embedding: list[float] | None = None,
        source_location: dict | None = None,
    ) -> KnowledgeItem:
        """Create a new knowledge item with embedding."""
        if embedding is None:
            embedding = await self.generate_embedding(content)

        item = KnowledgeItem(
            organization_id=organization_id,
            title=title,
            content=content,
            category=category,
            source=source,
            tags=tags or [],
            embedding=embedding,
            effective_date=effective_date,
            expiry_date=expiry_date,
            created_by=created_by,
            source_location=source_location,
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def search(
        self,
        organization_id: UUID,
        query: str,
        category: Optional[KnowledgeCategory] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10,
    ) -> list[KnowledgeItem]:
        """Semantic search over knowledge items."""
        query_embedding = await self.generate_embedding(query)

        # Build base query with organization scope
        conditions = [
            KnowledgeItem.organization_id == organization_id,
            KnowledgeItem.is_active.is_(True),
        ]

        if category:
            conditions.append(KnowledgeItem.category == category)

        if tags:
            # Filter items that have any of the specified tags
            conditions.append(KnowledgeItem.tags.overlap(tags))

        # Check effective/expiry dates
        today = date.today()
        conditions.append(
            (KnowledgeItem.effective_date.is_(None))
            | (KnowledgeItem.effective_date <= today)
        )
        conditions.append(
            (KnowledgeItem.expiry_date.is_(None)) | (KnowledgeItem.expiry_date >= today)
        )

        # Use pgvector's cosine distance for similarity search
        query_stmt = (
            select(KnowledgeItem)
            .where(and_(*conditions))
            .order_by(KnowledgeItem.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await self.db.execute(query_stmt)
        return list(result.scalars().all())

    async def get_relevant_knowledge(
        self,
        organization_id: UUID,
        context: str,
        categories: Optional[list[KnowledgeCategory]] = None,
        limit: int = 5,
    ) -> list[KnowledgeItem]:
        """Retrieve knowledge items relevant to a given context."""
        items = []
        if categories:
            for category in categories:
                category_items = await self.search(
                    organization_id=organization_id,
                    query=context,
                    category=category,
                    limit=limit // len(categories) + 1,
                )
                items.extend(category_items)
        else:
            items = await self.search(
                organization_id=organization_id,
                query=context,
                limit=limit,
            )

        # Deduplicate and limit
        seen = set()
        unique_items = []
        for item in items:
            if item.id not in seen:
                seen.add(item.id)
                unique_items.append(item)
                if len(unique_items) >= limit:
                    break

        return unique_items
