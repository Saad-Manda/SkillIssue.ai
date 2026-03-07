from fastapi import APIRouter, HTTPException
from ..controllers.health_check import health_check

router = APIRouter(prefix="/api/v1/health_check", tags=["health_check"])

@router.get("/")
def health_check_endpoint():
    return health_check()