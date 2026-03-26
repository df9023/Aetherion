from fastapi import APIRouter

from app.api.v1.endpoints import auth, cases, clients, documents, health, knowledge, recommendations

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
# Documents: generate-document lives under /recommendations/{id}/generate-document,
# download lives under /documents/{id}/download — both on the same router with no prefix
api_router.include_router(documents.router, tags=["documents"])
