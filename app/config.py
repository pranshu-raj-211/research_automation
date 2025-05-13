import logging
from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl


# TODO: improve
class Settings(BaseSettings):
    PROJECT_NAME: str = "RA"
    DEBUG: bool = Field(default=False)

    MONGO_DB_URL: str = Field(...)
    MONGO_DB_NAME: str = Field(...)

    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    ELASTICSEARCH_URL: AnyHttpUrl = Field(...)
    ES_INDEX_NAME: str = Field("text_chunks")

    OLLAMA_BASE_URL: AnyHttpUrl = Field(...)
    OLLAMA_EMBEDDING_MODEL: str = Field(...)
    OLLAMA_LLM_MODEL: str = Field(...)

    # JWT
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field("HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30)

    MAX_DOCS_PER_TOPIC: int = Field(10)
    MAX_DOC_SIZE_MB: int =Field(10)

    # BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

logger = logging.Logger("RA")

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s"
)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename="logs/app.log", mode="w")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
