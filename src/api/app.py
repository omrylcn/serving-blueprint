from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config.main import configs
from src.api.router import api_router
from src.monitoring.instrumentator import setup_monitoring


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=configs.PROJECT_NAME,
        description="API for text embedding using various models",
        version=configs.PROJECT_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup monitoring
    setup_monitoring(app)
    
    # Include API router
    app.include_router(api_router)
    

    @app.get("/")
    async def root():
        return {"message": "ML  API"}
    
    return app


# Create the application instance
app = create_application()


# For debugging purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)