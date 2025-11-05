"""
Factory para crear instancias de bases de datos vectoriales.

Este módulo implementa el patrón Factory para crear la instancia correcta
de base de datos vectorial según la configuración.
"""

import logging
from typing import Optional

from app.core.config import settings
from .base import VectorDBBase
from .qdrant_client import QdrantVectorDB

logger = logging.getLogger(__name__)

# Instancia global singleton
_vector_db_instance: Optional[VectorDBBase] = None


def get_vector_db() -> VectorDBBase:
    """
    Factory function que retorna la instancia de base de datos vectorial configurada.

    Utiliza un patrón Singleton para mantener una sola instancia durante
    el ciclo de vida de la aplicación.

    Returns:
        VectorDBBase: Instancia de la base de datos vectorial configurada

    Raises:
        ValueError: Si el tipo de base de datos no está soportado
    """
    global _vector_db_instance

    # Si ya existe una instancia, retornarla
    if _vector_db_instance is not None:
        return _vector_db_instance

    # Crear nueva instancia según configuración
    db_type = settings.VECTOR_DB_TYPE.lower()

    if db_type == "qdrant":
        logger.info(f"Inicializando Qdrant con URL: {settings.QDRANT_URL}")
        _vector_db_instance = QdrantVectorDB(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

    # Aquí se pueden agregar otros proveedores en el futuro
    # elif db_type == "pinecone":
    #     _vector_db_instance = PineconeVectorDB(...)
    # elif db_type == "weaviate":
    #     _vector_db_instance = WeaviateVectorDB(...)

    else:
        raise ValueError(
            f"Tipo de base de datos vectorial no soportado: {db_type}. "
            f"Tipos soportados: qdrant"
        )

    logger.info(f"Base de datos vectorial '{db_type}' inicializada exitosamente")
    return _vector_db_instance


def reset_vector_db() -> None:
    """
    Resetea la instancia global de la base de datos vectorial.

    NOTA: Esta función solo cierra la conexión del cliente en memoria.
    NO elimina ni modifica datos en Qdrant.
    Útil principalmente para testing.
    """
    global _vector_db_instance
    _vector_db_instance = None
    logger.info("Instancia de base de datos vectorial reseteada")
