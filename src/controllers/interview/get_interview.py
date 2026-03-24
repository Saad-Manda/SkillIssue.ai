from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from ...database import get_collection
from ...config import settings

async def get_interview(interview_id: str, collection_name: str = settings.COLLECTION_NAME) -> dict:
    try:
        oid = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid interview_id")

    interview = await collection.find_one({"_id": oid})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    interview["_id"] = str(interview["_id"])
    return interview