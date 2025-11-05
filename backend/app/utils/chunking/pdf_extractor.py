"""
Extractor optimizado de PDFs con soporte para BytesIO y procesamiento paralelo.
Adaptado para trabajar con Azure Blob Storage sin archivos temporales.
"""
import logging
import os
import time
import hashlib
from typing import List, Optional, Dict, BinaryIO
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

from langchain_core.documents import Document
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdf2image import convert_from_bytes

from .token_manager import TokenManager
from .chunk_processor import OptimizedChunkProcessor
from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class OptimizedPDFExtractor:
    """Extractor optimizado de PDFs con soporte para BytesIO"""

    def __init__(
        self,
        max_tokens: int = 1000,
        target_tokens: int = 800,
        gemini_client: Optional[GeminiClient] = None,
        custom_instructions: str = "",
        extract_images: bool = False,  # Por defecto deshabilitado según requerimientos
        max_workers: int = 4
    ):
        """
        Inicializa el extractor de PDFs.

        Args:
            max_tokens: Límite máximo de tokens por chunk
            target_tokens: Tokens objetivo para chunks
            gemini_client: Cliente de Gemini (opcional)
            custom_instructions: Instrucciones adicionales para optimización
            extract_images: Si True, extrae páginas con formato especial como imágenes
            max_workers: Número máximo de workers para procesamiento paralelo
        """
        self.client = gemini_client
        self.max_workers = max_workers
        self.token_manager = TokenManager()
        self.custom_instructions = custom_instructions
        self.extract_images = extract_images
        self._format_cache = {}

        self.chunk_processor = OptimizedChunkProcessor(
            max_tokens=max_tokens,
            target_tokens=target_tokens,
            gemini_client=gemini_client,
            custom_instructions=custom_instructions
        )

    def detect_special_format_batch(self, chunks: List[Document]) -> Dict[int, bool]:
        """
        Detecta chunks con formatos especiales (tablas, diagramas, etc.) en lote.

        Args:
            chunks: Lista de chunks a analizar

        Returns:
            Diccionario con índices de chunks y si tienen formato especial
        """
        results = {}

        chunks_to_process = []
        for i, chunk in enumerate(chunks):
            cache_key = hashlib.md5(chunk.page_content.encode()).hexdigest()[:16]
            if cache_key in self._format_cache:
                results[i] = self._format_cache[cache_key]
            else:
                chunks_to_process.append((i, chunk, cache_key))

        if not chunks_to_process:
            return results

        logger.info(f"Analizando {len(chunks_to_process)} chunks para formatos especiales...")

        if self.client and len(chunks_to_process) > 1:
            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(chunks_to_process))) as executor:
                futures = {
                    executor.submit(self._detect_single_format, chunk): (i, cache_key)
                    for i, chunk, cache_key in chunks_to_process
                }

                for future in futures:
                    i, cache_key = futures[future]
                    try:
                        result = future.result()
                        results[i] = result
                        self._format_cache[cache_key] = result
                    except Exception as e:
                        logger.error(f"Error procesando chunk {i}: {e}")
                        results[i] = False
                        self._format_cache[cache_key] = False
        else:
            for i, chunk, cache_key in chunks_to_process:
                result = self._detect_single_format(chunk)
                results[i] = result
                self._format_cache[cache_key] = result

        return results

    def _detect_single_format(self, chunk: Document) -> bool:
        """Detecta formato especial en un chunk individual."""
        if not self.client:
            content = chunk.page_content
            table_indicators = ['│', '├', '┼', '┤', '┬', '┴', '|', '+', '-']
            has_table_chars = any(char in content for char in table_indicators)
            has_multiple_columns = content.count('\t') > 10 or content.count('  ') > 20
            return has_table_chars or has_multiple_columns

        try:
            prompt = f"""¿Contiene este texto tablas estructuradas, diagramas ASCII, o elementos que requieren formato especial?

Responde SOLO 'SI' o 'NO'.

Texto:
{chunk.page_content[:1000]}"""

            response = self.client.generate_content(prompt)
            return response.strip().upper() == 'SI'

        except Exception as e:
            logger.error(f"Error detectando formato: {e}")
            return False

    def process_pdf_from_bytes(
        self,
        pdf_bytes: bytes,
        file_name: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        merge_related: bool = True
    ) -> List[Document]:
        """
        Procesa un PDF desde bytes (BytesIO).

        Args:
            pdf_bytes: Contenido del PDF en bytes
            file_name: Nombre del archivo PDF
            chunk_size: Tamaño del chunk
            chunk_overlap: Solapamiento entre chunks
            merge_related: Si True, intenta unir chunks relacionados

        Returns:
            Lista de documentos procesados
        """
        overall_start = time.time()
        logger.info(f"\n=== Iniciando procesamiento optimizado de PDF: {file_name} ===")
        logger.info(f"Configuración:")
        logger.info(f"  - Tokens máximos por chunk: {self.chunk_processor.max_tokens}")
        logger.info(f"  - Tokens objetivo: {self.chunk_processor.target_tokens}")
        logger.info(f"  - Chunk size: {chunk_size}")
        logger.info(f"  - Chunk overlap: {chunk_overlap}")
        logger.info(f"  - Merge relacionados: {merge_related}")
        logger.info(f"  - Extraer imágenes: {'✅' if self.extract_images else '❌'}")
        if self.custom_instructions:
            logger.info(f"  - Instrucciones personalizadas: {self.custom_instructions[:100]}...")

        logger.info(f"\n1. Creando chunks del PDF...")
        chunks = self._create_optimized_chunks_from_bytes(
            pdf_bytes,
            file_name,
            chunk_size,
            chunk_overlap
        )
        logger.info(f"  Total chunks creados: {len(chunks)}")

        # Nota: La extracción de imágenes desde bytes no se implementa por ahora
        # ya que extract_images está deshabilitado por defecto según requerimientos
        if self.extract_images:
            logger.warning("Extracción de imágenes desde bytes no implementada aún")

        logger.info(f"\n2. Procesando y optimizando chunks...")
        processed_chunks = self.chunk_processor.process_chunks_batch(chunks, merge_related)

        total_time = time.time() - overall_start
        if processed_chunks:
            avg_tokens = sum(
                self.token_manager.count_tokens(chunk.page_content)
                for chunk in processed_chunks
            ) / len(processed_chunks)
        else:
            avg_tokens = 0

        logger.info(f"\n=== Procesamiento completado ===")
        logger.info(f"  Tiempo total: {total_time:.2f}s")
        logger.info(f"  Chunks procesados: {len(processed_chunks)}")
        logger.info(f"  Tokens promedio por chunk: {avg_tokens:.1f}")
        if self.custom_instructions:
            logger.info(f"  Custom instructions aplicadas: ✅")

        return processed_chunks

    def _create_optimized_chunks_from_bytes(
        self,
        pdf_bytes: bytes,
        file_name: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Document]:
        """
        Crea chunks optimizados desde bytes del PDF.

        Args:
            pdf_bytes: Contenido del PDF en bytes
            file_name: Nombre del archivo
            chunk_size: Tamaño del chunk
            chunk_overlap: Solapamiento entre chunks

        Returns:
            Lista de documentos con chunks
        """
        logger.info(f"  Leyendo PDF desde bytes: {file_name}")

        # Crear BytesIO para pypdf
        pdf_buffer = BytesIO(pdf_bytes)
        pdf = PdfReader(pdf_buffer)
        chunks = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self.token_manager.count_tokens,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Extraer todo el texto concatenado con tracking de páginas
        full_text = ""
        page_boundaries = []  # Lista de (char_position, page_num)

        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text.strip():
                page_start = len(full_text)
                full_text += text
                # Agregar separador entre páginas (excepto después de la última)
                if page_num < len(pdf.pages):
                    full_text += "\n\n"
                page_end = len(full_text)
                page_boundaries.append((page_start, page_end, page_num))

        if not full_text.strip():
            return []

        # Dividir el texto completo (esto permite overlap entre páginas)
        text_chunks = text_splitter.split_text(full_text)

        logger.info(f"  Total de chunks generados por splitter: {len(text_chunks)}")
        if len(text_chunks) >= 2:
            # Verificar overlap entre primer y segundo chunk
            chunk0_end = text_chunks[0][-100:] if len(text_chunks[0]) > 100 else text_chunks[0]
            chunk1_start = text_chunks[1][:100] if len(text_chunks[1]) > 100 else text_chunks[1]
            logger.info(f"  Chunk 0 termina con: ...{chunk0_end}")
            logger.info(f"  Chunk 1 empieza con: {chunk1_start}...")

        # Asignar página a cada chunk basándonos en su posición en el texto original
        chunks = []
        current_search_pos = 0

        for chunk_text in text_chunks:
            # Buscar donde aparece este chunk en el texto completo
            chunk_pos = full_text.find(chunk_text, current_search_pos)

            if chunk_pos == -1:
                # Si no lo encontramos, usar la última posición conocida
                chunk_pos = current_search_pos

            # Determinar la página basándonos en la posición del inicio del chunk
            chunk_page = 1
            for start, end, page_num in page_boundaries:
                if chunk_pos >= start and chunk_pos < end:
                    chunk_page = page_num
                    break
                elif chunk_pos >= end:
                    # El chunk está después de esta página, continuar buscando
                    chunk_page = page_num  # Guardar la última página vista

            chunks.append(Document(
                page_content=chunk_text,
                metadata={
                    "page": chunk_page,
                    "file_name": file_name,
                }
            ))

            # Actualizar posición de búsqueda para el siguiente chunk
            current_search_pos = chunk_pos + len(chunk_text)

        return chunks
