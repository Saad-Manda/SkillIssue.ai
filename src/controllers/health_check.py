import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def health_check():
    logger.info("health_check controller called")
    try:
        response = {"message": "health check passed"}
        logger.info("health_check controller succeeded")
        return response
    except Exception as e:
        logger.exception("health_check controller failed")
        raise HTTPException(status_code=500, detail={"error": f"Server error {e}"})
