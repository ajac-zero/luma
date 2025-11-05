"""
Implementación de Qdrant para la interfaz VectorDBBase.

Este módulo proporciona la implementación concreta de todas las operaciones
vectoriales utilizando Qdrant como base de datos.
"""

import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from qdrant_client.http.exceptions import UnexpectedResponse

from .base import VectorDBBase

logger = logging.getLogger(__name__)


class QdrantVectorDB(VectorDBBase):
    """
    Implementación de VectorDBBase usando Qdrant como proveedor.

    Atributos:
        client: Cliente de Qdrant
        url: URL del servidor Qdrant
        api_key: API key para autenticación
    """

    def __init__(self, url: str, api_key: str):
        """
        Inicializa el cliente de Qdrant.

        Args:
            url: URL del servidor Qdrant
            api_key: API key para autenticación
        """
        self.url = url
        self.api_key = api_key
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=30
        )
        logger.info(f"QdrantVectorDB inicializado con URL: {url}")

    async def collection_exists(self, collection_name: str) -> bool:
        """
        Verifica si existe una colección en Qdrant.

        Args:
            collection_name: Nombre de la colección

        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            collections = self.client.get_collections().collections
            return any(col.name == collection_name for col in collections)
        except Exception as e:
            logger.error(f"Error al verificar colección '{collection_name}': {e}")
            return False

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int = 3072,
        distance: str = "Cosine"
    ) -> bool:
        """
        Crea una nueva colección en Qdrant.

        Args:
            collection_name: Nombre de la colección
            vector_size: Dimensión de los vectores (default: 3072)
            distance: Métrica de distancia

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            # Mapear string a enum de Qdrant
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclid": Distance.EUCLID,
                "Dot": Distance.DOT
            }

            distance_metric = distance_map.get(distance, Distance.COSINE)

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_metric
                )
            )

            logger.info(f"Colección '{collection_name}' creada exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error al crear colección '{collection_name}': {e}")
            return False

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Elimina una colección completa de Qdrant.

        Args:
            collection_name: Nombre de la colección

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Colección '{collection_name}' eliminada exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar colección '{collection_name}': {e}")
            return False

    async def file_exists_in_collection(
        self,
        collection_name: str,
        file_name: str
    ) -> bool:
        """
        Verifica si un archivo existe en una colección.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo

        Returns:
            bool: True si el archivo existe
        """
        try:
            # Buscar un solo punto con el file_name en metadata
            result = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.file_name",
                            match=MatchValue(value=file_name)
                        )
                    ]
                ),
                limit=1
            )

            return len(result[0]) > 0

        except Exception as e:
            logger.error(f"Error al verificar archivo '{file_name}' en colección '{collection_name}': {e}")
            return False

    async def get_chunks_by_file(
        self,
        collection_name: str,
        file_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los chunks de un archivo.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo
            limit: Límite opcional de resultados

        Returns:
            List[Dict]: Lista de chunks con metadata
        """
        try:
            chunks = []
            offset = None

            while True:
                result = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="metadata.file_name",
                                match=MatchValue(value=file_name)
                            )
                        ]
                    ),
                    limit=limit if limit else 100,
                    offset=offset
                )

                points, next_offset = result

                for point in points:
                    chunks.append({
                        "id": str(point.id),
                        "payload": point.payload,
                        "vector": point.vector if hasattr(point, 'vector') else None
                    })

                # Si hay límite y lo alcanzamos, salimos
                if limit and len(chunks) >= limit:
                    break

                # Si no hay más resultados, salimos
                if next_offset is None:
                    break

                offset = next_offset

            logger.info(f"Obtenidos {len(chunks)} chunks del archivo '{file_name}'")
            return chunks

        except Exception as e:
            logger.error(f"Error al obtener chunks del archivo '{file_name}': {e}")
            return []

    async def delete_file_from_collection(
        self,
        collection_name: str,
        file_name: str
    ) -> int:
        """
        Elimina todos los chunks de un archivo.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo

        Returns:
            int: Número de chunks eliminados
        """
        try:
            # Primero obtener todos los IDs del archivo
            chunks = await self.get_chunks_by_file(collection_name, file_name)

            if not chunks:
                logger.info(f"No se encontraron chunks para el archivo '{file_name}'")
                return 0

            # Extraer los IDs
            point_ids = [chunk["id"] for chunk in chunks]

            # Eliminar por IDs
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids
            )

            logger.info(f"Eliminados {len(point_ids)} chunks del archivo '{file_name}'")
            return len(point_ids)

        except Exception as e:
            logger.error(f"Error al eliminar archivo '{file_name}': {e}")
            return 0

    async def add_chunks(
        self,
        collection_name: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Agrega múltiples chunks a una colección.

        Args:
            collection_name: Nombre de la colección
            chunks: Lista de chunks con estructura:
                {
                    "id": str,
                    "vector": List[float],
                    "payload": {
                        "page_content": str,
                        "metadata": {
                            "file_name": str,
                            "page": int
                        }
                    }
                }

        Returns:
            Dict con 'success' (bool) y 'chunks_added' (int)
        """
        try:
            points = []

            for chunk in chunks:
                point = PointStruct(
                    id=chunk["id"],
                    vector=chunk["vector"],
                    payload=chunk["payload"]
                )
                points.append(point)

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )

            logger.info(f"Agregados {len(points)} chunks a la colección '{collection_name}'")
            return {
                "success": True,
                "chunks_added": len(points)
            }

        except Exception as e:
            logger.error(f"Error al agregar chunks a '{collection_name}': {e}")
            return {
                "success": False,
                "chunks_added": 0
            }

    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información sobre una colección.

        Args:
            collection_name: Nombre de la colección

        Returns:
            Optional[Dict]: Información de la colección o None
        """
        try:
            collection_info = self.client.get_collection(collection_name=collection_name)

            return {
                "name": collection_name,
                "vectors_count": collection_info.points_count,
                "vectors_config": {
                    "size": collection_info.config.params.vectors.size,
                    "distance": collection_info.config.params.vectors.distance.name
                },
                "status": collection_info.status.name
            }

        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.warning(f"Colección '{collection_name}' no encontrada")
                return None
            logger.error(f"Error al obtener info de colección '{collection_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener info de colección '{collection_name}': {e}")
            return None

    async def count_chunks_in_file(
        self,
        collection_name: str,
        file_name: str
    ) -> int:
        """
        Cuenta el número de chunks de un archivo.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo

        Returns:
            int: Número de chunks
        """
        try:
            result = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="file_name",
                            match=MatchValue(value=file_name)
                        )
                    ]
                ),
                limit=1,
                with_payload=False,
                with_vectors=False
            )

            # Qdrant scroll no retorna count directo, así que obtenemos todos
            chunks = await self.get_chunks_by_file(collection_name, file_name)
            count = len(chunks)

            logger.info(f"Archivo '{file_name}' tiene {count} chunks")
            return count

        except Exception as e:
            logger.error(f"Error al contar chunks del archivo '{file_name}': {e}")
            return 0

    async def health_check(self) -> bool:
        """
        Verifica la conexión con Qdrant.

        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            self.client.get_collections()
            logger.info("Health check de Qdrant exitoso")
            return True
        except Exception as e:
            logger.error(f"Health check de Qdrant falló: {e}")
            return False
