"""
Vector Database Module

Este módulo proporciona una abstracción para trabajar con bases de datos vectoriales.
Utiliza el patrón Repository para permitir cambiar fácilmente entre diferentes
implementaciones (Qdrant, Pinecone, Weaviate, etc.).
"""

from .base import VectorDBBase
from .factory import get_vector_db

__all__ = ["VectorDBBase", "get_vector_db"]
