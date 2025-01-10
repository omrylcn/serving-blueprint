from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

def setup_monitoring(app: FastAPI) -> None:
    """Configure Prometheus monitoring for the FastAPI application"""
    
    Instrumentator().instrument(app).expose(app)