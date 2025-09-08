from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import StreamingResponse, Response
from typing import Optional, List
import logging
import os
import zipfile
import io
from datetime import datetime

from ..models.file_models import (
    FileUploadRequest, FileUploadResponse, FileInfo, FileListResponse,
    FileDeleteResponse, FileBatchDeleteRequest, 
    FileConflictResponse, FileBatchDeleteResponse, 
    FileBatchDownloadRequest, TemasListResponse, 
    FileUploadCheckRequest, FileUploadConfirmRequest, ErrorResponse
)
from ..services.azure_service import azure_service
from ..services.file_service import file_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload/check", response_model=FileConflictResponse)
async def check_file_before_upload(request: FileUploadCheckRequest):
    """
    Verificar si un archivo ya existe antes de subirlo
    """
    try:
        # Validar nombre de archivo
        is_valid, error_msg = file_service.validate_filename(request.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validar extensión
        is_valid, error_msg = file_service.validate_file_extension(request.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Limpiar tema
        clean_tema = file_service.clean_tema_name(request.tema or "")
        
        # Verificar si existe conflicto
        has_conflict, suggested_name = await file_service.handle_file_conflict(
            request.filename, clean_tema
        )
        
        if has_conflict:
            return FileConflictResponse(
                conflict=True,
                message=f"El archivo '{request.filename}' ya existe en el tema '{clean_tema or 'general'}'",
                existing_file=request.filename,
                suggested_name=suggested_name,
                tema=clean_tema
            )
        else:
            # No hay conflicto, se puede subir directamente
            return FileConflictResponse(
                conflict=False,
                message="Archivo disponible para subir",
                existing_file=request.filename,
                suggested_name=request.filename,
                tema=clean_tema
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando archivo '{request.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/upload/confirm", response_model=FileUploadResponse)
async def upload_file_with_confirmation(
    file: UploadFile = File(...),
    action: str = Form(...),
    tema: Optional[str] = Form(None),
    new_filename: Optional[str] = Form(None)
):
    """
    Subir archivo con confirmación de acción para conflictos
    """
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        # Crear request de confirmación para validaciones
        confirm_request = FileUploadConfirmRequest(
            filename=file.filename,
            tema=tema,
            action=action,
            new_filename=new_filename
        )
        
        # Si la acción es cancelar, no hacer nada
        if confirm_request.action == "cancel":
            return FileUploadResponse(
                success=False,
                message="Subida cancelada por el usuario",
                file=None
            )
        
        # Determinar el nombre final del archivo
        final_filename = file.filename
        if confirm_request.action == "rename" and confirm_request.new_filename:
            final_filename = confirm_request.new_filename
        
        # Validar extensión del archivo final
        is_valid, error_msg = file_service.validate_file_extension(final_filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar tamaño del archivo
        is_valid, error_msg = file_service.validate_file_size(len(file_content))
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Limpiar tema
        clean_tema = file_service.clean_tema_name(confirm_request.tema or "")
        
        # Si es sobrescribir, verificar que el archivo original exista
        if confirm_request.action == "overwrite":
            exists = await file_service.check_file_exists(file.filename, clean_tema)
            if not exists:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Archivo '{file.filename}' no existe para sobrescribir"
                )
        
        # Subir archivo a Azure
        file_stream = io.BytesIO(file_content)
        uploaded_file_info = await azure_service.upload_file(
            file_data=file_stream,
            blob_name=final_filename,
            tema=clean_tema
        )
        
        # Crear objeto FileInfo
        file_info = FileInfo(
            name=uploaded_file_info["name"],
            full_path=uploaded_file_info["full_path"],
            tema=uploaded_file_info["tema"],
            size=uploaded_file_info["size"],
            last_modified=uploaded_file_info["last_modified"],
            url=uploaded_file_info["url"]
        )
        
        action_msg = {
            "overwrite": "sobrescrito",
            "rename": f"renombrado a '{final_filename}'"
        }
        
        logger.info(f"Archivo '{file.filename}' {action_msg.get(confirm_request.action, 'subido')} exitosamente")
        
        return FileUploadResponse(
            success=True,
            message=f"Archivo {action_msg.get(confirm_request.action, 'subido')} exitosamente",
            file=file_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en subida confirmada: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    tema: Optional[str] = Form(None)
):
    """
    Subir un archivo al almacenamiento
    """
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        # Validar extensión del archivo
        file_extension = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv']
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(allowed_extensions)}"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar tamaño del archivo (100MB máximo)
        max_size = 100 * 1024 * 1024  # 100MB
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo permitido: 100MB"
            )
        
        # Procesar tema
        upload_request = FileUploadRequest(tema=tema)
        processed_tema = upload_request.tema or ""
        
        # Subir archivo a Azure
        file_stream = io.BytesIO(file_content)
        uploaded_file_info = await azure_service.upload_file(
            file_data=file_stream,
            blob_name=file.filename,
            tema=processed_tema
        )
        
        # Crear objeto FileInfo
        file_info = FileInfo(
            name=uploaded_file_info["name"],
            full_path=uploaded_file_info["full_path"],
            tema=uploaded_file_info["tema"],
            size=uploaded_file_info["size"],
            last_modified=uploaded_file_info["last_modified"],
            url=uploaded_file_info["url"]
        )
        
        logger.info(f"Archivo '{file.filename}' subido exitosamente al tema '{processed_tema}'")
        
        return FileUploadResponse(
            success=True,
            message="Archivo subido exitosamente",
            file=file_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/", response_model=FileListResponse)
async def list_files(tema: Optional[str] = Query(None, description="Filtrar por tema")):
    """
    Listar archivos, opcionalmente filtrados por tema
    """
    try:
        # Obtener archivos de Azure
        files_data = await azure_service.list_files(tema=tema or "")
        
        # Convertir a objetos FileInfo
        files_info = []
        for file_data in files_data:
            file_info = FileInfo(
                name=file_data["name"],
                full_path=file_data["full_path"],
                tema=file_data["tema"],
                size=file_data["size"],
                last_modified=file_data["last_modified"],
                content_type=file_data.get("content_type")
            )
            files_info.append(file_info)
        
        logger.info(f"Listados {len(files_info)} archivos" + (f" del tema '{tema}'" if tema else ""))
        
        return FileListResponse(
            files=files_info,
            total=len(files_info),
            tema=tema
        )
        
    except Exception as e:
        logger.error(f"Error listando archivos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/temas", response_model=TemasListResponse)
async def list_temas():
    """
    Listar todos los temas disponibles
    """
    try:
        # Obtener todos los archivos
        files_data = await azure_service.list_files()
        
        # Extraer temas únicos
        temas = set()
        for file_data in files_data:
            if file_data["tema"]:
                temas.add(file_data["tema"])
        
        temas_list = sorted(list(temas))
        
        logger.info(f"Encontrados {len(temas_list)} temas")
        
        return TemasListResponse(
            temas=temas_list,
            total=len(temas_list)
        )
        
    except Exception as e:
        logger.error(f"Error listando temas: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/{filename}/download")
async def download_file(
    filename: str,
    tema: Optional[str] = Query(None, description="Tema donde está el archivo")
):
    """
    Descargar un archivo individual
    """
    try:
        # Descargar archivo de Azure
        file_content = await azure_service.download_file(
            blob_name=filename,
            tema=tema or ""
        )
        
        # Obtener información del archivo para content-type
        file_info = await azure_service.get_file_info(
            blob_name=filename,
            tema=tema or ""
        )
        
        # Determinar content-type
        content_type = file_info.get("content_type", "application/octet-stream")
        
        logger.info(f"Descargando archivo '{filename}'" + (f" del tema '{tema}'" if tema else ""))
        
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Archivo '{filename}' no encontrado")
    except Exception as e:
        logger.error(f"Error descargando archivo '{filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.delete("/{filename}", response_model=FileDeleteResponse)
async def delete_file(
    filename: str,
    tema: Optional[str] = Query(None, description="Tema donde está el archivo")
):
    """
    Eliminar un archivo
    """
    try:
        # Eliminar archivo de Azure
        await azure_service.delete_file(
            blob_name=filename,
            tema=tema or ""
        )
        
        logger.info(f"Archivo '{filename}' eliminado exitosamente" + (f" del tema '{tema}'" if tema else ""))
        
        return FileDeleteResponse(
            success=True,
            message="Archivo eliminado exitosamente",
            deleted_file=filename
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Archivo '{filename}' no encontrado")
    except Exception as e:
        logger.error(f"Error eliminando archivo '{filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/delete-batch", response_model=FileBatchDeleteResponse)
async def delete_batch_files(request: FileBatchDeleteRequest):
    """
    Eliminar múltiples archivos
    """
    try:
        deleted_files = []
        failed_files = []
        
        for filename in request.files:
            try:
                await azure_service.delete_file(
                    blob_name=filename,
                    tema=request.tema or ""
                )
                deleted_files.append(filename)
                logger.info(f"Archivo '{filename}' eliminado exitosamente")
            except Exception as e:
                failed_files.append(filename)
                logger.error(f"Error eliminando archivo '{filename}': {e}")
        
        success = len(failed_files) == 0
        message = f"Eliminados {len(deleted_files)} archivos exitosamente"
        if failed_files:
            message += f", {len(failed_files)} archivos fallaron"
        
        return FileBatchDeleteResponse(
            success=success,
            message=message,
            deleted_files=deleted_files,
            failed_files=failed_files
        )
        
    except Exception as e:
        logger.error(f"Error en eliminación batch: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/download-batch")
async def download_batch_files(request: FileBatchDownloadRequest):
    """
    Descargar múltiples archivos como ZIP
    """
    try:
        # Crear ZIP en memoria
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in request.files:
                try:
                    # Descargar archivo de Azure
                    file_content = await azure_service.download_file(
                        blob_name=filename,
                        tema=request.tema or ""
                    )
                    
                    # Agregar al ZIP
                    zip_file.writestr(filename, file_content)
                    logger.info(f"Archivo '{filename}' agregado al ZIP")
                    
                except Exception as e:
                    logger.error(f"Error agregando '{filename}' al ZIP: {e}")
                    # Continuar con otros archivos
                    continue
        
        zip_buffer.seek(0)
        
        # Generar nombre del ZIP
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{request.zip_name}_{timestamp}.zip"
        
        logger.info(f"ZIP creado exitosamente: {zip_filename}")
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error creando ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/tema/{tema}/download-all")
async def download_tema_completo(tema: str):
    """
    Descargar todos los archivos de un tema como ZIP
    """
    try:
        # Obtener todos los archivos del tema
        files_data = await azure_service.list_files(tema=tema)
        
        if not files_data:
            raise HTTPException(status_code=404, detail=f"No se encontraron archivos en el tema '{tema}'")
        
        # Crear ZIP en memoria
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_data in files_data:
                try:
                    filename = file_data["name"]
                    
                    # Descargar archivo de Azure
                    file_content = await azure_service.download_file(
                        blob_name=filename,
                        tema=tema
                    )
                    
                    # Agregar al ZIP
                    zip_file.writestr(filename, file_content)
                    logger.info(f"Archivo '{filename}' agregado al ZIP del tema '{tema}'")
                    
                except Exception as e:
                    logger.error(f"Error agregando '{filename}' al ZIP: {e}")
                    # Continuar con otros archivos
                    continue
        
        zip_buffer.seek(0)
        
        # Generar nombre del ZIP
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{tema}_{timestamp}.zip"
        
        logger.info(f"ZIP del tema '{tema}' creado exitosamente: {zip_filename}")
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando ZIP del tema '{tema}': {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.delete("/tema/{tema}/delete-all", response_model=FileBatchDeleteResponse)
async def delete_tema_completo(tema: str):
    """
    Eliminar todos los archivos de un tema
    """
    try:
        # Obtener todos los archivos del tema
        files_data = await azure_service.list_files(tema=tema)
        
        if not files_data:
            raise HTTPException(status_code=404, detail=f"No se encontraron archivos en el tema '{tema}'")
        
        deleted_files = []
        failed_files = []
        
        for file_data in files_data:
            filename = file_data["name"]
            try:
                await azure_service.delete_file(
                    blob_name=filename,
                    tema=tema
                )
                deleted_files.append(filename)
                logger.info(f"Archivo '{filename}' eliminado del tema '{tema}'")
            except Exception as e:
                failed_files.append(filename)
                logger.error(f"Error eliminando archivo '{filename}' del tema '{tema}': {e}")
        
        success = len(failed_files) == 0
        message = f"Tema '{tema}': eliminados {len(deleted_files)} archivos exitosamente"
        if failed_files:
            message += f", {len(failed_files)} archivos fallaron"
        
        logger.info(f"Eliminación completa del tema '{tema}': {len(deleted_files)} exitosos, {len(failed_files)} fallidos")
        
        return FileBatchDeleteResponse(
            success=success,
            message=message,
            deleted_files=deleted_files,
            failed_files=failed_files
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando tema '{tema}': {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/{filename}/info", response_model=FileInfo)
async def get_file_info(
    filename: str,
    tema: Optional[str] = Query(None, description="Tema donde está el archivo")
):
    """
    Obtener información detallada de un archivo
    """
    try:
        # Obtener información de Azure
        file_data = await azure_service.get_file_info(
            blob_name=filename,
            tema=tema or ""
        )
        
        # Convertir a objeto FileInfo
        file_info = FileInfo(
            name=file_data["name"],
            full_path=file_data["full_path"],
            tema=file_data["tema"],
            size=file_data["size"],
            last_modified=file_data["last_modified"],
            content_type=file_data.get("content_type"),
            url=file_data.get("url")
        )
        
        logger.info(f"Información obtenida para archivo '{filename}'")
        return file_info
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Archivo '{filename}' no encontrado")
    except Exception as e:
        logger.error(f"Error obteniendo info del archivo '{filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")