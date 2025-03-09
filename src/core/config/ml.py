from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union,Tuple
from enum import Enum
import yaml
from functools import lru_cache


class ModelFramework(str, Enum):
    ONNX = "onnx"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"


class ModelConfig(BaseModel):
    name: str
    version: str
    framework: ModelFramework
    path: str
    model_id: str = Field(default="")
    description: Optional[str] = Field(default="")
    params: Dict[str, Union[str, int, float, bool,Tuple,List]] = Field(default_factory=dict)
    # input_shape: List[int]
    # input_type: str = Field(default="float32")
    # device: str = Field(default="cpu")
    # batch_size: int = Field(default=1)
    # options: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)
    # preprocessing: Optional[Dict[str, Dict]] = Field(default_factory=dict)
    # postprocessing: Optional[Dict[str, Dict]] = Field(default_factory=dict)

class MLSettings(BaseModel):

    models: dict[str, ModelConfig]
#    cache_ttl: int = Field(default=3600)
#    max_batch_size: int = Field(default=32)
#    allowed_formats: List[str] = Field(default=["jpg", "png", "jpeg"])

    class Config:
        extra = "allow"
