import logging

from fastapi import APIRouter, HTTPException

from ..controllers.health_check import health_check

router = APIRouter(prefix="/api/v1/health_check", tags=["health_check"])
logger = logging.getLogger(__name__)


@router.get("/")
def health_check_endpoint():
    logger.info("health_check_endpoint called")
    response = health_check()
    logger.info("health_check_endpoint succeeded")
    return response
