from typing import List

from pydantic import RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración básica de la aplicación
    """

    # Configuración básica de la aplicación
    APP_NAME: str = "File Manager API"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Configuración de CORS para React frontend
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",
        "http://frontend:3000",  # Docker container name
    ]

    REDIS_OM_URL: RedisDsn

    # Azure Blob Storage configuración
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_ACCOUNT_NAME: str = ""
    AZURE_CONTAINER_NAME: str = "files"

    # Qdrant Vector DB configuración
    QDRANT_URL: str
    QDRANT_API_KEY: str
    VECTOR_DB_TYPE: str = "qdrant"  # Para futuro: soportar otros tipos

    # Azure OpenAI configuración
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    AZURE_OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-large"

    # Google Cloud / Vertex AI configuración
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # LandingAI configuración
    LANDINGAI_API_KEY: str
    LANDINGAI_ENVIRONMENT: str = "production"  # "production" o "eu"

    # Schemas storage
    SCHEMAS_DIR: str = "./data/schemas"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings.model_validate({})
