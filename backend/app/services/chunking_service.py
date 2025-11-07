"""
Servicio de chunking que orquesta todo el proceso:
- Descarga PDF desde Azure Blob
- Procesa con pipeline de chunking
- Genera embeddings con Azure OpenAI
- Sube a Qdrant con IDs determinísticos
"""
import logging
import uuid
from typing import List, Dict, Any, Optional
from io import BytesIO

from azure.storage.blob import BlobServiceClient
from langchain_core.documents import Document

from ..core.config import settings
from ..utils.chunking import (
    process_pdf_with_token_control,
    get_gemini_client,
    GeminiClient
)
from ..services.embedding_service import get_embedding_service
from ..vector_db.factory import get_vector_db

logger = logging.getLogger(__name__)


class ChunkingService:
    """Servicio para procesar PDFs y subirlos a Qdrant"""

    def __init__(self):
        """Inicializa el servicio con conexiones a Azure Blob y clientes"""
        self.blob_service = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = settings.AZURE_CONTAINER_NAME
        self.embedding_service = get_embedding_service()
        self.vector_db = get_vector_db()

    def _generate_deterministic_id(
        self,
        file_name: str,
        page: int,
        chunk_index: int
    ) -> str:
        """
        Genera un ID determinístico para un chunk usando UUID v5.

        Args:
            file_name: Nombre del archivo
            page: Número de página
            chunk_index: Índice del chunk dentro de la página

        Returns:
            ID en formato UUID válido para Qdrant
        """
        id_string = f"{file_name}_{page}_{chunk_index}"
        # Usar UUID v5 con namespace DNS para generar UUID determinístico
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, id_string))

    async def download_pdf_from_blob(
        self,
        file_name: str,
        tema: str
    ) -> bytes:
        """
        Descarga un PDF desde Azure Blob Storage.

        NOTA: Todos los blobs se guardan en minúsculas en Azure.

        Args:
            file_name: Nombre del archivo
            tema: Tema/carpeta del archivo

        Returns:
            Contenido del PDF en bytes

        Raises:
            Exception: Si hay error descargando el archivo
        """
        try:
            # Convertir a minúsculas ya que todos los blobs están en minúsculas
            blob_path = f"{tema.lower()}/{file_name.lower()}"
            logger.info(f"Descargando PDF: {blob_path} (tema original: {tema}, file original: {file_name})")

            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=blob_path
            )

            pdf_bytes = blob_client.download_blob().readall()
            logger.info(f"PDF descargado: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error descargando PDF: {e}")
            raise

    async def process_pdf_preview(
        self,
        file_name: str,
        tema: str,
        max_tokens: int = 950,
        target_tokens: int = 800,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_llm: bool = True,
        custom_instructions: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Procesa un PDF y genera exactamente 3 chunks de preview.

        Args:
            file_name: Nombre del archivo PDF
            tema: Tema/carpeta del archivo
            max_tokens: Límite máximo de tokens por chunk
            target_tokens: Tokens objetivo
            chunk_size: Tamaño del chunk
            chunk_overlap: Solapamiento
            use_llm: Si True, usa Gemini para procesamiento inteligente
            custom_instructions: Instrucciones personalizadas (solo si use_llm=True)

        Returns:
            Lista con exactamente 3 chunks de preview con metadata
        """
        try:
            logger.info(f"Generando preview para {file_name} (tema: {tema})")

            # Descargar PDF
            pdf_bytes = await self.download_pdf_from_blob(file_name, tema)

            # Configurar cliente Gemini si está habilitado
            gemini_client = get_gemini_client() if use_llm else None

            # Si LLM está deshabilitado, ignorar custom_instructions
            instructions = custom_instructions if use_llm else ""

            # Procesar PDF
            chunks = process_pdf_with_token_control(
                pdf_bytes=pdf_bytes,
                file_name=file_name,
                max_tokens=max_tokens,
                target_tokens=target_tokens,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                merge_related=True,
                gemini_client=gemini_client,
                custom_instructions=instructions,
                extract_images=False  # Deshabilitado según requerimientos
            )

            # Tomar los primeros chunks para preview (máximo 3, mínimo 1)
            preview_chunks = chunks[:min(3, len(chunks))] if chunks else []

            # Formatear para respuesta
            result = []
            for idx, chunk in enumerate(preview_chunks):
                result.append({
                    "index": idx,
                    "text": chunk.page_content,
                    "page": chunk.metadata.get("page", 0),
                    "file_name": chunk.metadata.get("file_name", file_name),
                    "tokens": len(chunk.page_content.split())  # Aproximación
                })

            logger.info(f"Preview generado: {len(result)} chunks")
            return result

        except Exception as e:
            logger.error(f"Error generando preview: {e}")
            raise

    async def process_pdf_full(
        self,
        file_name: str,
        tema: str,
        collection_name: str,
        max_tokens: int = 950,
        target_tokens: int = 800,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_llm: bool = True,
        custom_instructions: str = "",
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Procesa un PDF completo y lo sube a Qdrant.

        Args:
            file_name: Nombre del archivo PDF
            tema: Tema/carpeta del archivo
            collection_name: Nombre de la colección en Qdrant
            max_tokens: Límite máximo de tokens por chunk
            target_tokens: Tokens objetivo
            chunk_size: Tamaño del chunk
            chunk_overlap: Solapamiento
            use_llm: Si True, usa Gemini para procesamiento inteligente
            custom_instructions: Instrucciones personalizadas (solo si use_llm=True)
            progress_callback: Callback para reportar progreso

        Returns:
            Diccionario con resultados del procesamiento
        """
        try:
            logger.info(f"Procesando PDF completo: {file_name} (tema: {tema})")

            if progress_callback:
                await progress_callback({"status": "downloading", "progress": 0})

            # 1. Descargar PDF
            pdf_bytes = await self.download_pdf_from_blob(file_name, tema)

            if progress_callback:
                await progress_callback({"status": "chunking", "progress": 20})

            # 2. Configurar cliente Gemini
            gemini_client = get_gemini_client() if use_llm else None
            instructions = custom_instructions if use_llm else ""

            # 3. Procesar PDF
            chunks = process_pdf_with_token_control(
                pdf_bytes=pdf_bytes,
                file_name=file_name,
                max_tokens=max_tokens,
                target_tokens=target_tokens,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                merge_related=True,
                gemini_client=gemini_client,
                custom_instructions=instructions,
                extract_images=False
            )

            if progress_callback:
                await progress_callback({"status": "embedding", "progress": 50})

            # 4. Generar embeddings
            texts = [chunk.page_content for chunk in chunks]
            logger.info(f"Generando embeddings para {len(texts)} chunks")
            embeddings = await self.embedding_service.generate_embeddings_batch(texts)
            logger.info(f"Embeddings generados: {len(embeddings)} vectores de dimensión {len(embeddings[0]) if embeddings else 0}")

            if progress_callback:
                await progress_callback({"status": "uploading", "progress": 80})

            # 5. Preparar chunks para Qdrant con IDs determinísticos
            qdrant_chunks = []
            page_chunk_count = {}  # Contador de chunks por página

            logger.info(f"Preparando {len(chunks)} chunks con {len(embeddings)} embeddings para subir")
            for chunk, embedding in zip(chunks, embeddings):
                page = chunk.metadata.get("page", 0)

                # Incrementar contador para esta página
                if page not in page_chunk_count:
                    page_chunk_count[page] = 0
                chunk_index = page_chunk_count[page]
                page_chunk_count[page] += 1

                # Generar ID determinístico
                chunk_id = self._generate_deterministic_id(
                    file_name=file_name,
                    page=page,
                    chunk_index=chunk_index
                )

                qdrant_chunks.append({
                    "id": chunk_id,
                    "vector": embedding,
                    "payload": {
                        "page_content": chunk.page_content,
                        "metadata": {
                            "page": page,
                            "file_name": file_name
                        }
                    }
                })

            # 6. Subir a Qdrant
            logger.info(f"Subiendo {len(qdrant_chunks)} chunks a Qdrant colección '{collection_name}'")
            result = await self.vector_db.add_chunks(collection_name, qdrant_chunks)
            logger.info(f"Resultado de upsert: {result}")

            if progress_callback:
                await progress_callback({"status": "completed", "progress": 100})

            logger.info(f"Procesamiento completo: {result['chunks_added']} chunks subidos")

            return {
                "success": True,
                "collection_name": collection_name,
                "file_name": file_name,
                "total_chunks": len(chunks),
                "chunks_added": result['chunks_added'],
                "message": "PDF procesado y subido exitosamente"
            }

        except Exception as e:
            logger.error(f"Error procesando PDF completo: {e}")
            if progress_callback:
                await progress_callback({"status": "error", "progress": 0, "error": str(e)})
            raise


# Instancia global singleton
_chunking_service: ChunkingService | None = None


def get_chunking_service() -> ChunkingService:
    """
    Obtiene la instancia singleton del servicio de chunking.

    Returns:
        Instancia de ChunkingService
    """
    global _chunking_service
    if _chunking_service is None:
        _chunking_service = ChunkingService()
    return _chunking_service
