from fastapi import APIRouter
from app.api.api_v1.endpoints import papers, research, analytics

api_router = APIRouter()

api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])