from fastapi import HTTPException
from ...database import get_collection
from ...models.interview_model import Interview
from ...config import settings

async def add_interview(interview_data: dict, collection_name: str = settings.COLLECTION_NAME) -> dict:
    try:
        interview_collection = await get_collection(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured in loading collection {e}")
    result = await interview_collection.insert_one(interview_data)
    interview_data["_id"] = result.inserted_id
    return interview_data