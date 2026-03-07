from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...models.jd_model import JobDescription as JobDescriptionModel
from ...schemas.jd import JobDescription as JobDescriptionSchema

async def get_jd(db: AsyncSession, jd_id: str):
    stmt = select(JobDescriptionSchema).where(JobDescriptionSchema.jd_id == jd_id)
    result = await db.execute(statement=stmt)
    jd_obj = result.scalar_one_or_none()
    
    if not jd_obj:
        return None
    return JobDescriptionModel.model_validate(jd_obj)
