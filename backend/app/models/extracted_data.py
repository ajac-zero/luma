"""
Modelo Redis-OM para almacenar datos extraídos de documentos.
Permite búsqueda rápida de datos estructurados sin necesidad de búsqueda vectorial.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from redis_om import HashModel, Field, Migrator
import json


class ExtractedDocument(HashModel):
    """
    Modelo para guardar datos extraídos de documentos en Redis.

    Uso:
    1. Cuando se procesa un PDF con schema y se extraen datos
    2. Los chunks van a Qdrant (para RAG)
    3. Los datos extraídos van a Redis (para búsqueda estructurada)

    Ventajas:
    - Búsqueda rápida por file_name, tema, collection_name
    - Acceso directo a datos extraídos sin búsqueda vectorial
    - Permite filtros y agregaciones
    """

    # Identificadores
    file_name: str = Field(index=True)
    tema: str = Field(index=True)
    collection_name: str = Field(index=True)

    # Datos extraídos (JSON serializado)
    # Redis-OM HashModel no soporta Dict directamente, usamos str y serializamos
    extracted_data_json: str

    # Metadata
    extraction_timestamp: str  # ISO format

    class Meta:
        database = None  # Se configura en runtime
        global_key_prefix = "extracted_doc"
        model_key_prefix = "doc"

    def set_extracted_data(self, data: Dict[str, Any]) -> None:
        """Helper para serializar datos extraídos a JSON"""
        self.extracted_data_json = json.dumps(data, ensure_ascii=False, indent=2)

    def get_extracted_data(self) -> Dict[str, Any]:
        """Helper para deserializar datos extraídos desde JSON"""
        return json.loads(self.extracted_data_json)

    @classmethod
    def find_by_file(cls, file_name: str):
        """Busca todos los documentos extraídos de un archivo"""
        return cls.find(cls.file_name == file_name).all()

    @classmethod
    def find_by_tema(cls, tema: str):
        """Busca todos los documentos extraídos de un tema"""
        return cls.find(cls.tema == tema).all()

    @classmethod
    def find_by_collection(cls, collection_name: str):
        """Busca todos los documentos en una colección"""
        return cls.find(cls.collection_name == collection_name).all()


# Ejecutar migración para crear índices en Redis
Migrator().run()
