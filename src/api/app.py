from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response, HTMLResponse
from celery.result import AsyncResult

# from src.workers.celery_app import process_image_task
from src.core.config.main import settings
from src.api.route import st_router


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
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
        return Response(content=result.get(), media_type="image/png")
    return {"error": "Task failed"}


# @app.post("/process-image/")
# async def process_image_endpoint(
#     params: ImageProcessingParams,
#     file: UploadFile = File(...),
# ):

#     check_task_mode(params.model_mode, task_lib)
#     result = task_lib[params.model_mode].delay()
#     print(result)
#     # content = await file.read()
#     # task = process_image_task.delay(content, (image_size, image_size))
#     return {params.model_name, params.model_mode}


# @app.post("/process-image/")
# async def process_image_endpoint(
#     params: ImageProcessingParams,
#     file: UploadFile = File(...),

# ):
#     #content = await file.read()
#     #task = process_image_task.delay(content, (image_size, image_size))
#     return {params.model_name, params.model_mode}
