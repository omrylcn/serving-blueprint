from pydantic import BaseModel, Field
from typing import List, Optional


class ModelInfoResponse(BaseModel):
    """
    Schema for embedding model information.
    """
    name: str = Field(..., description="Model identifier")
    model_key: int = Field(..., description="Model key")
    dimension: int = Field(..., description="Embedding vector dimension")
    max_sequence_length: int = Field(..., description="Maximum sequence length")
    description: str = Field(..., description="Model description")
    


class TextEmbeddingRequest(BaseModel):
    """
    Request schema for single text embedding.
    """
    text: str = Field(..., description="Text to be embedded")
    model_key: int = Field(..., description="Key of the embedding model to use")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "This is a sample text to be embedded",
                "model_key": 11
            }
        }


class BatchEmbeddingRequest(BaseModel):
    """
    Request schema for batch text embedding.
    """
    texts: List[str] = Field(..., description="List of texts to be embedded")
    model_name: str = Field(..., description="Name of the embedding model to use")
    
    class Config:
        schema_extra = {
            "example": {
                "texts": [
                    "This is the first sample text to be embedded",
                    "This is the second sample text to be embedded"
                ],
                "model_name": "bert"
            }
        }


class TextEmbeddingResponse(BaseModel):
    """
    Response schema for embedding task creation.
    """
    task_id: str = Field(..., description="ID of the created task")
    model_key : int = Field(..., description="Key of the embedding model used")
    model_name: str = Field(..., description="Name of the embedding model being used")
    status: str = Field(..., description="Current status of the task")


