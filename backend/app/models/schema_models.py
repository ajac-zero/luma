"""
Modelos Pydantic para schemas personalizables.
Permite definir schemas dinámicos desde el frontend para extracción de datos.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
from datetime import datetime


class FieldType(str, Enum):
    """Tipos de campos soportados para extracción"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY_STRING = "array_string"
    ARRAY_INTEGER = "array_integer"
    ARRAY_FLOAT = "array_float"
    DATE = "date"


class SchemaField(BaseModel):
    """Definición de un campo del schema"""
    name: str = Field(..., description="Nombre del campo (snake_case)", min_length=1)
    type: FieldType = Field(..., description="Tipo de dato del campo")
    description: str = Field(..., description="Descripción clara para el LLM sobre qué extraer", min_length=1)
    required: bool = Field(default=False, description="¿Es obligatorio extraer este campo?")

    # Validaciones opcionales
    min_value: Optional[float] = Field(None, description="Valor mínimo (para integer/float)")
    max_value: Optional[float] = Field(None, description="Valor máximo (para integer/float)")
    pattern: Optional[str] = Field(None, description="Patrón regex para validar strings")

    @field_validator('name')
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        """Valida que el nombre del campo sea snake_case válido"""
        if not v.replace('_', '').isalnum():
            raise ValueError("El nombre del campo debe ser snake_case alfanumérico")
        if v[0].isdigit():
            raise ValueError("El nombre del campo no puede empezar con número")
        return v.lower()

    @field_validator('min_value', 'max_value')
    @classmethod
    def validate_numeric_constraints(cls, v: Optional[float], info) -> Optional[float]:
        """Valida que min/max solo se usen con tipos numéricos"""
        if v is not None:
            field_type = info.data.get('type')
            if field_type not in [FieldType.INTEGER, FieldType.FLOAT, FieldType.ARRAY_INTEGER, FieldType.ARRAY_FLOAT]:
                raise ValueError(f"min_value/max_value solo aplican a campos numéricos, no a {field_type}")
        return v


class CustomSchema(BaseModel):
    """Schema personalizable por el usuario para extracción de datos"""
    schema_id: Optional[str] = Field(None, description="ID único del schema (generado automáticamente si no se provee)")
    schema_name: str = Field(..., description="Nombre descriptivo del schema", min_length=1, max_length=100)
    description: str = Field(..., description="Descripción de qué extrae este schema", min_length=1, max_length=500)
    fields: List[SchemaField] = Field(..., description="Lista de campos a extraer", min_items=1, max_items=200)

    # Metadata
    created_at: Optional[str] = Field(None, description="Timestamp de creación ISO")
    updated_at: Optional[str] = Field(None, description="Timestamp de última actualización ISO")
    tema: Optional[str] = Field(None, description="Tema asociado (si es específico de un tema)")
    is_global: bool = Field(default=False, description="¿Disponible para todos los temas?")

    @field_validator('fields')
    @classmethod
    def validate_unique_field_names(cls, v: List[SchemaField]) -> List[SchemaField]:
        """Valida que no haya nombres de campos duplicados"""
        field_names = [field.name for field in v]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Los nombres de campos deben ser únicos en el schema")
        return v

    @field_validator('schema_name')
    @classmethod
    def validate_schema_name(cls, v: str) -> str:
        """Limpia y valida el nombre del schema"""
        return v.strip()


class SchemaListResponse(BaseModel):
    """Response para listar schemas"""
    schemas: List[CustomSchema]
    total: int


class SchemaValidationResponse(BaseModel):
    """Response para validación de schema"""
    valid: bool
    message: str
    json_schema: Optional[dict] = None
    errors: Optional[List[str]] = None
