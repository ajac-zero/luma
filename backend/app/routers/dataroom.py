import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.dataroom import DataRoom
from ..models.vector_models import CollectionCreateRequest
from ..services.azure_service import azure_service
from ..services.vector_service import vector_service

logger = logging.getLogger(__name__)


class DataroomCreate(BaseModel):
    name: str

    @property
    def collection(self) -> str:
        return self.name.lower().replace(" ", "_")

    @property
    def storage(self) -> str:
        return self.name.lower().replace(" ", "_")


class DataroomInfo(BaseModel):
    name: str
    collection: str
    storage: str
    file_count: int
    total_size_bytes: int
    total_size_mb: float
    collection_exists: bool
    vector_count: Optional[int]
    collection_info: Optional[dict]
    file_types: dict
    recent_files: list


router = APIRouter(prefix="/dataroom", tags=["Dataroom"])


@router.get("/{dataroom_name}/info")
async def dataroom_info(dataroom_name: str) -> DataroomInfo:
    """
    Obtener información detallada de un dataroom específico
    """
    try:
        # Find the dataroom in Redis
        datarooms = DataRoom.find().all()
        dataroom = None
        for room in datarooms:
            if room.name == dataroom_name:
                dataroom = room
                break

        if not dataroom:
            raise HTTPException(
                status_code=404, detail=f"Dataroom '{dataroom_name}' not found"
            )

        # Get file information from Azure Storage
        try:
            files_data = await azure_service.list_files(dataroom_name)
        except Exception as e:
            logger.warning(f"Could not fetch files for dataroom '{dataroom_name}': {e}")
            files_data = []

        # Calculate file metrics
        file_count = len(files_data)
        total_size_bytes = sum(file_data.get("size", 0) for file_data in files_data)
        total_size_mb = (
            round(total_size_bytes / (1024 * 1024), 2) if total_size_bytes > 0 else 0.0
        )

        # Analyze file types
        file_types = {}
        recent_files = []

        for file_data in files_data:
            # Count file types by extension
            filename = file_data.get("name", "")
            if "." in filename:
                ext = filename.split(".")[-1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1

            # Collect recent files (up to 5)
            if len(recent_files) < 5:
                recent_files.append(
                    {
                        "name": filename,
                        "size_mb": round(file_data.get("size", 0) / (1024 * 1024), 2),
                        "last_modified": file_data.get("last_modified"),
                    }
                )

        # Sort recent files by last modified (newest first)
        recent_files.sort(key=lambda x: x.get("last_modified", ""), reverse=True)

        # Get vector collection information
        collection_exists = False
        vector_count = None
        collection_info = None

        try:
            collection_exists_response = await vector_service.check_collection_exists(
                dataroom_name
            )
            collection_exists = collection_exists_response.exists

            if collection_exists:
                collection_info_response = await vector_service.get_collection_info(
                    dataroom_name
                )
                if collection_info_response:
                    collection_info = {
                        "vectors_count": collection_info_response.vectors_count,
                        "indexed_vectors_count": collection_info_response.vectors_count,
                        "points_count": collection_info_response.vectors_count,
                        "segments_count": collection_info_response.vectors_count,
                        "status": collection_info_response.status,
                    }
                    vector_count = collection_info_response.vectors_count
        except Exception as e:
            logger.warning(
                f"Could not fetch collection info for '{dataroom_name}': {e}"
            )

        logger.info(
            f"Retrieved info for dataroom '{dataroom_name}': {file_count} files, {total_size_mb}MB"
        )

        return DataroomInfo(
            name=dataroom.name,
            collection=dataroom.collection,
            storage=dataroom.storage,
            file_count=file_count,
            total_size_bytes=total_size_bytes,
            total_size_mb=total_size_mb,
            collection_exists=collection_exists,
            vector_count=vector_count,
            collection_info=collection_info,
            file_types=file_types,
            recent_files=recent_files,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataroom info for '{dataroom_name}': {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting dataroom info: {str(e)}"
        )


@router.get("/")
async def list_datarooms():
    """
    Listar todos los temas disponibles
    """
    try:
        # Get all DataRoom instances
        datarooms: list[DataRoom] = DataRoom.find().all()
        logger.info(f"Found {len(datarooms)} datarooms in Redis")

        # Convert to list of dictionaries
        dataroom_list = [
            {"name": room.name, "collection": room.collection, "storage": room.storage}
            for room in datarooms
        ]

        logger.info(f"Returning dataroom list: {dataroom_list}")
        return {"datarooms": dataroom_list}
    except Exception as e:
        logger.error(f"Error listing datarooms: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error listing datarooms: {str(e)}"
        )


@router.post("/")
async def create_dataroom(dataroom: DataroomCreate):
    """
    Crear un nuevo dataroom y su colección vectorial asociada
    """
    try:
        # Create new DataRoom instance
        new_dataroom = DataRoom(
            name=dataroom.name, collection=dataroom.collection, storage=dataroom.storage
        )

        # Save to Redis
        new_dataroom.save()

        # Create the vector collection for this dataroom
        try:
            # First check if collection already exists
            collection_exists_response = await vector_service.check_collection_exists(
                dataroom.name
            )

            if not collection_exists_response.exists:
                # Only create if it doesn't exist
                collection_request = CollectionCreateRequest(
                    collection_name=dataroom.name,
                    vector_size=3072,  # Default vector size for embeddings
                    distance="Cosine",  # Default distance metric
                )
                await vector_service.create_collection(collection_request)
                logger.info(f"Collection '{dataroom.name}' created successfully")
            else:
                logger.info(
                    f"Collection '{dataroom.name}' already exists, skipping creation"
                )
        except Exception as e:
            # Log the error but don't fail the dataroom creation
            logger.warning(
                f"Could not create collection for dataroom '{dataroom.name}': {e}"
            )

        return {
            "message": "Dataroom created successfully",
            "dataroom": {
                "name": new_dataroom.name,
                "collection": new_dataroom.collection,
                "storage": new_dataroom.storage,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating dataroom: {str(e)}"
        )


@router.delete("/{dataroom_name}")
async def delete_dataroom(dataroom_name: str):
    """
    Eliminar un dataroom y su colección vectorial asociada
    """
    try:
        # First check if dataroom exists
        existing_datarooms = DataRoom.find().all()
        dataroom_exists = any(room.name == dataroom_name for room in existing_datarooms)

        if not dataroom_exists:
            raise HTTPException(
                status_code=404, detail=f"Dataroom '{dataroom_name}' not found"
            )

        # Delete the vector collection first
        try:
            collection_exists = await vector_service.check_collection_exists(
                dataroom_name
            )
            if collection_exists.exists:
                await vector_service.delete_collection(dataroom_name)
                logger.info(
                    f"Collection '{dataroom_name}' deleted from vector database"
                )
        except Exception as e:
            logger.warning(
                f"Could not delete collection '{dataroom_name}' from vector database: {e}"
            )
            # Continue with dataroom deletion even if collection deletion fails

        # Delete the dataroom from Redis
        for room in existing_datarooms:
            if room.name == dataroom_name:
                # Delete using the primary key
                DataRoom.delete(room.pk)
                logger.info(f"Dataroom '{dataroom_name}' deleted from Redis")
                break

        return {
            "message": "Dataroom deleted successfully",
            "dataroom_name": dataroom_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dataroom '{dataroom_name}': {e}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting dataroom: {str(e)}"
        )
