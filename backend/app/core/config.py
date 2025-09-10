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
    
    @validator("AZURE_STORAGE_CONNECTION_STRING")
    def validate_azure_connection_string(cls, v):
        """Validar que el connection string de Azure esté presente"""
        if not v:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING es requerido")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()