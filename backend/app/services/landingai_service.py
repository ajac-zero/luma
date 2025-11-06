"""
LandingAI Service - Servicio independiente
Maneja toda la interacción con LandingAI ADE API.
Usa parse() para extracción de chunks y extract() para datos estructurados.
"""
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

from langchain_core.documents import Document

from ..models.schema_models import CustomSchema
from ..services.schema_builder_service import SchemaBuilderService

logger = logging.getLogger(__name__)


class LandingAIService:
    """
    Servicio para procesamiento de PDFs con LandingAI.

    Flujo:
    1. Parse PDF → obtener chunks estructurados + markdown
    2. Extract (opcional) → extraer datos según schema personalizado
    3. Process chunks → filtrar, enriquecer, controlar tokens
    4. Return Documents → listos para embeddings y Qdrant
    """

    def __init__(self, api_key: str, environment: str = "production"):
        """
        Inicializa el servicio LandingAI.

        Args:
            api_key: API key de LandingAI
            environment: "production" o "eu"

        Raises:
            ImportError: Si landingai-ade no está instalado
        """
        try:
            from landingai_ade import LandingAIADE

            self.client = LandingAIADE(
                apikey=api_key,
                environment=environment,
                timeout=480.0,  # 8 minutos para PDFs grandes
                max_retries=2
            )

            self.schema_builder = SchemaBuilderService()

            logger.info(f"LandingAIService inicializado (environment: {environment})")

        except ImportError:
            logger.error("landingai-ade no está instalado")
            raise ImportError(
                "Se requiere landingai-ade. Instalar con: pip install landingai-ade"
            )

    def process_pdf(
        self,
        pdf_bytes: bytes,
        file_name: str,
        custom_schema: Optional[CustomSchema] = None,
        include_chunk_types: Optional[List[str]] = None,
        model: str = "dpt-2-latest"
    ) -> Dict[str, Any]:
        """
        Procesa un PDF con LandingAI (modo rápido o con extracción).

        Args:
            pdf_bytes: Contenido del PDF en bytes
            file_name: Nombre del archivo
            custom_schema: Schema personalizado para extract (None = modo rápido)
            include_chunk_types: Tipos de chunks a incluir ["text", "table", "figure"]
            model: Modelo de LandingAI a usar

        Returns:
            Dict con:
            - chunks: List[Document] listos para embeddings
            - parse_metadata: Metadata del parse (páginas, duración, etc.)
            - extracted_data: Datos extraídos (si usó schema)
            - file_name: Nombre del archivo

        Raises:
            Exception: Si hay error en parse o extract
        """
        logger.info(f"=== Procesando PDF con LandingAI: {file_name} ===")
        logger.info(f"  Modo: {'Extracción' if custom_schema else 'Rápido'}")
        logger.info(f"  Tipos incluidos: {include_chunk_types or 'todos'}")

        # 1. Parse PDF
        parse_result = self._parse_pdf(pdf_bytes, file_name, model)

        # 2. Extract (si hay schema)
        extracted_data = None
        if custom_schema:
            logger.info(f"  Extrayendo datos con schema: {custom_schema.schema_name}")
            extracted_data = self._extract_data(
                parse_result["markdown"],
                custom_schema
            )

        # 3. Procesar chunks
        documents = self._process_chunks(
            parse_result,
            extracted_data,
            file_name,
            include_chunk_types
        )

        logger.info(f"=== Procesamiento completado: {len(documents)} chunks ===")

        return {
            "chunks": documents,
            "parse_metadata": parse_result["metadata"],
            "extracted_data": extracted_data,
            "file_name": file_name
        }

    def _parse_pdf(
        self,
        pdf_bytes: bytes,
        file_name: str,
        model: str
    ) -> Dict[str, Any]:
        """
        Parse PDF con LandingAI.

        Args:
            pdf_bytes: Contenido del PDF
            file_name: Nombre del archivo
            model: Modelo de LandingAI

        Returns:
            Dict con chunks, markdown, grounding y metadata
        """
        logger.info(f"  Parseando PDF con modelo {model}...")

        # LandingAI requiere Path, crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = Path(tmp.name)

        try:
            # Parse con LandingAI
            response = self.client.parse(document=tmp_path, model=model)

            # Procesar respuesta
            chunks_data = []
            for chunk in response.chunks:
                # Obtener grounding info del chunk
                grounding_info = {}
                if hasattr(response, 'grounding') and hasattr(response.grounding, chunk.id):
                    ground = getattr(response.grounding, chunk.id)
                    grounding_info = {
                        "bbox": ground.bbox if hasattr(ground, 'bbox') else None,
                        "page": ground.page if hasattr(ground, 'page') else 1
                    }

                page_num = grounding_info.get("page", 1) if grounding_info else 1

                chunks_data.append({
                    "id": chunk.id,
                    "content": chunk.markdown,
                    "type": chunk.type,
                    "grounding": grounding_info,
                    "page": page_num
                })

            # Obtener metadata
            metadata_dict = {}
            if hasattr(response, 'metadata'):
                metadata_dict = {
                    "page_count": getattr(response.metadata, 'page_count', None),
                    "duration_ms": getattr(response.metadata, 'duration_ms', None),
                    "version": getattr(response.metadata, 'version', None)
                }

            logger.info(
                f"  Parse completado: {len(chunks_data)} chunks, "
                f"{metadata_dict.get('page_count', 'N/A')} páginas"
            )

            return {
                "chunks": chunks_data,
                "markdown": response.markdown,
                "grounding": response.grounding,
                "metadata": metadata_dict
            }

        finally:
            # Limpiar archivo temporal
            tmp_path.unlink(missing_ok=True)

    def _extract_data(
        self,
        markdown: str,
        custom_schema: CustomSchema
    ) -> Optional[Dict[str, Any]]:
        """
        Extrae datos estructurados del markdown usando schema personalizado.

        Args:
            markdown: Markdown completo del documento
            custom_schema: Schema personalizado

        Returns:
            Dict con extraction, extraction_metadata y schema_used
            None si hay error
        """
        try:
            # 1. Construir Pydantic schema
            pydantic_schema = self.schema_builder.build_pydantic_schema(custom_schema)

            # 2. Convertir a JSON schema
            json_schema = self.schema_builder.to_json_schema(pydantic_schema)

            # 3. Crear archivo temporal con markdown
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=".md",
                delete=False,
                encoding='utf-8'
            ) as tmp:
                tmp.write(markdown)
                tmp_path = Path(tmp.name)

            try:
                # 4. Extract con LandingAI
                response = self.client.extract(
                    schema=json_schema,
                    markdown=tmp_path
                )

                logger.info(f"  Extracción completada: {len(response.extraction)} campos")

                return {
                    "extraction": response.extraction,
                    "extraction_metadata": response.extraction_metadata,
                    "schema_used": custom_schema.schema_id
                }

            finally:
                tmp_path.unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Error en extract: {e}")
            return None

    def _process_chunks(
        self,
        parse_result: Dict[str, Any],
        extracted_data: Optional[Dict[str, Any]],
        file_name: str,
        include_chunk_types: Optional[List[str]]
    ) -> List[Document]:
        """
        Convierte chunks de LandingAI a Documents de LangChain con metadata rica.

        Args:
            parse_result: Resultado del parse
            extracted_data: Datos extraídos (opcional)
            file_name: Nombre del archivo
            include_chunk_types: Tipos a incluir

        Returns:
            Lista de Documents listos para embeddings
        """
        documents = []
        filtered_count = 0

        for chunk in parse_result["chunks"]:
            # Filtrar por tipo si se especificó
            if include_chunk_types and chunk["type"] not in include_chunk_types:
                filtered_count += 1
                continue

            # Construir metadata rica
            metadata = {
                "file_name": file_name,
                "page": chunk["page"],
                "chunk_id": chunk["id"],
                "chunk_type": chunk["type"],
                "bbox": chunk["grounding"].get("bbox"),

                # Metadata del documento
                "document_metadata": {
                    "page_count": parse_result["metadata"].get("page_count"),
                    "processing_duration_ms": parse_result["metadata"].get("duration_ms"),
                    "landingai_version": parse_result["metadata"].get("version"),
                }
            }

            # Agregar datos extraídos si existen
            if extracted_data:
                metadata["extracted_data"] = extracted_data["extraction"]
                metadata["extraction_metadata"] = extracted_data["extraction_metadata"]
                metadata["schema_used"] = extracted_data["schema_used"]

            # Crear Document
            doc = Document(
                page_content=chunk["content"],
                metadata=metadata
            )
            documents.append(doc)

        if filtered_count > 0:
            logger.info(f"  Filtrados {filtered_count} chunks por tipo")

        logger.info(f"  Generados {len(documents)} documents")
        return documents


# Singleton factory
_landingai_service: Optional[LandingAIService] = None


def get_landingai_service() -> LandingAIService:
    """
    Factory para obtener instancia singleton del servicio.

    Returns:
        Instancia única de LandingAIService

    Raises:
        RuntimeError: Si la configuración no está disponible
    """
    global _landingai_service

    if _landingai_service is None:
        try:
            from ..core.config import settings

            api_key = settings.LANDINGAI_API_KEY
            if not api_key:
                raise ValueError("LANDINGAI_API_KEY no está configurada")

            environment = getattr(settings, 'LANDINGAI_ENVIRONMENT', 'production')

            _landingai_service = LandingAIService(
                api_key=api_key,
                environment=environment
            )

            logger.info("LandingAIService singleton inicializado")

        except Exception as e:
            logger.error(f"Error inicializando LandingAIService: {e}")
            raise RuntimeError(f"No se pudo inicializar LandingAIService: {str(e)}")

    return _landingai_service
