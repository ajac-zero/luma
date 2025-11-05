"""
Router para operaciones de chunking de PDFs.
Endpoints para generar preview y procesar PDFs completos.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from typing import List

from ..models.chunking_models import (
    ChunkingPreviewRequest,
    ChunkingPreviewResponse,
    ChunkingProcessRequest,
    ChunkingProcessResponse,
    ChunkingProfilesResponse,
    ChunkingProfile,
    ChunkPreview
)
from ..services.chunking_service import get_chunking_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chunking", tags=["chunking"])


# Perfiles predefinidos
CHUNKING_PROFILES = [
    ChunkingProfile(
        id="balanced",
        name="Balanceado",
        description="Configuración equilibrada entre velocidad y calidad",
        max_tokens=950,
        target_tokens=800,
        chunk_size=1000,
        chunk_overlap=200,
        use_llm=True
    ),
    ChunkingProfile(
        id="detailed",
        name="Detallado",
        description="Chunks más grandes para mantener más contexto",
        max_tokens=1500,
        target_tokens=1200,
        chunk_size=1500,
        chunk_overlap=300,
        use_llm=True
    ),
    ChunkingProfile(
        id="compact",
        name="Compacto",
        description="Chunks más pequeños para búsquedas precisas",
        max_tokens=600,
        target_tokens=500,
        chunk_size=700,
        chunk_overlap=150,
        use_llm=True
    ),
    ChunkingProfile(
        id="fast",
        name="Rápido",
        description="Sin LLM, solo procesamiento básico",
        max_tokens=950,
        target_tokens=800,
        chunk_size=1000,
        chunk_overlap=200,
        use_llm=False
    ),
]


@router.get("/profiles", response_model=ChunkingProfilesResponse)
async def get_chunking_profiles():
    """
    Obtiene los perfiles de configuración predefinidos para chunking.

    Returns:
        Lista de perfiles disponibles
    """
    return ChunkingProfilesResponse(profiles=CHUNKING_PROFILES)


@router.post("/preview", response_model=ChunkingPreviewResponse)
async def generate_preview(request: ChunkingPreviewRequest):
    """
    Genera preview de chunks para un PDF (hasta 3 chunks).

    Args:
        request: Configuración de chunking y ubicación del archivo

    Returns:
        Preview con chunks de ejemplo (máximo 3, mínimo 1)

    Raises:
        HTTPException: Si hay error generando el preview
    """
    try:
        logger.info(f"Generando preview para {request.file_name} (tema: {request.tema})")

        chunking_service = get_chunking_service()

        chunks = await chunking_service.process_pdf_preview(
            file_name=request.file_name,
            tema=request.tema,
            max_tokens=request.max_tokens,
            target_tokens=request.target_tokens,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            use_llm=request.use_llm,
            custom_instructions=request.custom_instructions
        )

        # Convertir a modelos Pydantic
        chunk_previews = [
            ChunkPreview(
                index=chunk["index"],
                text=chunk["text"],
                page=chunk["page"],
                file_name=chunk["file_name"],
                tokens=chunk["tokens"]
            )
            for chunk in chunks
        ]

        return ChunkingPreviewResponse(
            success=True,
            file_name=request.file_name,
            tema=request.tema,
            chunks=chunk_previews,
            message="Preview generado exitosamente"
        )

    except Exception as e:
        logger.error(f"Error generando preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando preview: {str(e)}"
        )


@router.post("/process", response_model=ChunkingProcessResponse)
async def process_pdf_full(request: ChunkingProcessRequest):
    """
    Procesa un PDF completo y lo sube a Qdrant.

    Este endpoint:
    1. Descarga el PDF desde Azure Blob
    2. Lo procesa en chunks con control de tokens
    3. Genera embeddings con Azure OpenAI
    4. Sube los chunks a Qdrant con IDs determinísticos

    Args:
        request: Configuración de chunking y destino

    Returns:
        Resultado del procesamiento con estadísticas

    Raises:
        HTTPException: Si hay error procesando el PDF
    """
    try:
        logger.info(f"Procesando PDF completo: {request.file_name} (tema: {request.tema})")

        chunking_service = get_chunking_service()

        result = await chunking_service.process_pdf_full(
            file_name=request.file_name,
            tema=request.tema,
            collection_name=request.collection_name,
            max_tokens=request.max_tokens,
            target_tokens=request.target_tokens,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            use_llm=request.use_llm,
            custom_instructions=request.custom_instructions
        )

        return ChunkingProcessResponse(**result)

    except Exception as e:
        logger.error(f"Error procesando PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando PDF: {str(e)}"
        )
