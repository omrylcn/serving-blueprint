from calendar import c
import os
from typing import Text
from src.workers.text_embedding_workers import TextEmbeddingWorkerService, EmbeddingTaskConfig, create_celery_app
from src.ml.text_embedding_service import TextEmbeddingService
from src.core.config.main import settings,ml_settings
from src.core.logger import logger

# Get model key from environment variable
model_key = os.getenv('MODEL_KEY', None)
model_type = os.getenv('MODEL_TYPE', None)

if model_key is None:
    raise ValueError("MODEL_KEY environment variable is not set")

if model_type is None:
    raise ValueError("MODEL_TYPE environment variable is not set")

try:
    # Find model config by key
    model_key = int(model_key)
    model_name = settings.ml_models[model_type][model_key]
    ml_config = ml_settings.models[model_name]
    model_version = ml_config.version
    # model_path = model_config.path

    logger.info(f"Initializing worker for model: {model_name} (version: {model_version})")

    # Initialize text embedding service with the model
    text_embedding_service = TextEmbeddingService(ml_config).load()
    
    # Create embedding service
    celery_app = create_celery_app(settings)
    text_embedding_worker = TextEmbeddingWorkerService(celery_app)
    
    # Create worker task
    task = text_embedding_worker.create_worker_task(model_name, text_embedding_service)
    
    # Get the Celery app for the worker
    celery_app = text_embedding_worker.celery_app
    
    # Log queue information
    task_queue = EmbeddingTaskConfig.get_queue_name(model_name)
    logger.info(f"Worker initialized successfully for model: {model_name}")
    logger.info(f"Listening to queue: {task_queue}")
    
except KeyError:
    raise KeyError(f"Model {model_key} not found in ML config")
except Exception as e:
    raise Exception(f"Error initializing text embedding service: {str(e)}")