import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.jd_model import JobDescription as JobDescriptionModel
from ...schemas.jd import JobDescription as JobDescriptionSchema

logger = logging.getLogger(__name__)


async def get_jd(db: AsyncSession, jd_id: str):
    logger.info("get_jd controller called for jd_id=%s", jd_id)
    stmt = select(JobDescriptionSchema).where(JobDescriptionSchema.jd_id == jd_id)
    result = await db.execute(statement=stmt)
    jd_obj = result.scalar_one_or_none()

    if not jd_obj:
        logger.warning("get_jd controller not found for jd_id=%s", jd_id)
        return None
    response = JobDescriptionModel.model_validate(jd_obj)
    logger.info("get_jd controller succeeded for jd_id=%s", jd_id)
    return response
