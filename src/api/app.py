from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response, HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
from celery.result import AsyncResult

# from src.workers.celery_app import process_image_task
from src.core.config.main import settings
from src.api.route import st_router
from src.monitoring.instrumentator import setup_monitoring


# Create custom metrics
RESULT_COUNTER = Counter(
    name="style_transfer_result_total",
    documentation="Total number of style transfer results",
    labelnames=["status"],
)




app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
setup_monitoring(app)
app.include_router(st_router, prefix="/api/v1", tags=["Style Transfer"])


@app.get("/health")
def get_health():
    return {"status": True}


@app.get("/", response_class=HTMLResponse)
def get_root():
    return """
        <html>
            <head>
                <title>Image Processing</title>
            </head>
            <body>
                <h1>Image Processing API</h1>
                <p>Send POST request to /process-image/ with an image file to process it.</p>
            </body>
        </html>
    """


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Check the status of a processing task"""
    result = AsyncResult(task_id)
    if result.ready():
        if result.successful():
            return {"status": "completed"}
        else:
            return {"status": "failed", "error": str(result.result)}
    return {"status": "processing"}


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """Get the processed image for a completed task"""
    result = AsyncResult(task_id)
    if not result.ready():
        return {"error": "Task still processing"}

    if result.successful():
        RESULT_COUNTER.labels("success").inc()
        return Response(content=result.get(), media_type="image/png")
    
    RESULT_COUNTER.labels("failed").inc()
    return {"error": "Task failed"}

