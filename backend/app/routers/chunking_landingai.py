"""
Router para procesamiento de PDFs con LandingAI.
Soporta dos modos: rápido (solo parse) y extracción (parse + extract con schema).
"""

import logging
import time
from typing import List, Literal, Optional

from fastapi import APIRouter, HTTPException
from langchain_core.documents import Document
from pydantic import BaseModel, Field

from ..repositories.schema_repository import get_schema_repository
from ..services.chunking_service import get_chunking_service
from ..services.landingai_service import get_landingai_service
from ..services.extracted_data_service import get_extracted_data_service
from ..utils.chunking.token_manager import TokenManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chunking-landingai", tags=["chunking-landingai"])


class ProcessLandingAIRequest(BaseModel):
    """Request para procesar PDF con LandingAI"""

    file_name: str = Field(..., description="Nombre del archivo PDF")
    tema: str = Field(..., description="Tema/carpeta del archivo")
    collection_name: str = Field(..., description="Colección de Qdrant")

    # Modo de procesamiento
    mode: Literal["quick", "extract"] = Field(
        default="quick",
        description="Modo: 'quick' (solo parse) o 'extract' (parse + datos estructurados)",
    )

    # Schema (obligatorio si mode='extract')
    schema_id: Optional[str] = Field(
        None, description="ID del schema a usar (requerido si mode='extract')"
    )

    # Configuración de chunks
    include_chunk_types: List[str] = Field(
        default=["text", "table"],
        description="Tipos de chunks a incluir: text, table, figure, etc.",
    )
    max_tokens_per_chunk: int = Field(
        default=1500,
        ge=500,
        le=3000,
        description="Tokens máximos por chunk (flexible para tablas/figuras)",
    )
    merge_small_chunks: bool = Field(
        default=True, description="Unir chunks pequeños de la misma página y tipo"
    )


class ProcessLandingAIResponse(BaseModel):
    """Response del procesamiento con LandingAI"""

    success: bool
    mode: str
    processing_time_seconds: float
    collection_name: str
    file_name: str
    total_chunks: int
    chunks_added: int
    schema_used: Optional[str] = None
    extracted_data: Optional[dict] = None
    parse_metadata: dict
    message: str


