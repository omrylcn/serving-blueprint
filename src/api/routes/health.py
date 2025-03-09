from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse

from src.core.config.main import configs

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Simple health check endpoint to verify the API is running.
    """
    return {
        "status": True,
        "service": configs.PROJECT_NAME,
        "version": configs.PROJECT_VERSION,
        
    }


 