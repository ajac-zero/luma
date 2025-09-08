import os
import re
from typing import Optional, Tuple
import logging

from ..services.azure_service import azure_service

logger = logging.getLogger(__name__)


class FileService:
    """
    Servicio para lógica de negocio de archivos
    """
    
    async def check_file_exists(self, filename: str, tema: str = "") -> bool:
        """
        Verificar si un archivo ya existe en el almacenamiento
        
        Args:
            filename: Nombre del archivo
            tema: Tema donde buscar el archivo
            
        Returns:
            bool: True si el archivo existe, False si no
        """
        try:
            await azure_service.get_file_info(filename, tema)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error verificando existencia del archivo '{filename}': {e}")
            return False
    
    def generate_new_filename(self, original_filename: str, existing_files: list = None) -> str:
        """
        Generar un nuevo nombre de archivo si ya existe uno igual
        
        Args:
            original_filename: Nombre original del archivo
            existing_files: Lista de archivos existentes (opcional)
            
        Returns:
            str: Nuevo nombre de archivo (ej: archivo_1.pdf)
        """
        # Separar nombre y extensión
        name, extension = os.path.splitext(original_filename)
        
        # Buscar si ya tiene un número al final (ej: archivo_1.pdf)
        match = re.search(r'(.+)_(\d+)$', name)
        if match:
            base_name = match.group(1)
            current_number = int(match.group(2))
        else:
            base_name = name
            current_number = 0
        
        # Incrementar número hasta encontrar uno disponible
        counter = current_number + 1
        new_filename = f"{base_name}_{counter}{extension}"
        
        # Si tenemos lista de archivos existentes, verificar contra ella
        if existing_files:
            while new_filename in existing_files:
                counter += 1
                new_filename = f"{base_name}_{counter}{extension}"
        
        return new_filename
    
    async def handle_file_conflict(self, filename: str, tema: str = "") -> Tuple[bool, Optional[str]]:
        """
        Manejar conflicto cuando un archivo ya existe
        
        Args:
            filename: Nombre del archivo
            tema: Tema donde está el archivo
            
        Returns:
            Tuple[bool, Optional[str]]: (existe_conflicto, nombre_sugerido)
        """
        exists = await self.check_file_exists(filename, tema)
        
        if not exists:
            return False, None
        
        # Generar nombre alternativo
        suggested_name = self.generate_new_filename(filename)
        
        # Verificar que el nombre sugerido tampoco exista
        counter = 1
        while await self.check_file_exists(suggested_name, tema):
            name, extension = os.path.splitext(filename)
            # Buscar base sin número
            match = re.search(r'(.+)_(\d+)$', name)
            base_name = match.group(1) if match else name
            counter += 1
            suggested_name = f"{base_name}_{counter}{extension}"
        
        return True, suggested_name
    
    def validate_filename(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validar que el nombre del archivo sea válido
        
        Args:
            filename: Nombre del archivo a validar
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not filename:
            return False, "Nombre de archivo requerido"
        
        # Verificar caracteres no permitidos
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, filename):
            return False, "El nombre contiene caracteres no permitidos: < > : \" / \\ | ? *"
        
        # Verificar longitud
        if len(filename) > 255:
            return False, "Nombre de archivo demasiado largo (máximo 255 caracteres)"
        
        # Verificar nombres reservados (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            return False, f"'{name_without_ext}' es un nombre reservado del sistema"
        
        return True, None
    
    def validate_file_extension(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validar que la extensión del archivo esté permitida
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv']
        
        file_extension = os.path.splitext(filename)[1].lower()
        
        if not file_extension:
            return False, "Archivo debe tener una extensión"
        
        if file_extension not in allowed_extensions:
            return False, f"Extensión no permitida. Permitidas: {', '.join(allowed_extensions)}"
        
        return True, None
    
    def validate_file_size(self, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validar que el tamaño del archivo esté dentro de los límites
        
        Args:
            file_size: Tamaño del archivo en bytes
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        max_size = 100 * 1024 * 1024  # 100MB
        
        if file_size <= 0:
            return False, "El archivo está vacío"
        
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"Archivo demasiado grande. Tamaño máximo: {max_size_mb}MB"
        
        return True, None
    
    def validate_tema(self, tema: str) -> Tuple[bool, Optional[str]]:
        """
        Validar que el tema sea válido
        
        Args:
            tema: Nombre del tema
            
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, mensaje_error)
        """
        if not tema:
            return True, None  # Tema opcional
        
        # Verificar caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9\-_\s]+$', tema):
            return False, "Tema solo puede contener letras, números, guiones y espacios"
        
        # Verificar longitud
        if len(tema) > 50:
            return False, "Nombre de tema demasiado largo (máximo 50 caracteres)"
        
        return True, None
    
    def clean_tema_name(self, tema: str) -> str:
        """
        Limpiar nombre de tema para Azure Storage
        
        Args:
            tema: Nombre del tema original
            
        Returns:
            str: Nombre limpio para usar como carpeta
        """
        if not tema:
            return ""
        
        # Convertir a minúsculas y reemplazar espacios con guiones
        cleaned = tema.lower().strip()
        cleaned = re.sub(r'\s+', '-', cleaned)  # Espacios múltiples a un guion
        cleaned = re.sub(r'[^a-z0-9\-_]', '', cleaned)  # Solo caracteres permitidos
        cleaned = re.sub(r'-+', '-', cleaned)  # Guiones múltiples a uno
        cleaned = cleaned.strip('-')  # Quitar guiones al inicio/final
        
        return cleaned
    
    async def get_existing_files_in_tema(self, tema: str = "") -> list:
        """
        Obtener lista de nombres de archivos existentes en un tema
        
        Args:
            tema: Tema donde buscar archivos
            
        Returns:
            list: Lista de nombres de archivos
        """
        try:
            files_data = await azure_service.list_files(tema)
            return [file_data["name"] for file_data in files_data]
        except Exception as e:
            logger.error(f"Error obteniendo archivos del tema '{tema}': {e}")
            return []


# Instancia global del servicio
file_service = FileService()