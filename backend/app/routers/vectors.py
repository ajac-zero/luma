"""
Router para endpoints de operaciones con bases de datos vectoriales.

Este módulo define todos los endpoints de la API relacionados con
la gestión de colecciones y chunks en bases de datos vectoriales.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.services.vector_service import vector_service
from app.models.vector_models import (
    CollectionExistsRequest,
    CollectionExistsResponse,
    CollectionCreateRequest,
    CollectionCreateResponse,
    CollectionDeleteResponse,
    CollectionInfoResponse,
    FileExistsInCollectionRequest,
    FileExistsInCollectionResponse,
    GetChunksByFileRequest,
    GetChunksByFileResponse,
    DeleteFileFromCollectionRequest,
    DeleteFileFromCollectionResponse,
    AddChunksRequest,
    AddChunksResponse,
    VectorDBHealthResponse,
    VectorDBErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/vectors",
    tags=["Vectors"],
    responses={
        500: {"model": VectorDBErrorResponse, "description": "Error interno del servidor"}
    }
)


# ============================================================================
# Endpoints de Health Check
# ============================================================================

@router.get(
    "/health",
    response_model=VectorDBHealthResponse,
    summary="Verificar estado de la base de datos vectorial",
    description="Verifica que la conexión con la base de datos vectorial esté funcionando correctamente"
)
async def health_check():
    """Health check de la base de datos vectorial."""
    try:
        return await vector_service.health_check()
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar estado de la base de datos: {str(e)}"
        )


# ============================================================================
# Endpoints de Colecciones
# ============================================================================

@router.post(
    "/collections/exists",
    response_model=CollectionExistsResponse,
    summary="Verificar si una colección existe",
    description="Verifica si existe una colección con el nombre especificado"
)
async def check_collection_exists(request: CollectionExistsRequest):
    """Verifica si una colección existe."""
    try:
        return await vector_service.check_collection_exists(request.collection_name)
    except Exception as e:
        logger.error(f"Error al verificar colección: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar colección: {str(e)}"
        )


@router.post(
    "/collections/create",
    response_model=CollectionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva colección",
    description="Crea una nueva colección en la base de datos vectorial"
)
async def create_collection(request: CollectionCreateRequest):
    """Crea una nueva colección."""
    try:
        return await vector_service.create_collection(request)
    except ValueError as e:
        logger.warning(f"Error de validación al crear colección: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al crear colección: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear colección: {str(e)}"
        )


@router.delete(
    "/collections/{collection_name}",
    response_model=CollectionDeleteResponse,
    summary="Eliminar una colección",
    description="Elimina completamente una colección y todos sus datos"
)
async def delete_collection(collection_name: str):
    """Elimina una colección completa."""
    try:
        return await vector_service.delete_collection(collection_name)
    except ValueError as e:
        logger.warning(f"Error de validación al eliminar colección: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al eliminar colección: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar colección: {str(e)}"
        )


@router.get(
    "/collections/{collection_name}/info",
    response_model=CollectionInfoResponse,
    summary="Obtener información de una colección",
    description="Obtiene información detallada sobre una colección"
)
async def get_collection_info(collection_name: str):
    """Obtiene información de una colección."""
    try:
        info = await vector_service.get_collection_info(collection_name)

        if info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Colección '{collection_name}' no encontrada"
            )

        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener info de colección: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de colección: {str(e)}"
        )


# ============================================================================
# Endpoints de Archivos en Colecciones
# ============================================================================

@router.post(
    "/files/exists",
    response_model=FileExistsInCollectionResponse,
    summary="Verificar si un archivo existe en una colección",
    description="Verifica si un archivo específico existe en una colección"
)
async def check_file_exists_in_collection(request: FileExistsInCollectionRequest):
    """Verifica si un archivo existe en una colección."""
    try:
        return await vector_service.check_file_exists_in_collection(
            request.collection_name,
            request.file_name
        )
    except Exception as e:
        logger.error(f"Error al verificar archivo en colección: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar archivo: {str(e)}"
        )


@router.get(
    "/collections/{collection_name}/files/{file_name}/chunks",
    response_model=GetChunksByFileResponse,
    summary="Obtener chunks de un archivo",
    description="Obtiene todos los chunks de un archivo específico en una colección"
)
async def get_chunks_by_file(
    collection_name: str,
    file_name: str,
    limit: Optional[int] = Query(None, description="Límite de chunks a retornar")
):
    """Obtiene todos los chunks de un archivo."""
    try:
        return await vector_service.get_chunks_by_file(
            collection_name,
            file_name,
            limit
        )
    except ValueError as e:
        logger.warning(f"Error de validación al obtener chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al obtener chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener chunks: {str(e)}"
        )


@router.delete(
    "/collections/{collection_name}/files/{file_name}",
    response_model=DeleteFileFromCollectionResponse,
    summary="Eliminar un archivo de una colección",
    description="Elimina todos los chunks de un archivo de una colección"
)
async def delete_file_from_collection(collection_name: str, file_name: str):
    """Elimina todos los chunks de un archivo."""
    try:
        return await vector_service.delete_file_from_collection(
            collection_name,
            file_name
        )
    except ValueError as e:
        logger.warning(f"Error de validación al eliminar archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al eliminar archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar archivo: {str(e)}"
        )


# ============================================================================
# Endpoints de Chunks
# ============================================================================

@router.post(
    "/chunks/add",
    response_model=AddChunksResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar chunks a una colección",
    description="Agrega múltiples chunks a una colección existente"
)
async def add_chunks(request: AddChunksRequest):
    """Agrega chunks a una colección."""
    try:
        return await vector_service.add_chunks(
            request.collection_name,
            request.chunks
        )
    except ValueError as e:
        logger.warning(f"Error de validación al agregar chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al agregar chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar chunks: {str(e)}"
        )
