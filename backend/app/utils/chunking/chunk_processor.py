"""
Procesador optimizado de chunks con soporte para LLM (Gemini).
Permite merge inteligente y mejora de chunks usando IA.
"""
import logging
import time
import hashlib
from typing import List, Optional
from langchain_core.documents import Document

from .token_manager import TokenManager
from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class OptimizedChunkProcessor:
    """Procesador de chunks con optimización mediante LLM"""

    def __init__(
        self,
        max_tokens: int = 1000,
        target_tokens: int = 800,
        chunks_per_batch: int = 5,
        gemini_client: Optional[GeminiClient] = None,
        model_name: str = "gpt-3.5-turbo",
        custom_instructions: str = ""
    ):
        """
        Inicializa el procesador de chunks.

        Args:
            max_tokens: Límite máximo de tokens por chunk
            target_tokens: Tokens objetivo para chunks optimizados
            chunks_per_batch: Chunks a procesar por lote
            gemini_client: Cliente de Gemini para procesamiento (opcional)
            model_name: Modelo para cálculo de tokens
            custom_instructions: Instrucciones adicionales para el prompt de optimización
        """
        self.client = gemini_client
        self.chunks_per_batch = chunks_per_batch
        self.max_tokens = max_tokens
        self.target_tokens = target_tokens
        self.token_manager = TokenManager(model_name)
        self.custom_instructions = custom_instructions

        # Caché para evitar reprocesamiento
        self._merge_cache = {}
        self._enhance_cache = {}

    def _get_cache_key(self, text: str) -> str:
        """Genera una clave de caché para el texto"""
        combined = text + self.custom_instructions
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def should_merge_chunks(self, chunk1: str, chunk2: str) -> bool:
        """
        Determina si dos chunks deben unirse basándose en continuidad semántica.

        Args:
            chunk1: Primer chunk
            chunk2: Segundo chunk

        Returns:
            True si los chunks deben unirse
        """
        cache_key = f"{self._get_cache_key(chunk1)}_{self._get_cache_key(chunk2)}"
        if cache_key in self._merge_cache:
            return self._merge_cache[cache_key]

        try:
            combined_text = f"{chunk1}\n\n{chunk2}"
            combined_tokens = self.token_manager.count_tokens(combined_text)

            if combined_tokens > self.max_tokens:
                self._merge_cache[cache_key] = False
                return False

            if self.client:
                base_prompt = f"""Analiza estos dos fragmentos de texto y determina si deben unirse.

LÍMITES ESTRICTOS:
- Tokens combinados: {combined_tokens}/{self.max_tokens}
- Solo unir si hay continuidad semántica clara

Criterios de unión:
1. El primer fragmento termina abruptamente
2. El segundo fragmento continúa la misma idea/concepto
3. La unión mejora la coherencia del contenido
4. Exceder {self.max_tokens} tokens, SOLAMENTE si es necesario para mantener el contexto

Responde SOLO 'SI' o 'NO'.

Fragmento 1 ({self.token_manager.count_tokens(chunk1)} tokens):
{chunk1[:500]}...

Fragmento 2 ({self.token_manager.count_tokens(chunk2)} tokens):
{chunk2[:500]}..."""

                response = self.client.generate_content(base_prompt)
                result = response.strip().upper() == 'SI'
                self._merge_cache[cache_key] = result
                return result

            # Heurística simple si no hay cliente LLM
            result = (
                chunk1.rstrip().endswith(('.', '!', '?')) == False and
                combined_tokens <= self.target_tokens
            )
            self._merge_cache[cache_key] = result
            return result

        except Exception as e:
            logger.error(f"Error analizando chunks para merge: {e}")
            self._merge_cache[cache_key] = False
            return False

    def enhance_chunk(self, chunk_text: str) -> str:
        """
        Mejora un chunk usando LLM o truncamiento.

        Args:
            chunk_text: Texto del chunk a mejorar

        Returns:
            Texto del chunk mejorado
        """
        cache_key = self._get_cache_key(chunk_text)
        if cache_key in self._enhance_cache:
            return self._enhance_cache[cache_key]

        current_tokens = self.token_manager.count_tokens(chunk_text)

        try:
            if self.client and current_tokens < self.max_tokens:
                base_prompt = f"""Optimiza este texto siguiendo estas reglas ESTRICTAS:

LÍMITES DE TOKENS:
- Actual: {current_tokens} tokens
- Máximo permitido: {self.max_tokens} tokens
- Objetivo: {self.target_tokens} tokens

REGLAS FUNDAMENTALES:
NO exceder {self.max_tokens} tokens bajo ninguna circunstancia
Mantener TODA la información esencial y metadatos
NO cambiar términos técnicos o palabras clave
Asegurar oraciones completas y coherentes
Optimizar claridad y estructura sin añadir contenido
SOLO devuelve el texto no agregues conclusiones NUNCA

Si el texto está cerca del límite, NO expandir. Solo mejorar estructura."""

                if self.custom_instructions.strip():
                    base_prompt += f"\n\nINSTRUCCIONES ADICIONALES:\n{self.custom_instructions}"

                base_prompt += f"\n\nTexto a optimizar:\n{chunk_text}"

                response = self.client.generate_content(base_prompt)
                enhanced_text = response.strip()

                enhanced_tokens = self.token_manager.count_tokens(enhanced_text)
                if enhanced_tokens > self.max_tokens:
                    logger.warning(
                        f"Texto optimizado excede límite ({enhanced_tokens} > {self.max_tokens}), truncando"
                    )
                    enhanced_text = self.token_manager.truncate_to_tokens(enhanced_text, self.max_tokens)

                self._enhance_cache[cache_key] = enhanced_text
                return enhanced_text
            else:
                # Sin LLM o ya en límite, solo truncar si es necesario
                if current_tokens > self.max_tokens:
                    truncated = self.token_manager.truncate_to_tokens(chunk_text, self.max_tokens)
                    self._enhance_cache[cache_key] = truncated
                    return truncated

                self._enhance_cache[cache_key] = chunk_text
                return chunk_text

        except Exception as e:
            logger.error(f"Error procesando chunk: {e}")
            if current_tokens > self.max_tokens:
                truncated = self.token_manager.truncate_to_tokens(chunk_text, self.max_tokens)
                self._enhance_cache[cache_key] = truncated
                return truncated

            self._enhance_cache[cache_key] = chunk_text
            return chunk_text

    def process_chunks_batch(
        self,
        chunks: List[Document],
        merge_related: bool = False
    ) -> List[Document]:
        """
        Procesa un lote de chunks, aplicando merge y mejoras.

        Args:
            chunks: Lista de documentos a procesar
            merge_related: Si True, intenta unir chunks relacionados

        Returns:
            Lista de documentos procesados
        """
        processed_chunks = []
        total_chunks = len(chunks)

        logger.info(f"Procesando {total_chunks} chunks en lotes de {self.chunks_per_batch}")
        if self.custom_instructions:
            logger.info(f"Con instrucciones personalizadas: {self.custom_instructions[:100]}...")

        i = 0
        while i < len(chunks):
            batch_start = time.time()
            current_chunk = chunks[i]
            merged_content = current_chunk.page_content
            original_tokens = self.token_manager.count_tokens(merged_content)

            # Intentar merge si está habilitado
            if merge_related and i < len(chunks) - 1:
                merge_count = 0
                while (
                    i + merge_count < len(chunks) - 1 and
                    self.should_merge_chunks(
                        merged_content,
                        chunks[i + merge_count + 1].page_content
                    )
                ):
                    merge_count += 1
                    merged_content += "\n\n" + chunks[i + merge_count].page_content
                    logger.info(f"  Uniendo chunk {i + 1} con chunk {i + merge_count + 1}")

                i += merge_count

            logger.info(f"\nProcesando chunk {i + 1}/{total_chunks}")
            logger.info(f"  Tokens originales: {original_tokens}")

            # Mejorar chunk
            enhanced_content = self.enhance_chunk(merged_content)
            final_tokens = self.token_manager.count_tokens(enhanced_content)

            processed_chunks.append(Document(
                page_content=enhanced_content,
                metadata={
                    **current_chunk.metadata,
                }
            ))

            logger.info(f"  Tokens finales: {final_tokens}")
            logger.info(f"  Tiempo de procesamiento: {time.time() - batch_start:.2f}s")

            i += 1

            if i % self.chunks_per_batch == 0 and i < len(chunks):
                logger.info(f"\nCompletados {i}/{total_chunks} chunks")
                time.sleep(0.1)

        return processed_chunks
