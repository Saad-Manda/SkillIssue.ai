import logging

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user_model import User as UserModel
from ...schemas.education import Education as EducationSchema
from ...schemas.experience import Experience as ExperienceSchema
from ...schemas.leadership import Leadership as LeadershipSchema
from ...schemas.project import Project as ProjectSchema
from ...schemas.user import User as UserSchema

logger = logging.getLogger(__name__)


async def update_user_profile(db: AsyncSession, user_id: str, user_profile: dict):
    logger.info("update_user_profile controller called for user_id=%s", user_id)
    # Fetch the existing user
    query = select(UserSchema).where(UserSchema.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(
            "update_user_profile controller not found for user_id=%s", user_id
        )
        raise HTTPException(status_code=404, detail="User not found")

    # Update user's basic information
    user.name = user_profile.get("name", user.name)
    user.username = user_profile.get("username", user.username)
    user.email = user_profile.get("email", user.email)
    user.hashed_password = user_profile.get("hashed_password", user.hashed_password)
    user.is_active = user_profile.get("is_active", user.is_active)
    user.mobile = user_profile.get("mobile", user.mobile)
    user.github_url = user_profile.get("github_url", user.github_url)
    user.linkedin_url = user_profile.get("linkedin_url", user.linkedin_url)
    user.skills = user_profile.get("skills", user.skills)

    # Delete existing related records
    await db.execute(
        delete(ExperienceSchema).where(ExperienceSchema.user_id == user_id)
    )
    await db.execute(delete(EducationSchema).where(EducationSchema.user_id == user_id))
    await db.execute(delete(ProjectSchema).where(ProjectSchema.user_id == user_id))
    await db.execute(
        delete(LeadershipSchema).where(LeadershipSchema.user_id == user_id)
    )

    # Add updated experiences
    for experience in user_profile.get("experiences", []):
        exp = ExperienceSchema(**experience, user_id=user_id)
        db.add(exp)

    # Add updated educations
    for education in user_profile.get("educations", []):
        edu = EducationSchema(**education, user_id=user_id)
        db.add(edu)

    # Add updated projects
    for project in user_profile.get("projects", []):
        proj = ProjectSchema(**project, user_id=user_id)
        db.add(proj)

    # Add updated leaderships
    for leadership in user_profile.get("leaderships", []):
        lead = LeadershipSchema(**leadership, user_id=user_id)
        db.add(lead)

    await db.commit()
    logger.info("update_user_profile controller succeeded for user_id=%s", user_id)
    return True