@router.post("/process", response_model=ProcessLandingAIResponse)
async def process_with_landingai(request: ProcessLandingAIRequest):
    """
    Procesa un PDF con LandingAI y sube a Qdrant.

    Flujo:
    1. Descarga PDF de Azure Blob
    2. Parse con LandingAI (siempre)
    3. Extract con schema (solo si mode='extract')
    4. Procesa chunks (filtrado, merge, control de tokens)
    5. Genera embeddings (Azure OpenAI)
    6. Sube a Qdrant con metadata rica

    Args:
        request: Configuración del procesamiento

    Returns:
        Resultado del procesamiento con estadísticas

    Raises:
        HTTPException 400: Si mode='extract' y no se provee schema_id
        HTTPException 404: Si el PDF o schema no existen
        HTTPException 500: Si hay error en el procesamiento
    """
    start_time = time.time()

    try:
        logger.info(f"\n{'=' * 60}")
        logger.info("INICIANDO PROCESAMIENTO CON LANDINGAI")
        logger.info(f"{'=' * 60}")
        logger.info(f"Archivo: {request.file_name}")
        logger.info(f"Tema: {request.tema}")
        logger.info(f"Modo: {request.mode}")
        logger.info(f"Colección: {request.collection_name}")
        logger.info(f"Schema ID recibido: '{request.schema_id}' (tipo: {type(request.schema_id).__name__})")

        # 1. Validar schema si es modo extract
        custom_schema = None
        if request.mode == "extract":
            if not request.schema_id or request.schema_id.strip() == "":
                raise HTTPException(
                    status_code=400,
                    detail="schema_id es requerido cuando mode='extract'",
                )

            schema_repo = get_schema_repository()
            custom_schema = schema_repo.get_by_id(request.schema_id)

            if not custom_schema:
                raise HTTPException(
                    status_code=404, detail=f"Schema no encontrado: {request.schema_id}"
                )

            logger.info(f"Schema seleccionado: {custom_schema.schema_name}")

        # 2. Descargar PDF desde Azure Blob
        logger.info("\n[1/5] Descargando PDF desde Azure Blob...")
        chunking_service = get_chunking_service()

        try:
            pdf_bytes = await chunking_service.download_pdf_from_blob(
                request.file_name, request.tema
            )
        except Exception as e:
            logger.error(f"Error descargando PDF: {e}")
            raise HTTPException(
                status_code=404, detail=f"No se pudo descargar el PDF: {str(e)}"
            )

        # 3. Procesar con LandingAI
        logger.info("\n[2/5] Procesando con LandingAI...")
        landingai_service = get_landingai_service()

        try:
            result = landingai_service.process_pdf(
                pdf_bytes=pdf_bytes,
                file_name=request.file_name,
                custom_schema=custom_schema,
                include_chunk_types=request.include_chunk_types,
            )
        except Exception as e:
            logger.error(f"Error en LandingAI: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error procesando con LandingAI: {str(e)}"
            )

        documents = result["chunks"]

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No se generaron chunks después del procesamiento",
            )

        # 4. Aplicar control flexible de tokens
        logger.info("\n[3/5] Aplicando control de tokens...")
        documents = _apply_flexible_token_control(
            documents,
            max_tokens=request.max_tokens_per_chunk,
            merge_small=request.merge_small_chunks,
        )

        # 5. Generar embeddings
        logger.info(f"\n[4/5] Generando embeddings para {len(documents)} chunks...")
        texts = [doc.page_content for doc in documents]

        try:
            embeddings = (
                await chunking_service.embedding_service.generate_embeddings_batch(
                    texts
                )
            )
            logger.info(f"Embeddings generados: {len(embeddings)} vectores")
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generando embeddings: {str(e)}"
            )

        # 6. Preparar chunks para Qdrant con IDs determinísticos
        logger.info("\n[5/5] Subiendo a Qdrant...")
        qdrant_chunks = []

        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # ID determinístico
            chunk_id = chunking_service._generate_deterministic_id(
                file_name=request.file_name,
                page=doc.metadata.get("page", 1),
                chunk_index=doc.metadata.get("chunk_id", str(idx)),
            )

            qdrant_chunks.append(
                {
                    "id": chunk_id,
                    "vector": embedding,
                    "payload": {
                        "page_content": doc.page_content,
                        "metadata": doc.metadata,  # Metadata rica de LandingAI
                    },
                }
            )

        # 7. Subir a Qdrant
        try:
            upload_result = await chunking_service.vector_db.add_chunks(
                request.collection_name, qdrant_chunks
            )
            logger.info(f"Subida completada: {upload_result['chunks_added']} chunks")
        except Exception as e:
            logger.error(f"Error subiendo a Qdrant: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error subiendo a Qdrant: {str(e)}"
            )

        # 8. Guardar datos extraídos en Redis (si existe extracted_data)
        if result.get("extracted_data") and result["extracted_data"].get("extraction"):
            try:
                logger.info("\n[6/6] Guardando datos extraídos en Redis...")
                extracted_data_service = get_extracted_data_service()

                await extracted_data_service.save_extracted_data(
                    file_name=request.file_name,
                    tema=request.tema,
                    collection_name=request.collection_name,
                    extracted_data=result["extracted_data"]["extraction"]
                )
            except Exception as e:
                # No fallar si Redis falla, solo logear
                logger.warning(f"⚠️  No se pudieron guardar datos en Redis (no crítico): {e}")

        # Tiempo total
        processing_time = time.time() - start_time

        logger.info(f"\n{'=' * 60}")
        logger.info(f"PROCESAMIENTO COMPLETADO")
        logger.info(f"{'=' * 60}")
        logger.info(f"Tiempo: {processing_time:.2f}s")
        logger.info(f"Chunks procesados: {len(documents)}")
        logger.info(f"Chunks subidos: {upload_result['chunks_added']}")

        return ProcessLandingAIResponse(
            success=True,
            mode=request.mode,
            processing_time_seconds=round(processing_time, 2),
            collection_name=request.collection_name,
            file_name=request.file_name,
            total_chunks=len(documents),
            chunks_added=upload_result["chunks_added"],
            schema_used=custom_schema.schema_id if custom_schema else None,
            extracted_data=result.get("extracted_data"),
            parse_metadata=result["parse_metadata"],
            message=f"PDF procesado exitosamente en modo {request.mode}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en procesamiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


def _apply_flexible_token_control(
    documents: List[Document], max_tokens: int, merge_small: bool
) -> List[Document]:
    """
    Aplica control flexible de tokens (Opción C del diseño).

    - Permite chunks más grandes para tablas/figuras (50% extra)
    - Mergea chunks pequeños de misma página y tipo
    - Divide chunks muy grandes en sub-chunks

    Args:
        documents: Lista de Documents
        max_tokens: Límite sugerido de tokens
        merge_small: Si True, une chunks pequeños

    Returns:
        Lista de Documents procesados
    """
    token_manager = TokenManager()
    processed = []
    i = 0

    logger.info(f"Control de tokens: max={max_tokens}, merge={merge_small}")

    while i < len(documents):
        doc = documents[i]
        tokens = token_manager.count_tokens(doc.page_content)
        chunk_type = doc.metadata.get("chunk_type", "text")

        # Límite flexible según tipo
        if chunk_type in ["table", "figure"]:
            max_allowed = int(max_tokens * 1.5)  # 50% más para contenido estructurado
        else:
            max_allowed = max_tokens

        # Si excede mucho el límite, dividir
        if tokens > max_allowed * 1.2:  # 20% de tolerancia
            logger.warning(
                f"Chunk muy grande ({tokens} tokens), dividiendo... "
                f"(tipo: {chunk_type})"
            )
            sub_chunks = _split_large_chunk(doc, max_tokens, token_manager)
            processed.extend(sub_chunks)

        else:
            # Intentar merge si es pequeño
            if merge_small and tokens < max_tokens * 0.5 and i < len(documents) - 1:
                next_doc = documents[i + 1]
                if _can_merge(doc, next_doc, max_tokens, token_manager):
                    logger.debug(f"Merging chunks {i} y {i + 1}")
                    doc = _merge_documents(doc, next_doc)
                    i += 1  # Skip next

            processed.append(doc)

        i += 1

    logger.info(f"Tokens aplicados: {len(documents)} → {len(processed)} chunks")
    return processed


def _split_large_chunk(
    doc: Document, max_tokens: int, token_manager: TokenManager
) -> List[Document]:
    """Divide un chunk grande en sub-chunks"""
    content = doc.page_content
    words = content.split()
    sub_chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = token_manager.count_tokens(word)
        if current_tokens + word_tokens > max_tokens and current_chunk:
            # Guardar chunk actual
            sub_content = " ".join(current_chunk)
            sub_doc = Document(
                page_content=sub_content, metadata={**doc.metadata, "is_split": True}
            )
            sub_chunks.append(sub_doc)
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    # Último chunk
    if current_chunk:
        sub_content = " ".join(current_chunk)
        sub_doc = Document(
            page_content=sub_content, metadata={**doc.metadata, "is_split": True}
        )
        sub_chunks.append(sub_doc)

    return sub_chunks


def _can_merge(
    doc1: Document, doc2: Document, max_tokens: int, token_manager: TokenManager
) -> bool:
    """Verifica si dos docs se pueden mergear"""
    # Misma página
    if doc1.metadata.get("page") != doc2.metadata.get("page"):
        return False

    # Mismo tipo
    if doc1.metadata.get("chunk_type") != doc2.metadata.get("chunk_type"):
        return False

    # No exceder límite
    combined_text = f"{doc1.page_content}\n\n{doc2.page_content}"
    combined_tokens = token_manager.count_tokens(combined_text)

    return combined_tokens <= max_tokens


def _merge_documents(doc1: Document, doc2: Document) -> Document:
    """Mergea dos documentos"""
    merged_content = f"{doc1.page_content}\n\n{doc2.page_content}"
    return Document(
        page_content=merged_content, metadata={**doc1.metadata, "is_merged": True}
    )
