import logging
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.education import Education as EducationSchema
from ...schemas.experience import Experience as ExperienceSchema
from ...schemas.leadership import Leadership as LeadershipSchema
from ...schemas.project import Project as ProjectSchema
from ...schemas.user import User as UserSchema

logger = logging.getLogger(__name__)


def _parse_datetime(value):
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            try:
                return datetime.strptime(normalized, "%Y-%m-%d")
            except ValueError as exc:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid datetime value: {value}",
                ) from exc
    raise HTTPException(
        status_code=422,
        detail=f"Invalid datetime value type: {type(value).__name__}",
    )


def _normalize_date_fields(items: list, fields: tuple[str, ...]) -> list:
    normalized_items = []
    for item in items:
        updated_item = dict(item)
        for field in fields:
            if field in updated_item:
                updated_item[field] = _parse_datetime(updated_item[field])
        normalized_items.append(updated_item)
    return normalized_items


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

    # Replace experiences only if provided in patch payload
    if "experiences" in user_profile:
        await db.execute(
            delete(ExperienceSchema).where(ExperienceSchema.user_id == user_id)
        )
        experiences = _normalize_date_fields(
            user_profile.get("experiences") or [],
            ("start_date", "end_date"),
        )
        for experience in experiences:
            exp = ExperienceSchema(**experience, user_id=user_id)
            db.add(exp)

    # Replace educations only if provided in patch payload
    if "educations" in user_profile:
        await db.execute(
            delete(EducationSchema).where(EducationSchema.user_id == user_id)
        )
        educations = _normalize_date_fields(
            user_profile.get("educations") or [],
            ("start_date", "end_date"),
        )
        for education in educations:
            edu = EducationSchema(**education, user_id=user_id)
            db.add(edu)

    # Replace projects only if provided in patch payload
    if "projects" in user_profile:
        await db.execute(delete(ProjectSchema).where(ProjectSchema.user_id == user_id))
        for project in user_profile.get("projects") or []:
            proj = ProjectSchema(**project, user_id=user_id)
            db.add(proj)

    # Replace leaderships only if provided in patch payload
    if "leaderships" in user_profile:
        await db.execute(
            delete(LeadershipSchema).where(LeadershipSchema.user_id == user_id)
        )
        leaderships = _normalize_date_fields(
            user_profile.get("leaderships") or [],
            ("start_date", "end_date"),
        )
        for leadership in leaderships:
            lead = LeadershipSchema(**leadership, user_id=user_id)
            db.add(lead)

    await db.commit()
    logger.info("update_user_profile controller succeeded for user_id=%s", user_id)
    return True
