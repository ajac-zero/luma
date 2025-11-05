"""
Gestor de tokens para contar y truncar texto basado en modelos de tokenización.
"""
import logging
import tiktoken

logger = logging.getLogger(__name__)


class TokenManager:
    """Gestor para contar y truncar tokens usando tiktoken"""

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Inicializa el gestor de tokens.

        Args:
            model_name: Nombre del modelo para la codificación de tokens
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            logger.warning(
                f"Modelo {model_name} no encontrado, usando codificación por defecto cl100k_base"
            )
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        Cuenta el número de tokens en un texto.

        Args:
            text: Texto a analizar

        Returns:
            Número de tokens
        """
        return len(self.encoding.encode(text))

    def truncate_to_tokens(
        self,
        text: str,
        max_tokens: int,
        preserve_sentences: bool = True
    ) -> str:
        """
        Trunca texto a un número máximo de tokens.

        Args:
            text: Texto a truncar
            max_tokens: Número máximo de tokens
            preserve_sentences: Si True, intenta mantener oraciones completas

        Returns:
            Texto truncado
        """
        tokens = self.encoding.encode(text)

        if len(tokens) <= max_tokens:
            return text

        truncated_tokens = tokens[:max_tokens]
        truncated_text = self.encoding.decode(truncated_tokens)

        if preserve_sentences:
            # Intentar cortar en el último punto
            last_period = truncated_text.rfind('.')
            # Solo cortar si el punto está en el último 30% del texto
            if last_period > len(truncated_text) * 0.7:
                return truncated_text[:last_period + 1]

        return truncated_text
