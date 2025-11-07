"""
Servicio de embeddings usando Azure OpenAI.
Genera embeddings para chunks de texto usando text-embedding-3-large (3072 dimensiones).
Incluye manejo de rate limits con retry exponencial y delays entre batches.
"""
import asyncio
import logging
from typing import List
from openai import AzureOpenAI, RateLimitError
from ..core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Servicio para generar embeddings usando Azure OpenAI"""

    def __init__(self):
        """Inicializa el cliente de Azure OpenAI"""
        try:
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            self.embedding_dimension = 3072
            logger.info(f"EmbeddingService inicializado con modelo {self.model}")
        except Exception as e:
            logger.error(f"Error inicializando EmbeddingService: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding para un texto individual.

        Args:
            text: Texto para generar embedding

        Returns:
            Vector de embedding (3072 dimensiones)

        Raises:
            Exception: Si hay error al generar el embedding
        """
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            embedding = response.data[0].embedding

            if len(embedding) != self.embedding_dimension:
                raise ValueError(
                    f"Dimensión incorrecta: esperada {self.embedding_dimension}, "
                    f"obtenida {len(embedding)}"
                )

            return embedding

        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            raise

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int | None = None,
        delay_between_batches: float | None = None,
        max_retries: int | None = None
    ) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos en lotes con manejo de rate limits.

        Args:
            texts: Lista de textos para generar embeddings
            batch_size: Tamaño del lote (None = usar configuración de settings)
            delay_between_batches: Segundos de espera entre batches (None = usar configuración)
            max_retries: Número máximo de reintentos (None = usar configuración)

        Returns:
            Lista de vectores de embeddings

        Raises:
            Exception: Si hay error al generar los embeddings después de todos los reintentos
        """
        # Usar configuración de settings si no se proporciona
        batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        delay_between_batches = delay_between_batches or settings.EMBEDDING_DELAY_BETWEEN_BATCHES
        max_retries = max_retries or settings.EMBEDDING_MAX_RETRIES

        try:
            embeddings = []
            total_batches = (len(texts) - 1) // batch_size + 1

            logger.info(f"Iniciando generación de embeddings: {len(texts)} textos en {total_batches} batches")
            logger.info(f"Configuración: batch_size={batch_size}, delay={delay_between_batches}s, max_retries={max_retries}")

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1

                logger.info(f"📊 Procesando batch {batch_num}/{total_batches} ({len(batch)} textos)...")

                # Retry con exponential backoff
                retry_count = 0
                while retry_count <= max_retries:
                    try:
                        response = self.client.embeddings.create(
                            input=batch,
                            model=self.model
                        )

                        batch_embeddings = [item.embedding for item in response.data]

                        # Validar dimensiones
                        for idx, emb in enumerate(batch_embeddings):
                            if len(emb) != self.embedding_dimension:
                                raise ValueError(
                                    f"Dimensión incorrecta en índice {i + idx}: "
                                    f"esperada {self.embedding_dimension}, obtenida {len(emb)}"
                                )

                        embeddings.extend(batch_embeddings)
                        logger.info(f"✓ Batch {batch_num}/{total_batches} completado exitosamente")
                        break  # Éxito, salir del retry loop

                    except RateLimitError as e:
                        retry_count += 1
                        if retry_count > max_retries:
                            logger.error(f"❌ Rate limit excedido después de {max_retries} reintentos")
                            raise

                        # Exponential backoff: 2^retry_count segundos
                        wait_time = 2 ** retry_count
                        logger.warning(
                            f"⚠️  Rate limit alcanzado en batch {batch_num}/{total_batches}. "
                            f"Reintento {retry_count}/{max_retries} en {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)

                    except Exception as e:
                        logger.error(f"❌ Error en batch {batch_num}/{total_batches}: {e}")
                        raise

                # Delay entre batches para respetar rate limit (excepto en el último)
                if i + batch_size < len(texts):
                    await asyncio.sleep(delay_between_batches)

            logger.info(f"✅ Embeddings generados exitosamente: {len(embeddings)} vectores de {self.embedding_dimension}D")
            return embeddings

        except Exception as e:
            logger.error(f"Error generando embeddings en lote: {e}")
            raise


# Instancia global singleton
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """
    Obtiene la instancia singleton del servicio de embeddings.

    Returns:
        Instancia de EmbeddingService
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
