from datetime import date
from typing import Optional
from uuid import UUID

from anthropic import AsyncAnthropic
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.knowledge_item import KnowledgeItem
from app.models.base import KnowledgeCategory


class MemoryService:
    """RAG over institutional knowledge."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text using Claude's embedding endpoint.

        Note: This is a placeholder. In production, use a proper embedding
        model like voyage-3 or text-embedding-3-large.
        """
        # Placeholder - return zeros. Real implementation would call
        # an embedding API
        return [0.0] * 1536

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
            KnowledgeItem.is_active == True,
        ]

        if category:
            conditions.append(KnowledgeItem.category == category)

        if tags:
            # Filter items that have any of the specified tags
            conditions.append(KnowledgeItem.tags.overlap(tags))

        # Check effective/expiry dates
        today = date.today()
        conditions.append(
            (KnowledgeItem.effective_date == None)
            | (KnowledgeItem.effective_date <= today)
        )
        conditions.append(
            (KnowledgeItem.expiry_date == None) | (KnowledgeItem.expiry_date >= today)
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
