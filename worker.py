import os
from src.workers.style_transfer_workers import create_worker_task
from src.core.config import settings
from src.ml.style_transfer_service import ImageService


model_name = os.getenv('MODEL_NAME', 'candy')
model_number = int(os.getenv('MODEL_NUMBER', '0'))
model_path = os.getenv('MODEL_PATH', 'models/candy-8.onnx')




style_transfer_service = ImageService(model_path=model_path)
model_instance = {}
worker_task, celery_app = create_worker_task(settings,"candy",0,style_transfer_service)




