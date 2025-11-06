"""
Schema Builder Service - Patrón Builder
Construye schemas Pydantic dinámicamente desde definiciones JSON del frontend.
"""
import logging
from typing import Dict, Any, Type, get_origin, get_args
from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo

from ..models.schema_models import CustomSchema, FieldType, SchemaField

logger = logging.getLogger(__name__)


class SchemaBuilderService:
    """
    Servicio para construir schemas Pydantic dinámicamente.
    Implementa patrón Builder para construcción step-by-step.
    """

    @staticmethod
    def build_pydantic_schema(custom_schema: CustomSchema) -> Type[BaseModel]:
        """
        Convierte un CustomSchema a una clase Pydantic dinámica.

        Este método es el núcleo del patrón Builder, construyendo
        una clase Pydantic válida que puede ser usada por LandingAI.

        Args:
            custom_schema: Schema personalizado del usuario

        Returns:
            Clase Pydantic generada dinámicamente

        Raises:
            ValueError: Si el schema es inválido
        """
        logger.info(f"Construyendo Pydantic schema: {custom_schema.schema_name}")

        field_definitions = {}

        for field in custom_schema.fields:
            try:
                # 1. Mapear tipo Python
                python_type = SchemaBuilderService._map_field_type(field.type)

                # 2. Crear FieldInfo con validaciones
                field_info = SchemaBuilderService._build_field_info(field)

                # 3. Agregar al diccionario de definiciones
                field_definitions[field.name] = (python_type, field_info)

                logger.debug(f"  Campo '{field.name}': {python_type} - {field.description[:50]}...")

            except Exception as e:
                logger.error(f"Error construyendo campo '{field.name}': {e}")
                raise ValueError(f"Campo inválido '{field.name}': {str(e)}")

        # 4. Crear clase dinámica
        try:
            # Nombre de clase válido (sin espacios ni caracteres especiales)
            class_name = custom_schema.schema_name.replace(" ", "").replace("-", "")
            if not class_name[0].isalpha():
                class_name = "Schema" + class_name

            DynamicSchema = create_model(
                class_name,
                **field_definitions
            )

            logger.info(f"Schema Pydantic creado exitosamente: {class_name} con {len(field_definitions)} campos")
            return DynamicSchema

        except Exception as e:
            logger.error(f"Error creando modelo Pydantic: {e}")
            raise ValueError(f"No se pudo crear el schema: {str(e)}")

    @staticmethod
    def _map_field_type(field_type: FieldType) -> Type:
        """
        Mapea FieldType a tipo Python nativo.

        Args:
            field_type: Tipo de campo del schema

        Returns:
            Tipo Python correspondiente
        """
        from typing import List

        type_mapping = {
            FieldType.STRING: str,
            FieldType.INTEGER: int,
            FieldType.FLOAT: float,
            FieldType.BOOLEAN: bool,
            FieldType.ARRAY_STRING: List[str],
            FieldType.ARRAY_INTEGER: List[int],
            FieldType.ARRAY_FLOAT: List[float],
            FieldType.DATE: str,  # Dates como strings ISO 8601
        }

        if field_type not in type_mapping:
            raise ValueError(f"Tipo de campo no soportado: {field_type}")

        return type_mapping[field_type]

    @staticmethod
    def _build_field_info(field: SchemaField) -> FieldInfo:
        """
        Construye FieldInfo con validaciones apropiadas.

        Args:
            field: Definición del campo

        Returns:
            FieldInfo configurado
        """
        # Configuración base
        field_kwargs = {
            "description": field.description,
        }

        # Default value según si es requerido
        if field.required:
            field_kwargs["default"] = ...  # Ellipsis = required
        else:
            field_kwargs["default"] = None

        # Validaciones numéricas
        if field.min_value is not None:
            field_kwargs["ge"] = field.min_value  # greater or equal

        if field.max_value is not None:
            field_kwargs["le"] = field.max_value  # less or equal

        # Validaciones de string
        if field.pattern:
            field_kwargs["pattern"] = field.pattern

        return Field(**field_kwargs)

    @staticmethod
    def to_json_schema(pydantic_schema: Type[BaseModel]) -> Dict[str, Any]:
        """
        Convierte un Pydantic schema a JSON Schema para LandingAI.

        Args:
            pydantic_schema: Clase Pydantic

        Returns:
            JSON Schema dict compatible con LandingAI

        Raises:
            ImportError: Si landingai-ade no está instalado
        """
        try:
            from landingai_ade.lib import pydantic_to_json_schema

            json_schema = pydantic_to_json_schema(pydantic_schema)
            logger.info("Schema convertido a JSON schema exitosamente")
            return json_schema

        except ImportError:
            logger.error("landingai-ade no está instalado")
            raise ImportError(
                "Se requiere landingai-ade para convertir a JSON schema. "
                "Instalar con: pip install landingai-ade"
            )

    @staticmethod
    def validate_schema(custom_schema: CustomSchema) -> Dict[str, Any]:
        """
        Valida que un schema se pueda construir correctamente.

        Args:
            custom_schema: Schema a validar

        Returns:
            Dict con resultado de validación:
            {
                "valid": bool,
                "message": str,
                "json_schema": dict (si válido),
                "errors": List[str] (si inválido)
            }
        """
        errors = []

        try:
            # Intentar construir el schema Pydantic
            pydantic_schema = SchemaBuilderService.build_pydantic_schema(custom_schema)

            # Intentar convertir a JSON schema
            json_schema = SchemaBuilderService.to_json_schema(pydantic_schema)

            return {
                "valid": True,
                "message": f"Schema '{custom_schema.schema_name}' es válido",
                "json_schema": json_schema,
                "errors": None
            }

        except ValueError as e:
            errors.append(f"Error de validación: {str(e)}")
        except ImportError as e:
            errors.append(f"Error de dependencias: {str(e)}")
        except Exception as e:
            errors.append(f"Error inesperado: {str(e)}")

        return {
            "valid": False,
            "message": f"Schema '{custom_schema.schema_name}' es inválido",
            "json_schema": None,
            "errors": errors
        }
