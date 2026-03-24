from fastapi import HTTPException
from ...database import get_collection

async def get_interview(interview_id: str, collection_name: str) -> dict:
    try:
        interview_collection = await get_collection(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured in loading collection {e}")
    
    interview = interview_collection.findOne({'_id': interview_id})
    return interview