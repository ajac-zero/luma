"""
Servicio de lógica de negocio para operaciones con bases de datos vectoriales.

Este módulo contiene toda la lógica de negocio relacionada con la gestión
de colecciones y chunks en bases de datos vectoriales.
"""

import logging
from typing import List, Dict, Any, Optional

from app.vector_db import get_vector_db
from app.models.vector_models import (
    CollectionCreateRequest,
    CollectionCreateResponse,
    CollectionDeleteResponse,
    CollectionExistsResponse,
    CollectionInfoResponse,
    FileExistsInCollectionResponse,
    GetChunksByFileResponse,
    DeleteFileFromCollectionResponse,
    AddChunksResponse,
    VectorDBHealthResponse,
    VectorDBErrorResponse
)

logger = logging.getLogger(__name__)


class VectorService:
    """
    Servicio para gestionar operaciones con bases de datos vectoriales.

    Este servicio actúa como una capa intermedia entre los routers y
    la implementación de la base de datos vectorial.
    """

    def __init__(self):
        """Inicializa el servicio con la instancia de la base de datos vectorial."""
        self.vector_db = get_vector_db()

    async def check_collection_exists(self, collection_name: str) -> CollectionExistsResponse:
        """
        Verifica si una colección existe.

        Args:
            collection_name: Nombre de la colección

        Returns:
            CollectionExistsResponse: Response con el resultado
        """
        try:
            exists = await self.vector_db.collection_exists(collection_name)
            logger.info(f"Verificación de colección '{collection_name}': {exists}")

            return CollectionExistsResponse(
                exists=exists,
                collection_name=collection_name
            )

        except Exception as e:
            logger.error(f"Error al verificar colección '{collection_name}': {e}")
            raise

    async def create_collection(
        self,
        request: CollectionCreateRequest
    ) -> CollectionCreateResponse:
        """
        Crea una nueva colección.

        Args:
            request: Request con los datos de la colección

        Returns:
            CollectionCreateResponse: Response con el resultado

        Raises:
            ValueError: Si la colección ya existe
        """
        try:
            # Verificar si ya existe
            exists = await self.vector_db.collection_exists(request.collection_name)

            if exists:
                logger.warning(f"Intento de crear colección existente: '{request.collection_name}'")
                raise ValueError(f"La colección '{request.collection_name}' ya existe")

            # Crear la colección
            success = await self.vector_db.create_collection(
                collection_name=request.collection_name,
                vector_size=request.vector_size,
                distance=request.distance
            )

            if success:
                logger.info(f"Colección '{request.collection_name}' creada exitosamente")
                return CollectionCreateResponse(
                    success=True,
                    collection_name=request.collection_name,
                    message=f"Colección '{request.collection_name}' creada exitosamente"
                )
            else:
                logger.error(f"Fallo al crear colección '{request.collection_name}'")
                raise Exception(f"No se pudo crear la colección '{request.collection_name}'")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error al crear colección '{request.collection_name}': {e}")
            raise

    async def delete_collection(self, collection_name: str) -> CollectionDeleteResponse:
        """
        Elimina una colección completa.

        Args:
            collection_name: Nombre de la colección

        Returns:
            CollectionDeleteResponse: Response con el resultado

        Raises:
            ValueError: Si la colección no existe
        """
        try:
            # Verificar que existe
            exists = await self.vector_db.collection_exists(collection_name)

            if not exists:
                logger.warning(f"Intento de eliminar colección inexistente: '{collection_name}'")
                raise ValueError(f"La colección '{collection_name}' no existe")

            # Eliminar la colección
            success = await self.vector_db.delete_collection(collection_name)

            if success:
                logger.info(f"Colección '{collection_name}' eliminada exitosamente")
                return CollectionDeleteResponse(
                    success=True,
                    collection_name=collection_name,
                    message=f"Colección '{collection_name}' eliminada exitosamente"
                )
            else:
                logger.error(f"Fallo al eliminar colección '{collection_name}'")
                raise Exception(f"No se pudo eliminar la colección '{collection_name}'")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error al eliminar colección '{collection_name}': {e}")
            raise

    async def get_collection_info(self, collection_name: str) -> Optional[CollectionInfoResponse]:
        """
        Obtiene información de una colección.

        Args:
            collection_name: Nombre de la colección

        Returns:
            Optional[CollectionInfoResponse]: Información de la colección o None
        """
        try:
            info = await self.vector_db.get_collection_info(collection_name)

            if info is None:
                logger.warning(f"Colección '{collection_name}' no encontrada")
                return None

            return CollectionInfoResponse(**info)

        except Exception as e:
            logger.error(f"Error al obtener info de colección '{collection_name}': {e}")
            raise

    async def check_file_exists_in_collection(
        self,
        collection_name: str,
        file_name: str
    ) -> FileExistsInCollectionResponse:
        """
        Verifica si un archivo existe en una colección.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo

        Returns:
            FileExistsInCollectionResponse: Response con el resultado
        """
        try:
            # Primero verificar que la colección existe
            collection_exists = await self.vector_db.collection_exists(collection_name)

            if not collection_exists:
                logger.warning(f"Colección '{collection_name}' no existe")
                return FileExistsInCollectionResponse(
                    exists=False,
                    collection_name=collection_name,
                    file_name=file_name,
                    chunk_count=0
                )

            # Verificar si el archivo existe
            file_exists = await self.vector_db.file_exists_in_collection(
                collection_name,
                file_name
            )

            chunk_count = None
            if file_exists:
                chunk_count = await self.vector_db.count_chunks_in_file(
                    collection_name,
                    file_name
                )

            logger.info(
                f"Archivo '{file_name}' en colección '{collection_name}': "
                f"existe={file_exists}, chunks={chunk_count}"
            )

            return FileExistsInCollectionResponse(
                exists=file_exists,
                collection_name=collection_name,
                file_name=file_name,
                chunk_count=chunk_count
            )

        except Exception as e:
            logger.error(
                f"Error al verificar archivo '{file_name}' "
                f"en colección '{collection_name}': {e}"
            )
            raise

    async def get_chunks_by_file(
        self,
        collection_name: str,
        file_name: str,
        limit: Optional[int] = None
    ) -> GetChunksByFileResponse:
        """
        Obtiene todos los chunks de un archivo.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo
            limit: Límite opcional de chunks

        Returns:
            GetChunksByFileResponse: Response con los chunks

        Raises:
            ValueError: Si la colección no existe
        """
        try:
            # Verificar que la colección existe
            exists = await self.vector_db.collection_exists(collection_name)

            if not exists:
                logger.warning(f"Colección '{collection_name}' no existe")
                raise ValueError(f"La colección '{collection_name}' no existe")

            # Obtener chunks
            chunks = await self.vector_db.get_chunks_by_file(
                collection_name,
                file_name,
                limit
            )

            logger.info(
                f"Obtenidos {len(chunks)} chunks del archivo '{file_name}' "
                f"de la colección '{collection_name}'"
            )

            return GetChunksByFileResponse(
                collection_name=collection_name,
                file_name=file_name,
                chunks=chunks,
                total_chunks=len(chunks)
            )

        except ValueError:
            raise
        except Exception as e:
            logger.error(
                f"Error al obtener chunks del archivo '{file_name}' "
                f"de la colección '{collection_name}': {e}"
            )
            raise

    async def delete_file_from_collection(
        self,
        collection_name: str,
        file_name: str
    ) -> DeleteFileFromCollectionResponse:
        """
        Elimina todos los chunks de un archivo de una colección.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo

        Returns:
            DeleteFileFromCollectionResponse: Response con el resultado

        Raises:
            ValueError: Si la colección no existe o el archivo no está en la colección
        """
        try:
            # Verificar que la colección existe
            collection_exists = await self.vector_db.collection_exists(collection_name)

            if not collection_exists:
                logger.warning(f"Colección '{collection_name}' no existe")
                raise ValueError(f"La colección '{collection_name}' no existe")

            # Verificar que el archivo existe en la colección
            file_exists = await self.vector_db.file_exists_in_collection(
                collection_name,
                file_name
            )

            if not file_exists:
                logger.warning(
                    f"Archivo '{file_name}' no existe en colección '{collection_name}'"
                )
                raise ValueError(
                    f"El archivo '{file_name}' no existe en la colección '{collection_name}'"
                )

            # Eliminar el archivo
            chunks_deleted = await self.vector_db.delete_file_from_collection(
                collection_name,
                file_name
            )

            logger.info(
                f"Eliminados {chunks_deleted} chunks del archivo '{file_name}' "
                f"de la colección '{collection_name}'"
            )

            return DeleteFileFromCollectionResponse(
                success=True,
                collection_name=collection_name,
                file_name=file_name,
                chunks_deleted=chunks_deleted,
                message=f"Archivo '{file_name}' eliminado exitosamente ({chunks_deleted} chunks)"
            )

        except ValueError:
            raise
        except Exception as e:
            logger.error(
                f"Error al eliminar archivo '{file_name}' "
                f"de la colección '{collection_name}': {e}"
            )
            raise

    async def add_chunks(
        self,
        collection_name: str,
        chunks: List[Dict[str, Any]]
    ) -> AddChunksResponse:
        """
        Agrega chunks a una colección.

        Args:
            collection_name: Nombre de la colección
            chunks: Lista de chunks a agregar

        Returns:
            AddChunksResponse: Response con el resultado

        Raises:
            ValueError: Si la colección no existe
        """
        try:
            # Verificar que la colección existe
            exists = await self.vector_db.collection_exists(collection_name)

            if not exists:
                logger.warning(f"Colección '{collection_name}' no existe")
                raise ValueError(f"La colección '{collection_name}' no existe")

            # Agregar chunks
            success = await self.vector_db.add_chunks(collection_name, chunks)

            if success:
                logger.info(
                    f"Agregados {len(chunks)} chunks a la colección '{collection_name}'"
                )
                return AddChunksResponse(
                    success=True,
                    collection_name=collection_name,
                    chunks_added=len(chunks),
                    message=f"Se agregaron {len(chunks)} chunks exitosamente"
                )
            else:
                logger.error(f"Fallo al agregar chunks a '{collection_name}'")
                raise Exception(f"No se pudieron agregar los chunks a '{collection_name}'")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error al agregar chunks a '{collection_name}': {e}")
            raise

    async def health_check(self) -> VectorDBHealthResponse:
        """
        Verifica el estado de la conexión con la base de datos vectorial.

        Returns:
            VectorDBHealthResponse: Response con el estado
        """
        try:
            is_healthy = await self.vector_db.health_check()

            if is_healthy:
                return VectorDBHealthResponse(
                    status="healthy",
                    db_type="qdrant",
                    message="Conexión exitosa con la base de datos vectorial"
                )
            else:
                return VectorDBHealthResponse(
                    status="unhealthy",
                    db_type="qdrant",
                    message="No se pudo conectar con la base de datos vectorial"
                )

        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return VectorDBHealthResponse(
                status="error",
                db_type="qdrant",
                message=f"Error al verificar conexión: {str(e)}"
            )


# Instancia global del servicio
vector_service = VectorService()
