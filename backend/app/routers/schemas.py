"""
Router para gestión de schemas personalizables.
Endpoints CRUD para crear, leer, actualizar y eliminar schemas.
"""
import logging
import uuid
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..models.schema_models import (
    CustomSchema,
    SchemaListResponse,
    SchemaValidationResponse
)
from ..repositories.schema_repository import get_schema_repository
from ..services.schema_builder_service import SchemaBuilderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/schemas", tags=["schemas"])


@router.post("/", response_model=CustomSchema, status_code=201)
async def create_schema(schema: CustomSchema):
    """
    Crea un nuevo schema personalizado.

    Args:
        schema: Definición del schema

    Returns:
        Schema creado con ID y timestamps

    Raises:
        HTTPException 400: Si el schema es inválido
        HTTPException 409: Si ya existe un schema con ese ID
    """
    try:
        # Generar ID si no viene
        if not schema.schema_id:
            schema.schema_id = f"schema_{uuid.uuid4().hex[:12]}"

        # Verificar que no exista
        repo = get_schema_repository()
        if repo.exists(schema.schema_id):
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un schema con ID: {schema.schema_id}"
            )

        # Validar que se puede construir el schema
        builder = SchemaBuilderService()
        validation = builder.validate_schema(schema)

        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Schema inválido",
                    "errors": validation["errors"]
                }
            )

        # Guardar
        saved_schema = repo.save(schema)

        logger.info(f"Schema creado: {saved_schema.schema_id} - {saved_schema.schema_name}")
        return saved_schema

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando schema: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/", response_model=List[CustomSchema])
async def list_schemas(
    tema: Optional[str] = Query(None, description="Filtrar por tema (incluye globales)")
):
    """
    Lista todos los schemas o filtrados por tema.

    Args:
        tema: Nombre del tema para filtrar (opcional)

    Returns:
        Lista de schemas
    """
    try:
        repo = get_schema_repository()

        if tema:
            schemas = repo.list_by_tema(tema)
        else:
            schemas = repo.list_all()

        return schemas

    except Exception as e:
        logger.error(f"Error listando schemas: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{schema_id}", response_model=CustomSchema)
async def get_schema(schema_id: str):
    """
    Obtiene un schema por su ID.

    Args:
        schema_id: ID del schema

    Returns:
        Schema solicitado

    Raises:
        HTTPException 404: Si el schema no existe
    """
    try:
        repo = get_schema_repository()
        schema = repo.get_by_id(schema_id)

        if not schema:
            raise HTTPException(
                status_code=404,
                detail=f"Schema no encontrado: {schema_id}"
            )

        return schema

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo schema {schema_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{schema_id}", response_model=CustomSchema)
async def update_schema(schema_id: str, schema: CustomSchema):
    """
    Actualiza un schema existente.

    Args:
        schema_id: ID del schema a actualizar
        schema: Nueva definición del schema

    Returns:
        Schema actualizado

    Raises:
        HTTPException 404: Si el schema no existe
        HTTPException 400: Si el nuevo schema es inválido
    """
    try:
        repo = get_schema_repository()

        # Verificar que existe
        existing = repo.get_by_id(schema_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Schema no encontrado: {schema_id}"
            )

        # Mantener el ID original
        schema.schema_id = schema_id
        schema.created_at = existing.created_at  # Mantener fecha de creación

        # Validar nuevo schema
        builder = SchemaBuilderService()
        validation = builder.validate_schema(schema)

        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Schema inválido",
                    "errors": validation["errors"]
                }
            )

        # Guardar
        updated_schema = repo.save(schema)

        logger.info(f"Schema actualizado: {schema_id}")
        return updated_schema

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando schema {schema_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete("/{schema_id}")
async def delete_schema(schema_id: str):
    """
    Elimina un schema.

    Args:
        schema_id: ID del schema a eliminar

    Returns:
        Mensaje de confirmación

    Raises:
        HTTPException 404: Si el schema no existe
    """
    try:
        repo = get_schema_repository()

        if not repo.delete(schema_id):
            raise HTTPException(
                status_code=404,
                detail=f"Schema no encontrado: {schema_id}"
            )

        logger.info(f"Schema eliminado: {schema_id}")
        return {
            "success": True,
            "message": f"Schema {schema_id} eliminado exitosamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando schema {schema_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/validate", response_model=SchemaValidationResponse)
async def validate_schema(schema: CustomSchema):
    """
    Valida un schema sin guardarlo.
    Útil para preview en el frontend antes de guardar.

    Args:
        schema: Schema a validar

    Returns:
        Resultado de validación con detalles
    """
    try:
        builder = SchemaBuilderService()
        validation = builder.validate_schema(schema)

        return SchemaValidationResponse(**validation)

    except Exception as e:
        logger.error(f"Error validando schema: {e}")
        return SchemaValidationResponse(
            valid=False,
            message="Error en validación",
            errors=[str(e)]
        )


@router.get("/stats/count")
async def get_schemas_count():
    """
    Obtiene estadísticas de schemas.

    Returns:
        Conteo de schemas total y por tema
    """
    try:
        repo = get_schema_repository()
        all_schemas = repo.list_all()

        # Contar por tema
        tema_counts = {}
        global_count = 0

        for schema in all_schemas:
            if schema.is_global:
                global_count += 1
            elif schema.tema:
                tema_counts[schema.tema] = tema_counts.get(schema.tema, 0) + 1

        return {
            "total": len(all_schemas),
            "global": global_count,
            "by_tema": tema_counts
        }

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
