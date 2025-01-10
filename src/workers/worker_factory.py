import os
from src.workers.style_transfer_workers import create_worker_task
from src.core.config import settings
from src.ml.style_transfer_service import ImageService
from src.core.logging import logger


model_key = os.getenv('MODEL_KEY', None)

if model_key is None:
    raise ValueError("model key environment variable is not set")

try:
    model_config = settings.ml_settings.models[model_key]
    model_name = model_config.name
    model_version = model_config.version
    model_number = model_config.model_id
    model_path = model_config.path

except KeyError:
    raise KeyError(f"Model {model_key} not found in ML config")
except Exception as e:
    raise Exception(f"Error loading ML config: {str(e)}")

try:
    style_transfer_service = ImageService(model_path=model_path)
    worker_task, celery_app = create_worker_task(settings, model_name, style_transfer_service)
    logger.info("Worker task and Celery app initialized successfully.")
except Exception as e:
    raise Exception(f"Error initializing services: {str(e)}")
