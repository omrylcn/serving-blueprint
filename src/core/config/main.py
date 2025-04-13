from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource
from pydantic import Field
from typing import Tuple, Type, List, Dict
import yaml
from functools import lru_cache

from src.core.config.ml import MLSettings

CONFIG_YAML_PATH = "config/config.yaml"

MODEL_TYPES = ["text_embedding"]
# STYLE_TRANSFER_MODELS = ["candy", "mosaic", "rain_princess", "udnie"]

class APPSettings(BaseSettings):
    project_name: str = Field(default="ML API")
    project_version: str = Field(default="0.0.0")

    # API Configuration<
    api_port: int = Field(default=8000)
    api_host: str = Field(default="0.0.0.0")

    # Model Configuration
    ml_config_path: str = Field(default="config/ml_config.yaml")
    ml_model_types: List[str] = Field(default=MODEL_TYPES)
    ml_models: Dict[str, Dict[int, str]] = Field(default={})

    rabbitmq_user: str = Field(default="guest")
    rabbitmq_password: str = Field(default="guest")
    rabbitmq_host: str = Field(default="rabbitmq")
    rabbitmq_port: int = Field(default=5672)
    rabbitmq_management_port: int = Field(default=15672)

    # Redis Configuration
    redis_host: str = Field(default="redis")
    redis_password: str = Field(default="")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)

    # Flower
    flower_port: int = Field(default=5555)
    flower_user: str = Field(default="guest")
    flower_password: str = Field(default="guest")

    # Logger Configuration
    log_level: str = Field(default="INFO")
    logger_handler: str = Field(default="file")
    log_dir: str = Field(default="logs")
    logger_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    sensitive_fields: List[str] = Field(
        default=["password", "key", "token", "secret"],
        description="Fields to redact in logs"
    )


    # # MinIO Configuration
    # minio_endpoint: str = Field(default="localhost")
    # minio_access_key: str = Field(default="minioadmin")
    # minio_secret_key: str = Field(default="minioadmin")

    # Elasticsearch Configuration
    elasticsearch_host: str = Field(default="elasticsearch")
    elasticsearch_port: int = Field(default=9200)
    elasticsearch_user: str = Field(default="elastic")
    elasticsearch_password: str = Field(default="changeme")
    elasticsearch_verify_certs: bool = Field(default=False)
    timeout: int = Field(default=30, description="Timeout for Elasticsearch operations")
    batch_size: int = Field(default=100,description="Batch size for bulk operations") 


    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}//"

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"    # @property
    # def ml_settings(self) -> MLSettings:
    #     return load_ml_co(self.ML_CONFIG_PATH)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # extra="allow",
        yaml_file=CONFIG_YAML_PATH,
        case_sensitive=False,
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
    """Load ML configs from yaml with caching"""
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        return MLSettings(**config_data)
    except Exception as e:
        raise ValueError(f"Error loading ML config from {config_path}: {str(e)}")


settings = APPSettings()  # Explanation of configuration priority (highest to lowest):
ml_settings = load_ml_settings(settings.ml_config_path)

# 1. Environment variables
# 2. .env file
# 3. YAML config file
# 4. Initialization values
# 5. File secrets
# 6. Default values in Field() (if no other source provides a value)
