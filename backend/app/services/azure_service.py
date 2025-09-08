from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from typing import List, Optional, BinaryIO
import logging
from datetime import datetime, timezone
import os
from ..core.config import settings

logger = logging.getLogger(__name__)


class AzureBlobService:
    """
    Servicio para interactuar con Azure Blob Storage
    """
    
    def __init__(self):
        """Inicializar el cliente de Azure Blob Storage"""
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            self.container_name = settings.AZURE_CONTAINER_NAME
            logger.info(f"Cliente de Azure Blob Storage inicializado para container: {self.container_name}")
        except Exception as e:
            logger.error(f"Error inicializando Azure Blob Service: {e}")
            raise e
    
    async def create_container_if_not_exists(self) -> bool:
        """
        Crear el container si no existe
        Returns: True si se creó, False si ya existía
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.create_container()
            logger.info(f"Container '{self.container_name}' creado exitosamente")
            return True
        except ResourceExistsError:
            logger.info(f"Container '{self.container_name}' ya existe")
            return False
        except Exception as e:
            logger.error(f"Error creando container: {e}")
            raise e
    
    async def upload_file(self, file_data: BinaryIO, blob_name: str, tema: str = "") -> dict:
        """
        Subir un archivo a Azure Blob Storage
        
        Args:
            file_data: Datos del archivo
            blob_name: Nombre del archivo en el blob
            tema: Tema/carpeta donde guardar el archivo
        
        Returns:
            dict: Información del archivo subido
        """
        try:
            # Construir la ruta completa con tema si se proporciona
            full_blob_name = f"{tema}/{blob_name}" if tema else blob_name
            
            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=full_blob_name
            )
            
            # Subir el archivo
            blob_client.upload_blob(file_data, overwrite=True)
            
            # Obtener propiedades del blob
            blob_properties = blob_client.get_blob_properties()
            
            logger.info(f"Archivo '{full_blob_name}' subido exitosamente")
            
            return {
                "name": blob_name,
                "full_path": full_blob_name,
                "tema": tema,
                "size": blob_properties.size,
                "last_modified": blob_properties.last_modified,
                "url": blob_client.url
            }
            
        except Exception as e:
            logger.error(f"Error subiendo archivo '{blob_name}': {e}")
            raise e
    
    async def download_file(self, blob_name: str, tema: str = "") -> bytes:
        """
        Descargar un archivo de Azure Blob Storage
        
        Args:
            blob_name: Nombre del archivo
            tema: Tema/carpeta donde está el archivo
        
        Returns:
            bytes: Contenido del archivo
        """
        try:
            # Construir la ruta completa
            full_blob_name = f"{tema}/{blob_name}" if tema else blob_name
            
            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=full_blob_name
            )
            
            # Descargar el archivo
            blob_data = blob_client.download_blob()
            content = blob_data.readall()
            
            logger.info(f"Archivo '{full_blob_name}' descargado exitosamente")
            return content
            
        except ResourceNotFoundError:
            logger.error(f"Archivo '{full_blob_name}' no encontrado")
            raise FileNotFoundError(f"El archivo '{blob_name}' no existe")
        except Exception as e:
            logger.error(f"Error descargando archivo '{blob_name}': {e}")
            raise e
    
    async def delete_file(self, blob_name: str, tema: str = "") -> bool:
        """
        Eliminar un archivo de Azure Blob Storage
        
        Args:
            blob_name: Nombre del archivo
            tema: Tema/carpeta donde está el archivo
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            # Construir la ruta completa
            full_blob_name = f"{tema}/{blob_name}" if tema else blob_name
            
            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=full_blob_name
            )
            
            # Eliminar el archivo
            blob_client.delete_blob()
            
            logger.info(f"Archivo '{full_blob_name}' eliminado exitosamente")
            return True
            
        except ResourceNotFoundError:
            logger.error(f"Archivo '{full_blob_name}' no encontrado para eliminar")
            raise FileNotFoundError(f"El archivo '{blob_name}' no existe")
        except Exception as e:
            logger.error(f"Error eliminando archivo '{blob_name}': {e}")
            raise e
    
    async def list_files(self, tema: str = "") -> List[dict]:
        """
        Listar archivos en el container o en un tema específico
        
        Args:
            tema: Tema/carpeta específica (opcional)
        
        Returns:
            List[dict]: Lista de archivos con sus propiedades
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Filtrar por tema si se proporciona
            name_starts_with = f"{tema}/" if tema else None
            
            blobs = container_client.list_blobs(name_starts_with=name_starts_with)
            
            files = []
            for blob in blobs:
                # Extraer información del blob
                blob_info = {
                    "name": os.path.basename(blob.name),
                    "full_path": blob.name,
                    "tema": os.path.dirname(blob.name) if "/" in blob.name else "",
                    "size": blob.size,
                    "last_modified": blob.last_modified,
                    "content_type": blob.content_settings.content_type if blob.content_settings else None
                }
                files.append(blob_info)
            
            logger.info(f"Listados {len(files)} archivos" + (f" en tema '{tema}'" if tema else ""))
            return files
            
        except Exception as e:
            logger.error(f"Error listando archivos: {e}")
            raise e
    
    async def get_file_info(self, blob_name: str, tema: str = "") -> dict:
        """
        Obtener información de un archivo específico
        
        Args:
            blob_name: Nombre del archivo
            tema: Tema/carpeta donde está el archivo
        
        Returns:
            dict: Información del archivo
        """
        try:
            # Construir la ruta completa
            full_blob_name = f"{tema}/{blob_name}" if tema else blob_name
            
            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=full_blob_name
            )
            
            # Obtener propiedades
            properties = blob_client.get_blob_properties()
            
            return {
                "name": blob_name,
                "full_path": full_blob_name,
                "tema": tema,
                "size": properties.size,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type,
                "url": blob_client.url
            }
            
        except ResourceNotFoundError:
            logger.error(f"Archivo '{full_blob_name}' no encontrado")
            raise FileNotFoundError(f"El archivo '{blob_name}' no existe")
        except Exception as e:
            logger.error(f"Error obteniendo info del archivo '{blob_name}': {e}")
            raise e
    
    async def get_download_url(self, blob_name: str, tema: str = "") -> str:
        """
        Obtener URL de descarga directa para un archivo
        
        Args:
            blob_name: Nombre del archivo
            tema: Tema/carpeta donde está el archivo
        
        Returns:
            str: URL de descarga
        """
        try:
            # Construir la ruta completa
            full_blob_name = f"{tema}/{blob_name}" if tema else blob_name
            
            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=full_blob_name
            )
            
            return blob_client.url
            
        except Exception as e:
            logger.error(f"Error obteniendo URL de descarga para '{blob_name}': {e}")
            raise e


# Instancia global del servicio
azure_service = AzureBlobService()