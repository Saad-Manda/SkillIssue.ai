from typing import List
from fastapi import HTTPException
from ...database import get_collection
from ...config import settings

async def get_all_interviews(user_id: str, collection_name: str = settings.COLLECTION_NAME) -> List[dict]:
    try:
        interview_collection = await get_collection(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured in loading collection {e}")
    
    interviews = []
    async for interview in interview_collection.find({"user_id": user_id}):
        if "_id" in interview:
            interview["_id"] = str(interview["_id"])
        interviews.append(interview)
    return interviews