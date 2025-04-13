from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from light_embed.utils import model

from src import ml
from src.core.config import ml_settings,settings

from src.api.schemas.embedding import (
    TextEmbeddingRequest,
    TextEmbeddingResponse,
    ModelInfoResponse,
    #BatchEmbeddingRequest,
    #TaskResultResponse
)

from src.workers.text_embedding_workers import TextEmbeddingWorkerService,create_celery_app

router = APIRouter()

# Dependency to get embedding service
def get_embedding_worker_service(settings)->TextEmbeddingWorkerService:
    celery_app = create_celery_app(settings)
    return TextEmbeddingWorkerService(celery_app)

text_embedding_worker_service = get_embedding_worker_service(settings)

@router.get("/models") #, response_model=List[ModelInfoResponse])
async def get_available_models():
    """
    Get a list of all available embedding models and their details.
    """
    models = []

    for key,model_name in settings.ML_MODELS['text_embedding'].items():
        ml_cfg = ml_settings.models[model_name]
        models.append(
            ModelInfoResponse(
                 name=ml_cfg.name,
                 model_key=key,
                 dimension=ml_cfg.params.get('embedding_dim', -1),
                 max_sequence_length=ml_cfg.params.get('max_seq_length', -1),
                 description=ml_cfg.description
            ))

    return models


@router.post("/", response_model=TextEmbeddingResponse)
async def create_embedding(
    request: TextEmbeddingRequest,
    #embedding_service: TextEmbeddingWorkerService = Depends(get_embedding_service)
):
    """
    Create embeddings for a single text using the specified model.
    """
    # Validate model name
    if request.model_key not in settings.ML_MODELS['text_embedding'].keys():
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model_key}' not available. Use one of: {settings.ML_MODELS['text_embedding']}"
        )
    
    # Send text to embedding task
    model_name = settings.ML_MODELS['text_embedding'][request.model_key]
    model_key = request.model_key

    print(settings.model_dump())
    try:
        result = text_embedding_worker_service.send_as_task(
            texts=[request.text],
            model_name=model_name
        )
        
        return TextEmbeddingResponse(
            task_id=result["task_id"],
            model_key=model_key,
            model_name=model_name,
            status=result["status"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}")
async def get_task_result(
    task_id: str
):
    """
    Get the result of a text embedding task.
    """
    try:
        result = text_embedding_worker_service.get_task_result(task_id)
        print(type(result))
        print(result.keys())
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task result: {str(e)}")


