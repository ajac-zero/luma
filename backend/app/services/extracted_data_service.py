"""
Servicio para manejar el almacenamiento de datos extraídos en Redis.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..models.extracted_data import ExtractedDocument

logger = logging.getLogger(__name__)


class ExtractedDataService:
    """Servicio para guardar y recuperar datos extraídos de documentos"""

    async def save_extracted_data(
        self,
        file_name: str,
        tema: str,
        collection_name: str,
        extracted_data: Dict[str, Any]
    ) -> ExtractedDocument:
        """
        Guarda datos extraídos de un documento en Redis.

        Args:
            file_name: Nombre del archivo
            tema: Tema del documento
            collection_name: Colección de Qdrant
            extracted_data: Datos extraídos (dict)

        Returns:
            ExtractedDocument guardado
        """
        try:
            # Crear instancia del modelo
            doc = ExtractedDocument(
                file_name=file_name,
                tema=tema,
                collection_name=collection_name,
                extracted_data_json="",  # Se setea después
                extraction_timestamp=datetime.utcnow().isoformat()
            )

            # Serializar datos extraídos
            doc.set_extracted_data(extracted_data)

            # Guardar en Redis
            doc.save()

            logger.info(
                f"💾 Datos extraídos guardados en Redis: {file_name} "
                f"({len(extracted_data)} campos)"
            )

            return doc

        except Exception as e:
            logger.error(f"Error guardando datos extraídos en Redis: {e}")
            raise

    async def get_by_file(self, file_name: str) -> List[ExtractedDocument]:
        """
        Obtiene todos los documentos extraídos de un archivo.

        Args:
            file_name: Nombre del archivo

        Returns:
            Lista de ExtractedDocument
        """
        try:
            docs = ExtractedDocument.find_by_file(file_name)
            logger.info(f"Encontrados {len(docs)} documentos extraídos para {file_name}")
            return docs
        except Exception as e:
            logger.error(f"Error buscando documentos por archivo: {e}")
            return []

    async def get_by_tema(self, tema: str) -> List[ExtractedDocument]:
        """
        Obtiene todos los documentos extraídos de un tema.

        Args:
            tema: Tema a buscar

        Returns:
            Lista de ExtractedDocument
        """
        try:
            docs = ExtractedDocument.find_by_tema(tema)
            logger.info(f"Encontrados {len(docs)} documentos extraídos para tema {tema}")
            return docs
        except Exception as e:
            logger.error(f"Error buscando documentos por tema: {e}")
            return []

    async def get_by_collection(self, collection_name: str) -> List[ExtractedDocument]:
        """
        Obtiene todos los documentos de una colección.

        Args:
            collection_name: Nombre de la colección

        Returns:
            Lista de ExtractedDocument
        """
        try:
            docs = ExtractedDocument.find_by_collection(collection_name)
            logger.info(f"Encontrados {len(docs)} documentos en colección {collection_name}")
            return docs
        except Exception as e:
            logger.error(f"Error buscando documentos por colección: {e}")
            return []


# Instancia global singleton
_extracted_data_service: Optional[ExtractedDataService] = None


def get_extracted_data_service() -> ExtractedDataService:
    """
    Obtiene la instancia singleton del servicio.

    Returns:
        Instancia de ExtractedDataService
    """
    global _extracted_data_service
    if _extracted_data_service is None:
        _extracted_data_service = ExtractedDataService()
    return _extracted_data_service
