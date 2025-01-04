from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from fastapi import FastAPI, File, UploadFile

from src.core.config.main import settings
from src.workers.style_transfer_workers import create_api_side_task,check_task_mode

from pydantic import BaseModel


class StyleTransferResponse(BaseModel):
    result_id: str
    model_name: str
    model_mode: int
    status: str


class StyleTransferRequest(BaseModel):
    model_name: str
    model_mode: int

style_transfer_task_lib, style_transfer_task_info,style_transfer_celery_app = create_api_side_task(settings)

st_router = APIRouter(prefix="/style_transfer")


@st_router.get("/models")
def get_style_transfer_models():

    return {"models": settings.ML_MODELS}


@st_router.post("", response_model=StyleTransferResponse)
async def do_style_transfer(
    model_name: str = Query(..., description="Name of the style transfer model"),
    model_mode: int = Query(..., description="Mode number for the model"),
    file: UploadFile = File(...),
):

    try:
        content = await file.read()
        check_task_mode(model_mode, style_transfer_task_lib)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        result = style_transfer_task_lib[model_mode].delay(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = StyleTransferResponse(
        result_id=result.id, model_name=model_name, model_mode=model_mode, status=result.status
    )
    print(result.id, result.status)

    return response


@st_router.get("/mode")
def get_style_transfer_mode(params: StyleTransferRequest):
    return {"models": settings.ML_MODELS}
