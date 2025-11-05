"""
Clase abstracta base para operaciones con bases de datos vectoriales.

Este módulo define la interfaz que todas las implementaciones de bases de datos
vectoriales deben seguir, permitiendo cambiar fácilmente entre diferentes proveedores.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class VectorDBBase(ABC):
    """
    Clase abstracta que define las operaciones básicas para una base de datos vectorial.

    Esta interfaz permite implementar el patrón Repository/Strategy para
    abstraer la lógica de acceso a datos vectoriales.
    """

    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """
        Verifica si existe una colección con el nombre especificado.

        Args:
            collection_name: Nombre de la colección a verificar

        Returns:
            bool: True si la colección existe, False en caso contrario
        """
        pass

    @abstractmethod
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int = 3072,
        distance: str = "Cosine"
    ) -> bool:
        """
        Crea una nueva colección en la base de datos vectorial.

        Args:
            collection_name: Nombre de la colección a crear
            vector_size: Dimensión de los vectores (por defecto 3072)
            distance: Métrica de distancia ("Cosine", "Euclid", "Dot")

        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        pass

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """
        Elimina una colección completa.

        Args:
            collection_name: Nombre de la colección a eliminar

        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        pass

    @abstractmethod
    async def file_exists_in_collection(
        self,
        collection_name: str,
        file_name: str
    ) -> bool:
        """
        Verifica si un archivo ya existe en una colección.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo a buscar

        Returns:
            bool: True si el archivo existe, False en caso contrario
        """
        pass

    @abstractmethod
    async def get_chunks_by_file(
        self,
        collection_name: str,
        file_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los chunks de un archivo específico.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo
            limit: Límite opcional de resultados

        Returns:
            List[Dict]: Lista de chunks con su metadata
        """
        pass

    @abstractmethod
    async def delete_file_from_collection(
        self,
        collection_name: str,
        file_name: str
    ) -> int:
        """
        Elimina todos los chunks de un archivo de una colección.

        Args:
            collection_name: Nombre de la colección
            file_name: Nombre del archivo a eliminar

        Returns:
            int: Número de chunks eliminados
        """
        pass

    @abstractmethod
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
                        "text": str,
                        "file_name": str,
                        "page": int,
                        ...otros campos opcionales
                    }
                }

        Returns:
            Dict con 'success' (bool) y 'chunks_added' (int)
        """
        pass

    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información sobre una colección.

        Args:
            collection_name: Nombre de la colección

        Returns:
            Optional[Dict]: Información de la colección o None si no existe
        """
        pass

    @abstractmethod
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
            int: Número de chunks del archivo
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verifica que la conexión con la base de datos vectorial esté funcionando.

        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        pass
