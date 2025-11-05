"""
Servicio de embeddings usando Azure OpenAI.
Genera embeddings para chunks de texto usando text-embedding-3-large (3072 dimensiones).
"""
import logging
from typing import List
from openai import AzureOpenAI
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
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos en lotes.

        Args:
            texts: Lista de textos para generar embeddings
            batch_size: Tamaño del lote para procesamiento (default: 100)

        Returns:
            Lista de vectores de embeddings

        Raises:
            Exception: Si hay error al generar los embeddings
        """
        try:
            embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.info(f"Procesando lote {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

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

            logger.info(f"Generados {len(embeddings)} embeddings exitosamente")
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
