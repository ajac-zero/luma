import logging
import os
from datetime import datetime, timedelta, timezone
from typing import BinaryIO, List, Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import (
    BlobClient,
    BlobSasPermissions,
    BlobServiceClient,
    ContainerClient,
    generate_blob_sas,
)

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
            logger.info(
                f"Cliente de Azure Blob Storage inicializado para container: {self.container_name}"
            )

            # Configurar CORS automáticamente al inicializar
            self._configure_cors()
        except Exception as e:
            logger.error(f"Error inicializando Azure Blob Service: {e}")
            raise e

    def _configure_cors(self):
        """
        Configurar CORS en Azure Blob Storage para permitir acceso desde el frontend

        Esto es necesario para que el navegador pueda cargar PDFs directamente
        desde Azure usando las URLs SAS generadas.
        """
        try:
            from azure.storage.blob import CorsRule

            # Definir regla CORS permisiva para desarrollo y producción
            cors_rule = CorsRule(
                allowed_origins=["*"],  # En producción, especificar dominios exactos
                allowed_methods=["GET", "HEAD", "OPTIONS"],
                allowed_headers=["*"],
                exposed_headers=["*"],
                max_age_in_seconds=3600,
            )

            # Aplicar la configuración CORS
            self.blob_service_client.set_service_properties(cors=[cors_rule])
            logger.info("CORS configurado exitosamente en Azure Blob Storage")

        except Exception as e:
            # No fallar si CORS no se puede configurar (puede que ya esté configurado)
            logger.warning(f"No se pudo configurar CORS automáticamente: {e}")
            logger.warning(
                "Asegúrate de configurar CORS manualmente en Azure Portal si es necesario"
            )

    async def create_container_if_not_exists(self) -> bool:
        """
        Crear el container si no existe
        Returns: True si se creó, False si ya existía
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            container_client.create_container()
            logger.info(f"Container '{self.container_name}' creado exitosamente")
            return True
        except ResourceExistsError:
            logger.info(f"Container '{self.container_name}' ya existe")
            return False
        except Exception as e:
            logger.error(f"Error creando container: {e}")
            raise e

    async def upload_file(
        self, file_data: BinaryIO, blob_name: str, tema: str = ""
    ) -> dict:
        """
        Subir un archivo a Azure Blob Storage

        Args:
            file_data: Datos del archivo
            blob_name: Nombre del archivo en el blob
            tema: Tema/carpeta donde guardar el archivo (se normaliza a lowercase)

        Returns:
            dict: Información del archivo subido
        """
        try:
            # Normalizar tema a lowercase para consistencia
            tema_normalized = tema.lower() if tema else ""

            # Construir la ruta completa con tema normalizado
            full_blob_name = (
                f"{tema_normalized}/{blob_name}" if tema_normalized else blob_name
            )

            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=full_blob_name
            )

            # Subir el archivo
            blob_client.upload_blob(file_data, overwrite=True)

            # Obtener propiedades del blob
            blob_properties = blob_client.get_blob_properties()

            logger.info(f"Archivo '{full_blob_name}' subido exitosamente")

            return {
                "name": blob_name,
                "full_path": full_blob_name,
                "tema": tema_normalized,
                "size": blob_properties.size,
                "last_modified": blob_properties.last_modified,
                "url": blob_client.url,
            }

        except Exception as e:
            logger.error(f"Error subiendo archivo '{blob_name}': {e}")
            raise e

    async def download_file(self, blob_name: str, tema: str = "") -> bytes:
        """
        Descargar un archivo de Azure Blob Storage

        Args:
            blob_name: Nombre del archivo
            tema: Tema/carpeta donde está el archivo (búsqueda case-insensitive)

        Returns:
            bytes: Contenido del archivo
        """
        try:
            # Si se proporciona tema, buscar el archivo de manera case-insensitive
            if tema:
                full_blob_name = await self._find_blob_case_insensitive(blob_name, tema)
            else:
                full_blob_name = blob_name

            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=full_blob_name
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
            tema: Tema/carpeta donde está el archivo (búsqueda case-insensitive)

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            # Si se proporciona tema, buscar el archivo de manera case-insensitive
            if tema:
                full_blob_name = await self._find_blob_case_insensitive(blob_name, tema)
            else:
                full_blob_name = blob_name

            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=full_blob_name
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
            tema: Tema/carpeta específica (opcional) - filtrado case-insensitive

        Returns:
            List[dict]: Lista de archivos con sus propiedades
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )

            # Obtener todos los blobs para hacer filtrado case-insensitive
            blobs = container_client.list_blobs()

            files = []
            tema_lower = tema.lower() if tema else ""

            for blob in blobs:
                # Extraer información del blob
                blob_tema = os.path.dirname(blob.name) if "/" in blob.name else ""

                # Filtrar por tema de manera case-insensitive si se proporciona
                if tema and blob_tema.lower() != tema_lower:
                    continue

                blob_info = {
                    "name": os.path.basename(blob.name),
                    "full_path": blob.name,
                    "tema": blob_tema,
                    "size": blob.size,
                    "last_modified": blob.last_modified,
                    "content_type": blob.content_settings.content_type
                    if blob.content_settings
                    else None,
                }
                files.append(blob_info)

            logger.info(
                f"Listados {len(files)} archivos"
                + (f" en tema '{tema}' (case-insensitive)" if tema else "")
            )
            return files

        except Exception as e:
            logger.error(f"Error listando archivos: {e}")
            raise e

    async def get_file_info(self, blob_name: str, tema: str = "") -> dict:
        """
        Obtener información de un archivo específico

        Args:
            blob_name: Nombre del archivo
            tema: Tema/carpeta donde está el archivo (búsqueda case-insensitive)

        Returns:
            dict: Información del archivo
        """
        try:
            # Si se proporciona tema, buscar el archivo de manera case-insensitive
            if tema:
                full_blob_name = await self._find_blob_case_insensitive(blob_name, tema)
                # Extraer el tema real del path encontrado
                real_tema = (
                    os.path.dirname(full_blob_name) if "/" in full_blob_name else ""
                )
            else:
                full_blob_name = blob_name
                real_tema = ""

            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=full_blob_name
            )

            # Obtener propiedades
            properties = blob_client.get_blob_properties()

            return {
                "name": blob_name,
                "full_path": full_blob_name,
                "tema": real_tema,
                "size": properties.size,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type,
                "url": blob_client.url,
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
            tema: Tema/carpeta donde está el archivo (búsqueda case-insensitive)

        Returns:
            str: URL de descarga
        """
        try:
            # Si se proporciona tema, buscar el archivo de manera case-insensitive
            if tema:
                full_blob_name = await self._find_blob_case_insensitive(blob_name, tema)
            else:
                full_blob_name = blob_name

            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=full_blob_name
            )

            return blob_client.url

        except Exception as e:
            logger.error(f"Error obteniendo URL de descarga para '{blob_name}': {e}")
            raise e

    async def generate_sas_url(
        self, blob_name: str, tema: str = "", expiry_hours: int = 1
    ) -> str:
        """
        Generar una URL SAS (Shared Access Signature) temporal para acceder a un archivo

        Esta URL permite acceso temporal y seguro al archivo sin requerir autenticación.
        Es ideal para vistas previas de archivos en el navegador.

        Args:
            blob_name: Nombre del archivo
            tema: Tema/carpeta donde está el archivo (búsqueda case-insensitive)
            expiry_hours: Horas de validez de la URL (por defecto 1 hora)

        Returns:
            str: URL completa con SAS token para acceso temporal
        """
        try:
            from azure.storage.blob import ContentSettings

            # Si se proporciona tema, buscar el archivo de manera case-insensitive
            if tema:
                full_blob_name = await self._find_blob_case_insensitive(blob_name, tema)
            else:
                full_blob_name = blob_name

            # Obtener cliente del blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=full_blob_name
            )

            # Verificar que el archivo existe antes de generar el SAS
            if not blob_client.exists():
                raise FileNotFoundError(f"El archivo '{blob_name}' no existe")

            # IMPORTANTE: Configurar el blob para que se muestre inline (no descarga)
            # Esto hace que el navegador muestre el PDF en lugar de descargarlo
            try:
                content_settings = ContentSettings(
                    content_type="application/pdf",
                    content_disposition="inline",  # Clave para mostrar en navegador
                )
                blob_client.set_http_headers(content_settings=content_settings)
                logger.info(
                    f"Headers configurados para visualización inline de '{full_blob_name}'"
                )
            except Exception as e:
                logger.warning(f"No se pudieron configurar headers inline: {e}")

            # Definir el tiempo de expiración del SAS token
            start_time = datetime.now(timezone.utc)
            expiry_time = start_time + timedelta(hours=expiry_hours)

            # Extraer la account key del connection string para generar el SAS
            # El SAS necesita la account key para firmar el token
            account_key = None
            for part in settings.AZURE_STORAGE_CONNECTION_STRING.split(";"):
                if part.startswith("AccountKey="):
                    account_key = part.split("=", 1)[1]
                    break

            if not account_key:
                raise ValueError("No se pudo extraer AccountKey del connection string")

            # Generar el SAS token con permisos de solo lectura
            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=self.container_name,
                blob_name=full_blob_name,
                account_key=account_key,
                permission=BlobSasPermissions(read=True),  # Solo permisos de lectura
                expiry=expiry_time,
                start=start_time,
            )

            # Construir la URL completa con el SAS token
            sas_url = f"{blob_client.url}?{sas_token}"

            logger.info(
                f"SAS URL generada para '{full_blob_name}' (válida por {expiry_hours} horas)"
            )
            return sas_url

        except FileNotFoundError:
            logger.error(f"Archivo '{full_blob_name}' no encontrado para generar SAS")
            raise
        except Exception as e:
            logger.error(f"Error generando SAS URL para '{blob_name}': {e}")
            raise e

    async def _find_blob_case_insensitive(self, blob_name: str, tema: str) -> str:
        """
        Buscar un blob de manera case-insensitive

        Args:
            blob_name: Nombre del archivo a buscar
            tema: Tema donde buscar (case-insensitive)

        Returns:
            str: Ruta completa del blob encontrado

        Raises:
            FileNotFoundError: Si no se encuentra el archivo
        """
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            blobs = container_client.list_blobs()

            tema_lower = tema.lower()
            blob_name_lower = blob_name.lower()

            for blob in blobs:
                blob_tema = os.path.dirname(blob.name) if "/" in blob.name else ""
                current_blob_name = os.path.basename(blob.name)

                if (
                    blob_tema.lower() == tema_lower
                    and current_blob_name.lower() == blob_name_lower
                ):
                    return blob.name

            # Si no se encuentra, usar la construcción original para que falle apropiadamente
            return f"{tema}/{blob_name}"

        except Exception as e:
            logger.error(f"Error buscando blob case-insensitive: {e}")
            # Fallback a construcción original
            return f"{tema}/{blob_name}"


# Instancia global del servicio
azure_service = AzureBlobService()
