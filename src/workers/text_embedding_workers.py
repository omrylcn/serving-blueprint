from typing import Callable,Dict,Optional
from celery import Celery
from src.ml.text_embedding_service import TextEmbeddingService
from src.core.config import APPSettings,settings


#from config import EmbeddingTaskConfig
from typing import List, Dict, Any
from src.core.logger import logger


class EmbeddingTaskConfig:
    @staticmethod
    def get_task_name(model_name: str) -> str:
        return f"text_embedding_{model_name}"
    
    @staticmethod
    def get_queue_name(model_name: str) -> str:
        return f"text_embedding_{model_name}_queue"

def create_celery_app(settings:APPSettings=settings) -> Celery:
    return Celery('embedding_tasks',broker=settings.rabbitmq_url, backend=settings.redis_url)   
    

# def get_embedding_task_config(settings:APPsettings) -> EmbeddingTaskConfig:
#     return EmbeddingTaskConfig(settings)


class TextEmbeddingWorkerService:
    """
    Service class that can be used for text embedding operations on both API and worker sides.
    
    This class manages text embedding tasks, sends tasks to Celery workers on the API side,
    and defines tasks that will perform the actual embedding operations on the worker side.
    
    Parameters
    ----------
    celery_app : Celery, optional
        Celery application. If None, a new application is created.
    
    Attributes
    ----------
    celery_app : Celery
        Celery application used to manage tasks.
    """
    
    def __init__(self, celery_app: Optional[Celery]= None):
        """
        Initializes the EmbeddingService class.
        
        Parameters
        ----------
        celery_app : Celery, optional
            Celery application. If None, a new application is created.
        """
        self.celery_app = celery_app if celery_app is not None else create_celery_app()    
        
    def send_as_task(self, texts: List[str], model_name: str) -> Dict[str, Any]:
        """
        Sends texts to a worker for embedding processing.
        
        Parameters
        ----------
        texts : List[str]
            List of texts to be processed.
        model_name : str
            Name of the embedding model to be used.
            
        Returns
        -------
        Dict[str, Any]
            Dictionary containing task ID and status information.
            
        Examples
        --------
        >>> service = EmbeddingService()
        >>> result = service.send_text_to_task(["Hello, world!"], "bert")
        >>> print(result)
        {'task_id': '8f1c9e7b-6f3a-4c12-8142-3ac6d8d681a5', 'status': 'PENDING', 'model': 'bert'}
        """
        # Get task and queue names
        task_name = EmbeddingTaskConfig.get_task_name(model_name)
        queue_name = EmbeddingTaskConfig.get_queue_name(model_name)
        
        # Send the task
        result = self.celery_app.send_task(
            task_name,
            args=[texts],
            queue=queue_name
        )
        
        return {
            "task_id": result.id,
            "status": "PENDING",
            "model": model_name
        }
        
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Checks the task result.
        
        Parameters
        ----------
        task_id : str
            Task ID to be checked.
            
        Returns
        -------
        Dict[str, Any]
            Dictionary containing task status and result information if available.
            
        Notes
        -----
        The dictionary contains the following keys:
        - task_id: Task identifier
        - status: Task status ('PENDING', 'PROCESSING', 'SUCCESS', 'FAILURE')
        - result: (If successful) Task result
        - error: (If failed) Error message
        
        Examples
        --------
        >>> service = EmbeddingService()
        >>> result = service.get_task_result('8f1c9e7b-6f3a-4c12-8142-3ac6d8d681a5')
        >>> print(result)
        {'task_id': '8f1c9e7b-6f3a-4c12-8142-3ac6d8d681a5', 'status': 'SUCCESS', 'result': [...]}
        """
        result = self.celery_app.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": result.status
        }
        
        if result.ready():
            # Add the result if the task is completed
            if result.successful():
                response["result"] = result.get()
            else:
                # In case of error
                response["error"] = str(result.result)
        
        return response
    
    def create_worker_task(self, model_name: str, model_service: TextEmbeddingService) -> Callable:
        """
        Creates an embedding task that will run on the worker side.
        
        Parameters
        ----------
        model_name : str
            Name of the embedding model.
        model_service : TextEmbeddingService
            Service that will perform the embedding process.
            
        Returns
        -------
        Callable
            Created Celery task function.
            
        Notes
        -----
        This method should be called during worker initialization. Even if the return value is not used,
        the task is registered to Celery thanks to the decorator.
        
        Examples
        --------
        >>> service = EmbeddingService()
        >>> model_service = TextEmbeddingService("bert")
        >>> task = service.create_worker_task("bert", model_service)
        """
        task_name = EmbeddingTaskConfig.get_task_name(model_name)
        queue_name = EmbeddingTaskConfig.get_queue_name(model_name)
        #celery_app = create_celery_app()
        
        @self.celery_app.task(name=task_name, 
                    queue=queue_name,
                    bind=True,
                    serializer='json')
        def embedding_task(self, texts):
            """
            Task that performs the text embedding process.
            
            Parameters
            ----------
            texts : List[str]
                List of texts to be processed.
                
            Returns
            -------
            List[List[float]]
                List of generated embedding vectors.
            """
            logger.info(f"Processing {len(texts)} texts with model {model_name}")
            
            self.update_state(state='PROCESSING')
            embeddings = model_service.predict(texts)
            result = embeddings.tolist()
            logger.info(f"Successfully processed {len(texts)} texts with model {model_name}")
            
            return result
            
        return embedding_task