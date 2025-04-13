from prometheus_fastapi_instrumentator import Instrumentator,metrics
from fastapi import FastAPI

def setup_monitoring(app: FastAPI) -> None:
    """Configure Prometheus monitoring for the FastAPI application"""
    instrumentator = Instrumentator()
    instrumentator.add(metrics.default())
    instrumentator.instrument(app).expose(app)