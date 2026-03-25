from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from ...database import get_collection
from ...config import settings

async def delete_interview(interview_id: str, collection_name: str = settings.COLLECTION_NAME) -> dict:
    try:
        oid = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid interview_id")

    try:
        collection = await get_collection(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured in loading collection {e}")
    
    result = await collection.delete_one({"_id": oid})
    
    return result