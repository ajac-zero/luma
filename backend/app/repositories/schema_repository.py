"""
Schema Repository - Patrón Repository
Abstrae la persistencia de schemas, actualmente usando archivos JSON.
Fácil migrar a base de datos después.
"""
import logging
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..models.schema_models import CustomSchema

logger = logging.getLogger(__name__)


class SchemaRepository:
    """
    Repository para gestión de schemas.
    Implementa patrón Repository para abstraer almacenamiento.

    Actualmente usa archivos JSON en disco.
    Para migrar a DB: solo cambiar esta clase, resto del código no cambia.
    """

    def __init__(self, schemas_dir: Path):
        """
        Inicializa el repositorio.

        Args:
            schemas_dir: Directorio donde se guardan los schemas
        """
        self.schemas_dir = Path(schemas_dir)
        self.schemas_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"SchemaRepository inicializado en: {self.schemas_dir}")

    def save(self, schema: CustomSchema) -> CustomSchema:
        """
        Guarda o actualiza un schema.

        Args:
            schema: Schema a guardar

        Returns:
            Schema guardado con timestamps actualizados

        Raises:
            IOError: Si hay error escribiendo el archivo
        """
        try:
            # Actualizar timestamps
            now = datetime.utcnow().isoformat()
            if not schema.created_at:
                schema.created_at = now
            schema.updated_at = now

            # Guardar archivo
            file_path = self._get_file_path(schema.schema_id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema.model_dump(), f, indent=2, ensure_ascii=False)

            logger.info(f"Schema guardado: {schema.schema_id} - {schema.schema_name}")
            return schema

        except Exception as e:
            logger.error(f"Error guardando schema {schema.schema_id}: {e}")
            raise IOError(f"No se pudo guardar el schema: {str(e)}")

    def get_by_id(self, schema_id: str) -> Optional[CustomSchema]:
        """
        Obtiene un schema por su ID.

        Args:
            schema_id: ID del schema

        Returns:
            Schema si existe, None si no

        Raises:
            ValueError: Si el archivo está corrupto
        """
        try:
            file_path = self._get_file_path(schema_id)
            if not file_path.exists():
                logger.debug(f"Schema no encontrado: {schema_id}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            schema = CustomSchema(**data)
            logger.debug(f"Schema cargado: {schema_id}")
            return schema

        except json.JSONDecodeError as e:
            logger.error(f"Archivo JSON corrupto para schema {schema_id}: {e}")
            raise ValueError(f"Schema corrupto: {schema_id}")
        except Exception as e:
            logger.error(f"Error cargando schema {schema_id}: {e}")
            return None

    def list_all(self) -> List[CustomSchema]:
        """
        Lista todos los schemas disponibles.

        Returns:
            Lista de schemas ordenados por fecha de creación (más reciente primero)
        """
        schemas = []

        try:
            for file_path in self.schemas_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    schema = CustomSchema(**data)
                    schemas.append(schema)
                except Exception as e:
                    logger.warning(f"Error cargando schema desde {file_path}: {e}")
                    continue

            # Ordenar por fecha de creación (más reciente primero)
            schemas.sort(key=lambda s: s.created_at or "", reverse=True)

            logger.info(f"Listados {len(schemas)} schemas")
            return schemas

        except Exception as e:
            logger.error(f"Error listando schemas: {e}")
            return []

    def list_by_tema(self, tema: str) -> List[CustomSchema]:
        """
        Lista schemas disponibles para un tema específico.
        Incluye schemas del tema + schemas globales.

        Args:
            tema: Nombre del tema

        Returns:
            Lista de schemas aplicables al tema
        """
        all_schemas = self.list_all()

        filtered = [
            schema for schema in all_schemas
            if schema.tema == tema or schema.is_global
        ]

        logger.info(f"Encontrados {len(filtered)} schemas para tema '{tema}'")
        return filtered

    def delete(self, schema_id: str) -> bool:
        """
        Elimina un schema.

        Args:
            schema_id: ID del schema a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        try:
            file_path = self._get_file_path(schema_id)
            if not file_path.exists():
                logger.warning(f"Intento de eliminar schema inexistente: {schema_id}")
                return False

            file_path.unlink()
            logger.info(f"Schema eliminado: {schema_id}")
            return True

        except Exception as e:
            logger.error(f"Error eliminando schema {schema_id}: {e}")
            raise IOError(f"No se pudo eliminar el schema: {str(e)}")

    def exists(self, schema_id: str) -> bool:
        """
        Verifica si un schema existe.

        Args:
            schema_id: ID del schema

        Returns:
            True si existe, False si no
        """
        file_path = self._get_file_path(schema_id)
        return file_path.exists()

    def count(self) -> int:
        """
        Cuenta el número total de schemas.

        Returns:
            Número de schemas
        """
        return len(list(self.schemas_dir.glob("*.json")))

    def _get_file_path(self, schema_id: str) -> Path:
        """
        Obtiene la ruta del archivo para un schema.

        Args:
            schema_id: ID del schema

        Returns:
            Path del archivo
        """
        # Sanitizar schema_id para evitar path traversal
        safe_id = schema_id.replace("/", "_").replace("\\", "_")
        return self.schemas_dir / f"{safe_id}.json"


# Singleton factory pattern
_schema_repository: Optional[SchemaRepository] = None


def get_schema_repository() -> SchemaRepository:
    """
    Factory para obtener instancia singleton del repositorio.

    Returns:
        Instancia única de SchemaRepository

    Raises:
        RuntimeError: Si la configuración no está disponible
    """
    global _schema_repository

    if _schema_repository is None:
        try:
            from ..core.config import settings

            schemas_dir = getattr(settings, 'SCHEMAS_DIR', None) or "./data/schemas"
            _schema_repository = SchemaRepository(Path(schemas_dir))

            logger.info("SchemaRepository singleton inicializado")

        except Exception as e:
            logger.error(f"Error inicializando SchemaRepository: {e}")
            raise RuntimeError(f"No se pudo inicializar SchemaRepository: {str(e)}")

    return _schema_repository
