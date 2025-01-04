from celery import Celery

from ..core.config.main import settings
from celery import Celery, Task
from celery.result import AsyncResult
from typing import Dict, Callable, Union


def create_api_side_task(settings):
    style_transfer_task_lib: Dict[int, Task] = {}
    style_transfer_task_info: Dict[str, int] = {}
    if "style_transfer" in settings.ML_MODEL_TYPES:

        style_transfer_task_info = settings.ML_MODELS["style_transfer"]
        celery_app = Celery("model_tasks", broker=settings.RABBITMQ_URL, backend=settings.REDIS_URL)

        for model_name, model_no in settings.ML_MODELS["style_transfer"].items():
            # Create a closure to capture model_task value
            def create_task(model_name):
                @celery_app.task(name=f"task_{model_name}", queue=f"task_{model_name}_queue")
                def dynamic_task(image_bytes: bytes) -> str:
                    return f"task_{model_name}"

                return dynamic_task

            # Create the task and store in library
            task = create_task(model_name)
            style_transfer_task_lib[model_no] = task

    return style_transfer_task_lib, style_transfer_task_info, celery_app


def create_worker_side_tasks(model_instance: Dict[str, any], settings):
    style_transfer_task_lib: Dict[int, Task] = {}
    style_transfer_task_info: Dict[str, int] = {}
    if "style_transfer" in settings.ML_MODEL_TYPES:

        style_transfer_task_info = settings.ML_MODELS["style_transfer"]
        celery_app = Celery("model_tasks", broker=settings.RABBITMQ_URL, backend=settings.REDIS_URL)

        for model_name, model_no in settings.ML_MODELS["style_transfer"].items():
            # Create a closure to capture model_task value
            def create_task(model_name):
                @celery_app.task(name=f"task_{model_name}", queue=f"task_{model_name}_queue")
                def dynamic_task(model_bytes: bytes) -> str:
                    print(int(model_bytes))
                    return f"task_{model_name}"

                return dynamic_task

            # Create the task and store in library
            task = create_task(model_name)
            style_transfer_task_lib[model_no] = task

    return style_transfer_task_lib, style_transfer_task_info, celery_app


# for one worker and container
def create_worker_task(settings, model_name, model_no, model_instance):
    celery_app = Celery("model_tasks", broker=settings.RABBITMQ_URL, backend=settings.REDIS_URL)

    @celery_app.task(name=f"task_{model_name}", queue=f"task_{model_name}_queue")
    def dynamic_task(image_bytes: bytes) -> str:
        model_instance.process_image(image_bytes)
        return model_instance.process_image(image_bytes)

    return dynamic_task, celery_app


# Optional: Type checking function
def check_task_mode(task_mode: int, task_library: Dict[int, Task]) -> None:
    """
    Validates if the given task mode exists in the task library.

    Parameters
    ----------
    task_mode : int
        The task mode to validate
    task_lib : dict
        Dictionary containing valid task modes as keys

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If task_mode is not found in task_lib
    """
    if task_mode not in task_library:
        raise ValueError(f"Invalid task mode: {task_mode}")


# celery_app = Celery('model_tasks', broker=settings.RABBITMQ_URL, backend=settings.REDIS_URL)

# @celery_app.task(name="task_0")
# def task_0() -> str:
#     return "task_0"

# @celery_app.task(name="task_1")
# def task_1() -> str:
#     return "task_1"

# @celery_app.task(name="task_2")
# def task_2() -> str:
#     return "task_2"

# @celery_app.task(name="task_3")

# def task_3() -> str:
#     return "task_3"


# # Define queues
# celery_app.conf.task_queues = {
#     'task_0_queue': Queue('task_0_queue', routing_key='task_0.#'),
#     'task_1_queue': Queue('task_1_queue', routing_key='task_1.#'),
#     'task_2_queue': Queue('task_2_queue', routing_key='task_2.#'),
#     'task_3_queue': Queue('task_3_queue', routing_key='task_3.#')
# }


# if "style_transfer" in settings.ML_MODEL_TYPES:
# task_lib: Dict[int, Task] = {}
# celery_app = Celery('style_transfer', broker=settings.RABBITMQ_URL, backend=settings.REDIS_URL)

# for model_task in settings.ML_MODEL_TYPES["style_transfer"]:


#     @celery_app.task(name="task_0", queue='task_0_queue')
#     def task() -> str:
#         return f"task_{model_task}"

# @celery_app.task(name="task_1", queue='task_1_queue')
# def task_1() -> str:
#     return "task_1"

# @celery_app.task(name="task_2", queue='task_2_queue')
# def task_2() -> str:
#     return "task_2"

# @celery_app.task(name="task_3", queue='task_3_queue')
# def task_3() -> str:
#     return "task_3"


# if "style_transfer" in settings.ML_MODEL_TYPES:
#         task_lib: Dict[int, Task] = {}
#         celery_app = Celery('model_tasks', broker=settings.RABBITMQ_URL, backend=settings.REDIS_URL)

#         for model_name, model_no in settings.ML_MODELS["style_transfer"].items():
#             # Create a closure to capture model_task value
#             def create_task(model_name):
#                 @celery_app.task(name=f"task_{model_name}",
#                                queue=f"task_{model_name}_queue")
#                 def dynamic_task() -> str:
#                     return f"task_{model_name}"
#                 return dynamic_task

#             # Create the task and store in library
#             task = create_task(model_name)
#             task_lib[model_no] = task

# Type for Celery task
# CeleryTask = Task[Callable[..., str], str]  # Generic Task with input callable and str return type

# # Task library mapping task numbers to Celery tasks
# task_lib: Dict[int, Task] = {
#     0: task_0,
#     1: task_1,
#     2: task_2,
# }

# # Optional: Type checking function
# def check_task_mode(task_mode: int, task_library: Dict[int, Task]) -> None:
#     """
#     Validates if the given task mode exists in the task library.

#     Parameters
#     ----------
#     task_mode : int
#         The task mode to validate
#     task_lib : dict
#         Dictionary containing valid task modes as keys

#     Returns
#     -------
#     None

#     Raises
#     ------
#     ValueError
#         If task_mode is not found in task_lib
#     """
#     if task_mode not in task_library:
#         raise ValueError(f"Invalid task mode: {task_mode}")
