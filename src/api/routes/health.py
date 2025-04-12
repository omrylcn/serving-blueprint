from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse

from src.core.config.main import settings

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Simple health check endpoint to verify the API is running.
    """
    return {
        "status": True,
        "service": settings.project_name,
        "version": settings.project_version,
        
    }


 