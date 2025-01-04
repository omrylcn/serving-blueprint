from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource
from pydantic import Field
from typing import Tuple, Type,List,Dict
import yaml
from functools import lru_cache

from src.core.config.ml import MLSettings

CONFIG_YAML_PATH = "config/config.yaml"




MODEL_TYPES = ["style_transfer"]

STYLE_TRANSFER_MODELS = ["candy", "mosaic", "rain_princess", "udnie"]


class Settings(BaseSettings):
    # API Configuration
    API_PORT: int = Field(default=8000)
    API_HOST: str = Field(default="0.0.0.0")
    PROJECT_NAME: str = Field(default="ML API")
    PROJECT_VERSION: str = Field(default="0.0.0")

    # Model Configuration
    ML_CONFIG_PATH: str = Field(default="config/ml_config.yaml")
    ML_MODEL_TYPES: List[str] = Field(default=MODEL_TYPES)
    ML_MODELS: Dict[str, Dict[str, int]] = Field(default={})
    
    RABBITMQ_USER: str = Field(default="guest")
    RABBITMQ_PASSWORD: str = Field(default="guest")
    RABBITMQ_HOST: str = Field(default="rabbitmq")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_MANAGEMENT_PORT: int = Field(default=15672)

    # Redis Configuration
    REDIS_HOST: str = Field(default="redis")
    REDIS_PASSWORD: str = Field(default="")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    # Logger Configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOGGER_HANDLER: str = Field(default="file")
    LOG_DIR: str = Field(default="logs")

    # MinIO Configuration
    MINIO_ENDPOINT: str = Field(default="localhost")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")

    # MongoDB Configuration
    MONGODB_PORT: int = Field(default=27017)
    MONGODB_ROOT_USERNAME: str = Field(default="root")
    MONGODB_ROOT_PASSWORD: str = Field(default="root")
    MONGODB_HOST: str = Field(default="localhost")
    MONGODB_URL: str = Field(default="mongodb://root:example@localhost:27017")

    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def ml_settings(self) -> MLSettings:
        return load_ml_settings(self.ML_CONFIG_PATH)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # extra="allow",
        yaml_file=CONFIG_YAML_PATH,
        case_sensitive=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            init_settings,
            file_secret_settings,
        )

@lru_cache()
def load_ml_settings(config_path: str) -> MLSettings:
    """Load ML settings from yaml with caching"""
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return MLSettings(**config_data)
    except Exception as e:
        raise ValueError(f"Error loading ML config from {config_path}: {str(e)}")


settings = Settings()  # Explanation of configuration priority (highest to lowest):
# 1. Environment variables
# 2. .env file
# 3. YAML config file
# 4. Initialization values
# 5. File secrets
# 6. Default values in Field() (if no other source provides a value)
