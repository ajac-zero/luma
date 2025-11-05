"""
Modelos Pydantic para las operaciones de chunking.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional


# Request Models

class ChunkingPreviewRequest(BaseModel):
    """Request para generar preview de chunks"""
    file_name: str = Field(..., description="Nombre del archivo PDF")
    tema: str = Field(..., description="Tema/carpeta del archivo")
    max_tokens: int = Field(default=950, ge=100, le=2000, description="Límite máximo de tokens por chunk")
    target_tokens: int = Field(default=800, ge=100, le=2000, description="Tokens objetivo")
    chunk_size: int = Field(default=1000, ge=100, le=3000, description="Tamaño del chunk")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Solapamiento entre chunks")
    use_llm: bool = Field(default=True, description="Usar LLM (Gemini) para procesamiento inteligente")
    custom_instructions: str = Field(default="", description="Instrucciones personalizadas (solo si use_llm=True)")

    @validator("custom_instructions")
    def validate_custom_instructions(cls, v, values):
        """Valida que custom_instructions solo se use con LLM habilitado"""
        if v and not values.get("use_llm", True):
            raise ValueError("custom_instructions solo puede usarse cuando use_llm=True")
        return v

    @validator("target_tokens")
    def validate_target_tokens(cls, v, values):
        """Valida que target_tokens sea menor que max_tokens"""
        if "max_tokens" in values and v >= values["max_tokens"]:
            raise ValueError("target_tokens debe ser menor que max_tokens")
        return v


class ChunkingProcessRequest(BaseModel):
    """Request para procesar PDF completo"""
    file_name: str = Field(..., description="Nombre del archivo PDF")
    tema: str = Field(..., description="Tema/carpeta del archivo")
    collection_name: str = Field(..., description="Nombre de la colección en Qdrant")
    max_tokens: int = Field(default=950, ge=100, le=2000, description="Límite máximo de tokens por chunk")
    target_tokens: int = Field(default=800, ge=100, le=2000, description="Tokens objetivo")
    chunk_size: int = Field(default=1000, ge=100, le=3000, description="Tamaño del chunk")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Solapamiento entre chunks")
    use_llm: bool = Field(default=True, description="Usar LLM (Gemini) para procesamiento inteligente")
    custom_instructions: str = Field(default="", description="Instrucciones personalizadas (solo si use_llm=True)")

    @validator("custom_instructions")
    def validate_custom_instructions(cls, v, values):
        """Valida que custom_instructions solo se use con LLM habilitado"""
        if v and not values.get("use_llm", True):
            raise ValueError("custom_instructions solo puede usarse cuando use_llm=True")
        return v

    @validator("target_tokens")
    def validate_target_tokens(cls, v, values):
        """Valida que target_tokens sea menor que max_tokens"""
        if "max_tokens" in values and v >= values["max_tokens"]:
            raise ValueError("target_tokens debe ser menor que max_tokens")
        return v


# Response Models

class ChunkPreview(BaseModel):
    """Modelo para un chunk de preview"""
    index: int = Field(..., description="Índice del chunk")
    text: str = Field(..., description="Contenido del chunk")
    page: int = Field(..., description="Número de página")
    file_name: str = Field(..., description="Nombre del archivo")
    tokens: int = Field(..., description="Número aproximado de tokens")


class ChunkingPreviewResponse(BaseModel):
    """Response para preview de chunks"""
    success: bool = Field(default=True, description="Indica si la operación fue exitosa")
    file_name: str = Field(..., description="Nombre del archivo procesado")
    tema: str = Field(..., description="Tema del archivo")
    chunks: List[ChunkPreview] = Field(..., description="Lista de chunks de preview (hasta 3)")
    message: str = Field(default="Preview generado exitosamente", description="Mensaje descriptivo")

    @validator("chunks")
    def validate_chunk_count(cls, v):
        """Valida que haya al menos 1 chunk y máximo 3 chunks en el preview"""
        if len(v) < 1:
            raise ValueError("El preview debe contener al menos 1 chunk")
        if len(v) > 3:
            raise ValueError("El preview no puede contener más de 3 chunks")
        return v


class ChunkingProcessResponse(BaseModel):
    """Response para procesamiento completo"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    collection_name: str = Field(..., description="Nombre de la colección")
    file_name: str = Field(..., description="Nombre del archivo procesado")
    total_chunks: int = Field(..., description="Total de chunks generados")
    chunks_added: int = Field(..., description="Chunks agregados a Qdrant")
    message: str = Field(..., description="Mensaje descriptivo")


# Profile Models

class ChunkingProfile(BaseModel):
    """Perfil de configuración predefinido para chunking"""
    id: str = Field(..., description="ID del perfil")
    name: str = Field(..., description="Nombre del perfil")
    description: str = Field(..., description="Descripción del perfil")
    max_tokens: int = Field(..., description="Límite máximo de tokens")
    target_tokens: int = Field(..., description="Tokens objetivo")
    chunk_size: int = Field(..., description="Tamaño del chunk")
    chunk_overlap: int = Field(..., description="Solapamiento")
    use_llm: bool = Field(..., description="Si usa LLM")


class ChunkingProfilesResponse(BaseModel):
    """Response con perfiles disponibles"""
    profiles: List[ChunkingProfile] = Field(..., description="Lista de perfiles disponibles")


# Progress Models (para WebSockets)

class ChunkingProgress(BaseModel):
    """Modelo para reportar progreso de chunking"""
    status: str = Field(..., description="Estado actual: downloading, chunking, embedding, uploading, completed, error")
    progress: int = Field(..., ge=0, le=100, description="Progreso en porcentaje")
    message: Optional[str] = Field(None, description="Mensaje adicional")
    error: Optional[str] = Field(None, description="Mensaje de error si status=error")
