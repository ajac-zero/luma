"""
Router para consultar datos extraídos almacenados en Redis.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..services.extracted_data_service import get_extracted_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/extracted-data", tags=["extracted-data"])


class ExtractedDataResponse(BaseModel):
    """Response con datos extraídos de un documento"""
    pk: str
    file_name: str
    tema: str
    collection_name: str
    extracted_data: dict
    extraction_timestamp: str


class ExtractedDataListResponse(BaseModel):
    """Response con lista de datos extraídos"""
    total: int
    documents: List[ExtractedDataResponse]


@router.get("/by-file/{file_name}", response_model=ExtractedDataListResponse)
async def get_by_file(file_name: str):
    """
    Obtiene todos los datos extraídos de un archivo específico.

    Args:
        file_name: Nombre del archivo

    Returns:
        Lista de documentos con datos extraídos
    """
    try:
        service = get_extracted_data_service()
        docs = await service.get_by_file(file_name)

        documents = [
            ExtractedDataResponse(
                pk=doc.pk,
                file_name=doc.file_name,
                tema=doc.tema,
                collection_name=doc.collection_name,
                extracted_data=doc.get_extracted_data(),
                extraction_timestamp=doc.extraction_timestamp
            )
            for doc in docs
        ]

        return ExtractedDataListResponse(
            total=len(documents),
            documents=documents
        )

    except Exception as e:
        logger.error(f"Error obteniendo datos extraídos por archivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-tema/{tema}", response_model=ExtractedDataListResponse)
async def get_by_tema(tema: str):
    """
    Obtiene todos los datos extraídos de un tema específico.

    Args:
        tema: Nombre del tema

    Returns:
        Lista de documentos con datos extraídos
    """
    try:
        service = get_extracted_data_service()
        docs = await service.get_by_tema(tema)

        documents = [
            ExtractedDataResponse(
                pk=doc.pk,
                file_name=doc.file_name,
                tema=doc.tema,
                collection_name=doc.collection_name,
                extracted_data=doc.get_extracted_data(),
                extraction_timestamp=doc.extraction_timestamp
            )
            for doc in docs
        ]

        return ExtractedDataListResponse(
            total=len(documents),
            documents=documents
        )

    except Exception as e:
        logger.error(f"Error obteniendo datos extraídos por tema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-collection/{collection_name}", response_model=ExtractedDataListResponse)
async def get_by_collection(collection_name: str):
    """
    Obtiene todos los datos extraídos de una colección específica.

    Args:
        collection_name: Nombre de la colección

    Returns:
        Lista de documentos con datos extraídos
    """
    try:
        service = get_extracted_data_service()
        docs = await service.get_by_collection(collection_name)

        documents = [
            ExtractedDataResponse(
                pk=doc.pk,
                file_name=doc.file_name,
                tema=doc.tema,
                collection_name=doc.collection_name,
                extracted_data=doc.get_extracted_data(),
                extraction_timestamp=doc.extraction_timestamp
            )
            for doc in docs
        ]

        return ExtractedDataListResponse(
            total=len(documents),
            documents=documents
        )

    except Exception as e:
        logger.error(f"Error obteniendo datos extraídos por colección: {e}")
        raise HTTPException(status_code=500, detail=str(e))
