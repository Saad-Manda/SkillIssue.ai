from fastapi import HTTPException
from ...database import get_collection
from ...models.interview_model import Interview
from ...config import settings

async def add_interview(interview_data: Interview, collection_name: str = settings.COLLECTION_NAME) -> Interview:
    try:
        interview_collection = await get_collection(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured in loading collection {e}")
    interview_dict = interview_data.model_dump()
    result = await interview_collection.insert_one(interview_dict)
    interview_dict["_id"] = result.inserted_id
    return Interview.model_validate(interview_dict)

