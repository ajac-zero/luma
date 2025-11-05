"""
Cliente para interactuar con Gemini (Google Vertex AI).
Usado para procesamiento inteligente de chunks con LLM.
"""
import logging
import os
import google.oauth2.service_account as sa
import vertexai.generative_models as gm
import vertexai
from ...core.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Cliente para generar contenido usando Gemini via Vertex AI"""

    def __init__(
        self,
        account_file: str | None = None,
        project: str | None = None,
        model: str | None = None
    ) -> None:
        """
        Inicializa el cliente de Gemini.

        Args:
            account_file: Ruta al archivo de credenciales de servicio (default: desde settings)
            project: ID del proyecto de Google Cloud (default: desde settings)
            model: Modelo de Gemini a usar (default: desde settings)
        """
        # Usar configuración de settings si no se proporciona
        account_file = account_file or settings.GOOGLE_APPLICATION_CREDENTIALS
        project = project or settings.GOOGLE_CLOUD_PROJECT
        model = model or settings.GEMINI_MODEL

        try:
            # Cargar credenciales desde archivo
            credentials = sa.Credentials.from_service_account_file(account_file)

            # Inicializar Vertex AI
            vertexai.init(
                project=project,
                credentials=credentials,
                location=settings.GOOGLE_CLOUD_LOCATION
            )

            # Inicializar modelo
            self.model = gm.GenerativeModel(model)
            logger.info(f"GeminiClient inicializado con modelo {model}")

        except Exception as e:
            logger.error(f"Error inicializando GeminiClient: {e}")
            raise

    def generate_content(self, prompt: str) -> str:
        """
        Genera contenido usando Gemini.

        Args:
            prompt: Prompt para el modelo

        Returns:
            Texto generado por el modelo

        Raises:
            Exception: Si hay error en la generación
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            return ""


# Instancia global singleton
_gemini_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    """
    Obtiene la instancia singleton del cliente de Gemini.

    Returns:
        Instancia de GeminiClient
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
