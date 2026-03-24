from typing import List
from fastapi import HTTPException
from ...database import get_collection
from ...config import settings

async def get_all_interviews(collection_name: str = settings.COLLECTION_NAME) -> List[dict]:
    try:
        interview_collection = await get_collection(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured in loading collection {e}")
    
    interviews = []
    async for interview in interview_collection.find({}):
        interviews.append(interview)
    return interviews