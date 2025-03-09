from pydantic import BaseModel, Field
from typing import List, Optional, Any


class TaskStatusResponse(BaseModel):
    """
    Response schema for task status.
    """
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Current task status (PENDING, PROCESSING, SUCCESS, FAILURE)")


class TaskResultResponse(BaseModel):
    """
    Response schema for task results.
    """
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Current task status")
    result: Optional[List[List[float]]] = Field(None, description="Embedding vectors if task is completed")
    error: Optional[str] = Field(None, description="Error message if task failed")