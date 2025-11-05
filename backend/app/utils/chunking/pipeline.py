"""
Pipeline principal para procesar PDFs con control de tokens.
Función de alto nivel que orquesta el proceso completo de chunking.
"""
import logging
from typing import List, Optional
from langchain_core.documents import Document

from .pdf_extractor import OptimizedPDFExtractor
from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)


def process_pdf_with_token_control(
    pdf_bytes: bytes,
    file_name: str,
    max_tokens: int = 950,
    target_tokens: int = 800,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    merge_related: bool = True,
    gemini_client: Optional[GeminiClient] = None,
    custom_instructions: str = "",
    extract_images: bool = False
) -> List[Document]:
    """
    Función principal para procesar PDFs con control completo de tokens.

    Args:
        pdf_bytes: Contenido del PDF en bytes
        file_name: Nombre del archivo PDF
        max_tokens: Límite máximo de tokens por chunk
        target_tokens: Tokens objetivo para optimización
        chunk_size: Tamaño base de chunks
        chunk_overlap: Solapamiento entre chunks
        merge_related: Si unir chunks relacionados
        gemini_client: Cliente de Gemini (opcional, para LLM processing)
        custom_instructions: Instrucciones adicionales para optimización
        extract_images: Si True, extrae páginas con formato especial como imágenes

    Returns:
        Lista de documentos procesados con metadata simple (page, file_name)
    """
    logger.info(f"Iniciando pipeline de chunking para {file_name}")

    extractor = OptimizedPDFExtractor(
        max_tokens=max_tokens,
        target_tokens=target_tokens,
        gemini_client=gemini_client,
        custom_instructions=custom_instructions,
        extract_images=extract_images,
        max_workers=4
    )

    chunks = extractor.process_pdf_from_bytes(
        pdf_bytes=pdf_bytes,
        file_name=file_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        merge_related=merge_related
    )

    logger.info(f"Pipeline completado: {len(chunks)} chunks generados")
    return chunks
