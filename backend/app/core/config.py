import os
from typing import List
from pydantic import validator
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
        "http://frontend:3000",   # Docker container name
    ]
    
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

    @validator("AZURE_STORAGE_CONNECTION_STRING")
    def validate_azure_connection_string(cls, v):
        """Validar que el connection string de Azure esté presente"""
        if not v:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING es requerido")
        return v

    @validator("QDRANT_URL")
    def validate_qdrant_url(cls, v):
        """Validar que la URL de Qdrant esté presente"""
        if not v:
            raise ValueError("QDRANT_URL es requerido")
        return v

    @validator("QDRANT_API_KEY")
    def validate_qdrant_api_key(cls, v):
        """Validar que la API key de Qdrant esté presente"""
        if not v:
            raise ValueError("QDRANT_API_KEY es requerido")
        return v

    @validator("AZURE_OPENAI_ENDPOINT")
    def validate_azure_openai_endpoint(cls, v):
        """Validar que el endpoint de Azure OpenAI esté presente"""
        if not v:
            raise ValueError("AZURE_OPENAI_ENDPOINT es requerido")
        return v

    @validator("AZURE_OPENAI_API_KEY")
    def validate_azure_openai_api_key(cls, v):
        """Validar que la API key de Azure OpenAI esté presente"""
        if not v:
            raise ValueError("AZURE_OPENAI_API_KEY es requerido")
        return v

    @validator("GOOGLE_APPLICATION_CREDENTIALS")
    def validate_google_credentials(cls, v):
        """Validar que el path de credenciales de Google esté presente"""
        if not v:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS es requerido")
        return v

    @validator("GOOGLE_CLOUD_PROJECT")
    def validate_google_project(cls, v):
        """Validar que el proyecto de Google Cloud esté presente"""
        if not v:
            raise ValueError("GOOGLE_CLOUD_PROJECT es requerido")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()