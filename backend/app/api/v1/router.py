from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    cases,
    client_organizations,
    clients,
    dashboard,
    documents,
    firm_insights,
    health,
    knowledge,
    recommendations,
)

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(
    client_organizations.router,
    prefix="/client-organizations",
    tags=["client-organizations"],
)
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(
    firm_insights.router, prefix="/firm-insights", tags=["firm-insights"]
)
api_router.include_router(dashboard.router, tags=["dashboard"])
# Documents: generate-document lives under /recommendations/{id}/generate-document,
# download lives under /documents/{id}/download — both on the same router with no prefix
api_router.include_router(documents.router, tags=["documents"])
