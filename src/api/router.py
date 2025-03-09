from fastapi import APIRouter

from src.api.routes.text_embedding import router as embedding_router
from src.api.routes.health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(embedding_router, prefix="/embedding", tags=["Text Embedding"])