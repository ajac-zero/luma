"""
Modelos Pydantic para operaciones con bases de datos vectoriales.

Este módulo define todos los modelos de datos para requests y responses
relacionados con la gestión de colecciones y chunks en bases de datos vectoriales.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


# ============================================================================
# Modelos para Colecciones
# ============================================================================

class CollectionExistsRequest(BaseModel):
    """Request para verificar si una colección existe."""
    collection_name: str = Field(..., description="Nombre de la colección a verificar")


class CollectionExistsResponse(BaseModel):
    """Response de verificación de existencia de colección."""
    exists: bool = Field(..., description="True si la colección existe")
    collection_name: str = Field(..., description="Nombre de la colección")


class CollectionCreateRequest(BaseModel):
    """Request para crear una nueva colección."""
    collection_name: str = Field(..., description="Nombre de la colección a crear")
    vector_size: int = Field(default=3072, description="Dimensión de los vectores")
    distance: str = Field(default="Cosine", description="Métrica de distancia")

    @validator("distance")
    def validate_distance(cls, v):
        """Valida que la métrica de distancia sea válida."""
        allowed = ["Cosine", "Euclid", "Dot"]
        if v not in allowed:
            raise ValueError(f"Métrica de distancia debe ser una de: {allowed}")
        return v

    @validator("vector_size")
    def validate_vector_size(cls, v):
        """Valida que el tamaño del vector sea positivo."""
        if v <= 0:
            raise ValueError("El tamaño del vector debe ser mayor a 0")
        return v


class CollectionCreateResponse(BaseModel):
    """Response de creación de colección."""
    success: bool = Field(..., description="True si se creó exitosamente")
    collection_name: str = Field(..., description="Nombre de la colección creada")
    message: str = Field(..., description="Mensaje descriptivo")


class CollectionDeleteResponse(BaseModel):
    """Response de eliminación de colección."""
    success: bool = Field(..., description="True si se eliminó exitosamente")
    collection_name: str = Field(..., description="Nombre de la colección eliminada")
    message: str = Field(..., description="Mensaje descriptivo")


class CollectionInfoResponse(BaseModel):
    """Response con información de una colección."""
    name: str = Field(..., description="Nombre de la colección")
    vectors_count: int = Field(..., description="Número total de vectores")
    vectors_config: Dict[str, Any] = Field(..., description="Configuración de vectores")
    status: str = Field(..., description="Estado de la colección")


# ============================================================================
# Modelos para Archivos en Colecciones
# ============================================================================

class FileExistsInCollectionRequest(BaseModel):
    """Request para verificar si un archivo existe en una colección."""
    collection_name: str = Field(..., description="Nombre de la colección")
    file_name: str = Field(..., description="Nombre del archivo a verificar")


class FileExistsInCollectionResponse(BaseModel):
    """Response de verificación de existencia de archivo."""
    exists: bool = Field(..., description="True si el archivo existe")
    collection_name: str = Field(..., description="Nombre de la colección")
    file_name: str = Field(..., description="Nombre del archivo")
    chunk_count: Optional[int] = Field(None, description="Número de chunks del archivo si existe")


# ============================================================================
# Modelos para Chunks
# ============================================================================

class ChunkMetadata(BaseModel):
    """Metadata de un chunk."""
    file_name: str = Field(..., description="Nombre del archivo")
    page: int = Field(..., description="Número de página")
    text: Optional[str] = Field(None, description="Texto del chunk")
    # Se pueden agregar más campos según necesidad


class ChunkData(BaseModel):
    """Datos completos de un chunk."""
    id: str = Field(..., description="ID único del chunk")
    payload: ChunkMetadata = Field(..., description="Metadata del chunk")
    vector: Optional[List[float]] = Field(None, description="Vector de embeddings")


class GetChunksByFileRequest(BaseModel):
    """Request para obtener chunks de un archivo."""
    collection_name: str = Field(..., description="Nombre de la colección")
    file_name: str = Field(..., description="Nombre del archivo")
    limit: Optional[int] = Field(None, description="Límite de chunks a retornar")

    @validator("limit")
    def validate_limit(cls, v):
        """Valida que el límite sea positivo si está presente."""
        if v is not None and v <= 0:
            raise ValueError("El límite debe ser mayor a 0")
        return v


class GetChunksByFileResponse(BaseModel):
    """Response con los chunks de un archivo."""
    collection_name: str = Field(..., description="Nombre de la colección")
    file_name: str = Field(..., description="Nombre del archivo")
    chunks: List[Dict[str, Any]] = Field(..., description="Lista de chunks")
    total_chunks: int = Field(..., description="Número total de chunks")


class DeleteFileFromCollectionRequest(BaseModel):
    """Request para eliminar un archivo de una colección."""
    collection_name: str = Field(..., description="Nombre de la colección")
    file_name: str = Field(..., description="Nombre del archivo a eliminar")


class DeleteFileFromCollectionResponse(BaseModel):
    """Response de eliminación de archivo."""
    success: bool = Field(..., description="True si se eliminó exitosamente")
    collection_name: str = Field(..., description="Nombre de la colección")
    file_name: str = Field(..., description="Nombre del archivo eliminado")
    chunks_deleted: int = Field(..., description="Número de chunks eliminados")
    message: str = Field(..., description="Mensaje descriptivo")


class AddChunksRequest(BaseModel):
    """Request para agregar chunks a una colección."""
    collection_name: str = Field(..., description="Nombre de la colección")
    chunks: List[Dict[str, Any]] = Field(..., description="Lista de chunks a agregar")

    @validator("chunks")
    def validate_chunks(cls, v):
        """Valida que la lista de chunks no esté vacía."""
        if not v:
            raise ValueError("La lista de chunks no puede estar vacía")
        return v


class AddChunksResponse(BaseModel):
    """Response de agregado de chunks."""
    success: bool = Field(..., description="True si se agregaron exitosamente")
    collection_name: str = Field(..., description="Nombre de la colección")
    chunks_added: int = Field(..., description="Número de chunks agregados")
    message: str = Field(..., description="Mensaje descriptivo")


# ============================================================================
# Modelos para Health Check
# ============================================================================

class VectorDBHealthResponse(BaseModel):
    """Response del health check de la base de datos vectorial."""
    status: str = Field(..., description="Estado de la conexión")
    db_type: str = Field(..., description="Tipo de base de datos vectorial")
    message: str = Field(..., description="Mensaje descriptivo")


# ============================================================================
# Modelos para Errores
# ============================================================================

class VectorDBErrorResponse(BaseModel):
    """Response genérico de error."""
    error: str = Field(..., description="Descripción del error")
    detail: Optional[str] = Field(None, description="Detalle adicional del error")
