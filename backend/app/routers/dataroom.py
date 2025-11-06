import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.dataroom import DataRoom
from ..models.vector_models import CollectionCreateRequest
from ..services.vector_service import vector_service

logger = logging.getLogger(__name__)


class DataroomCreate(BaseModel):
    name: str
    collection: str = ""
    storage: str = ""


router = APIRouter(prefix="/dataroom", tags=["Dataroom"])


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
