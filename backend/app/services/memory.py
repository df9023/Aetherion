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


def _fake_embedding(text: str) -> list[float]:
    """Deterministic 1536-dim pseudo-embedding from text content.

    Uses overlapping hash windows so semantically related content
    (sharing words/phrases) produces closer vectors than unrelated content.
    Good enough for dev/test without an API key.
    """
    words = text.lower().split()
    vec = [0.0] * 1536

    for i, word in enumerate(words):
        h = hashlib.sha256(word.encode()).digest()
        for j in range(0, min(32, len(h)), 2):
            idx = int.from_bytes(h[j : j + 2], "big") % 1536
            vec[idx] += 1.0

        if i + 1 < len(words):
            bigram = f"{word} {words[i + 1]}"
            h2 = hashlib.sha256(bigram.encode()).digest()
            for j in range(0, min(32, len(h2)), 2):
                idx = int.from_bytes(h2[j : j + 2], "big") % 1536
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
        self._openai_client = None

        if self.settings.openai_api_key:
            from openai import AsyncOpenAI

            self._openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        else:
            logger.warning(
                "OPENAI_API_KEY not set — using hash-based fake embeddings. "
                "Set the key for real semantic search."
            )

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate a 1536-dim embedding for *text*.

        Uses OpenAI text-embedding-3-small when OPENAI_API_KEY is configured.
        Falls back to a deterministic hash-based embedding otherwise (dev mode).
        """
        if self._openai_client is None:
            return _fake_embedding(text)

        response = await self._openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

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
    ) -> KnowledgeItem:
        """Create a new knowledge item with embedding."""
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
