from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import os


class FileUploadRequest(BaseModel):
    """Modelo para request de subida de archivo"""
    tema: Optional[str] = Field(None, description="Tema/carpeta donde guardar el archivo")
    
    @validator("tema")
    def validate_tema(cls, v):
        if v:
            # Limpiar el tema: solo letras, números, guiones y espacios
            cleaned = "".join(c for c in v if c.isalnum() or c in "-_ ")
            return cleaned.strip().lower().replace(" ", "-")
        return v


class FileInfo(BaseModel):
    """Modelo para información de un archivo"""
    name: str = Field(..., description="Nombre del archivo")
    full_path: str = Field(..., description="Ruta completa en Azure")
    tema: Optional[str] = Field(None, description="Tema/carpeta del archivo")
    size: int = Field(..., description="Tamaño del archivo en bytes")
    last_modified: datetime = Field(..., description="Fecha de última modificación")
    content_type: Optional[str] = Field(None, description="Tipo MIME del archivo")
    url: Optional[str] = Field(None, description="URL de descarga")
    
    @property
    def size_mb(self) -> float:
        """Tamaño del archivo en MB"""
        return round(self.size / (1024 * 1024), 2)
    
    @property
    def extension(self) -> str:
        """Extensión del archivo"""
        return os.path.splitext(self.name)[1].lower()
    
    class Config:
        # Permitir usar propiedades calculadas en JSON
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileListResponse(BaseModel):
    """Modelo para respuesta de listado de archivos"""
    files: List[FileInfo] = Field(..., description="Lista de archivos")
    total: int = Field(..., description="Total de archivos")
    tema: Optional[str] = Field(None, description="Tema filtrado (si aplica)")


class FileUploadResponse(BaseModel):
    """Modelo para respuesta de subida de archivo"""
    success: bool = Field(..., description="Indica si la subida fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    file: Optional[FileInfo] = Field(None, description="Información del archivo subido")


class FileDeleteResponse(BaseModel):
    """Modelo para respuesta de eliminación de archivo"""
    success: bool = Field(..., description="Indica si la eliminación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    deleted_file: str = Field(..., description="Nombre del archivo eliminado")


class FileBatchDeleteRequest(BaseModel):
    """Modelo para request de eliminación múltiple"""
    files: List[str] = Field(..., description="Lista de nombres de archivos a eliminar")
    tema: Optional[str] = Field(None, description="Tema donde están los archivos")
    
    @validator("files")
    def validate_files_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("La lista de archivos no puede estar vacía")
        return v


class FileBatchDeleteResponse(BaseModel):
    """Modelo para respuesta de eliminación múltiple"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    deleted_files: List[str] = Field(..., description="Archivos eliminados exitosamente")
    failed_files: List[str] = Field(default_factory=list, description="Archivos que no se pudieron eliminar")


class FileBatchDownloadRequest(BaseModel):
    """Modelo para request de descarga múltiple"""
    files: List[str] = Field(..., description="Lista de nombres de archivos a descargar")
    tema: Optional[str] = Field(None, description="Tema donde están los archivos")
    zip_name: Optional[str] = Field("archivos", description="Nombre del archivo ZIP")
    
    @validator("files")
    def validate_files_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("La lista de archivos no puede estar vacía")
        return v
    
    @validator("zip_name")
    def validate_zip_name(cls, v):
        # Limpiar nombre del ZIP
        if v:
            cleaned = "".join(c for c in v if c.isalnum() or c in "-_")
            return cleaned or "archivos"
        return "archivos"


class TemasListResponse(BaseModel):
    """Modelo para respuesta de listado de temas"""
    temas: List[str] = Field(..., description="Lista de temas disponibles")
    total: int = Field(..., description="Total de temas")


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: bool = Field(True, description="Indica que es un error")
    message: str = Field(..., description="Mensaje de error")
    status_code: int = Field(..., description="Código de estado HTTP")
    details: Optional[str] = Field(None, description="Detalles adicionales del error")


class FileConflictResponse(BaseModel):
    """Modelo para respuesta cuando hay conflicto de archivo existente"""
    conflict: bool = Field(True, description="Indica que hay conflicto")
    message: str = Field(..., description="Mensaje explicando el conflicto")
    existing_file: str = Field(..., description="Nombre del archivo que ya existe")
    suggested_name: str = Field(..., description="Nombre sugerido para evitar conflicto")
    tema: Optional[str] = Field(None, description="Tema donde está el archivo")


class FileUploadCheckRequest(BaseModel):
    """Modelo para verificar si un archivo existe antes de subir"""
    filename: str = Field(..., description="Nombre del archivo a verificar")
    tema: Optional[str] = Field(None, description="Tema donde verificar")
    
    @validator("tema")
    def validate_tema(cls, v):
        if v:
            # Limpiar el tema: solo letras, números, guiones y espacios
            cleaned = "".join(c for c in v if c.isalnum() or c in "-_ ")
            return cleaned.strip().lower().replace(" ", "-")
        return v


class FileUploadConfirmRequest(BaseModel):
    """Modelo para confirmar subida de archivo con decisión del usuario"""
    filename: str = Field(..., description="Nombre del archivo original")
    tema: Optional[str] = Field(None, description="Tema donde subir")
    action: str = Field(..., description="Acción a tomar: 'overwrite', 'rename', 'cancel'")
    new_filename: Optional[str] = Field(None, description="Nuevo nombre si action es 'rename'")
    
    @validator("action")
    def validate_action(cls, v):
        allowed_actions = ["overwrite", "rename", "cancel"]
        if v not in allowed_actions:
            raise ValueError(f"Acción debe ser una de: {', '.join(allowed_actions)}")
        return v
    
    @validator("new_filename")
    def validate_new_filename(cls, v, values):
        if values.get("action") == "rename" and not v:
            raise ValueError("new_filename es requerido cuando action es 'rename'")
        return v
    
    @validator("tema")
    def validate_tema(cls, v):
        if v:
            # Limpiar el tema: solo letras, números, guiones y espacios
            cleaned = "".join(c for c in v if c.isalnum() or c in "-_ ")
            return cleaned.strip().lower().replace(" ", "-")
        return v


class HealthResponse(BaseModel):
    """Modelo para respuesta de health check"""
    status: str = Field(..., description="Estado de la aplicación")
    message: str = Field(..., description="Mensaje descriptivo")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del check")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }