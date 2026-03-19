from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.base import DocumentType, FileFormat
from app.models.case import Case
from app.models.document import Document
from app.models.recommendation import Recommendation
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService

router = APIRouter()


class GenerateDocumentRequest(BaseModel):
    file_format: Optional[FileFormat] = FileFormat.DOCX


@router.post(
    "/recommendations/{recommendation_id}/generate-document",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["recommendations", "documents"],
)
async def generate_document(
    recommendation_id: UUID,
    body: GenerateDocumentRequest,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Document:
    """Generate a recommendation pack document (DOCX or PDF)."""

    # Verify recommendation belongs to user's organization
    result = await db.execute(
        select(Recommendation)
        .join(Case, Case.id == Recommendation.case_id)
        .where(
            Recommendation.id == recommendation_id,
            Case.organization_id == organization_id,
        )
    )
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    service = DocumentService(db)
    document = await service.generate_recommendation_pack(
        recommendation_id=recommendation_id,
        generated_by=current_user.id,
        organization_id=organization_id,
        file_format=body.file_format or FileFormat.DOCX,
    )

    await db.commit()
    return document


@router.get(
    "/documents/{document_id}/download",
    tags=["documents"],
)
async def download_document(
    document_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> FileResponse:
    """Download a generated document file."""

    # Load document and verify org ownership via case
    result = await db.execute(
        select(Document)
        .join(Case, Case.id == Document.case_id)
        .where(
            Document.id == document_id,
            Case.organization_id == organization_id,
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on disk",
        )

    media_types = {
        FileFormat.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        FileFormat.PDF: "application/pdf",
    }

    return FileResponse(
        path=str(file_path),
        media_type=media_types.get(document.file_format, "application/octet-stream"),
        filename=file_path.name,
    )
