from pydantic import BaseModel


class ImageProcessingParams(BaseModel):
    model_name: str
    model_mode: int