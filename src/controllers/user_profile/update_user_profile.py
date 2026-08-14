import logging
from datetime import date, datetime
from uuid import uuid4

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
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=422,
                detail="Invalid payload item type. Each item must be an object.",
            )
        updated_item = dict(item)
        for field in fields:
            if field in updated_item:
                updated_item[field] = _parse_datetime(updated_item[field])
        normalized_items.append(updated_item)
    return normalized_items


async def _sync_experiences(db: AsyncSession, user_id: str, experiences_payload: list):
    experiences = _normalize_date_fields(experiences_payload, ("start_date", "end_date"))
    result = await db.execute(select(ExperienceSchema).where(ExperienceSchema.user_id == user_id))
    existing = {row.experience_id: row for row in result.scalars().all()}
    seen_ids = set()
    allowed_fields = {
        "role",
        "company",
        "emp_type",
        "loc_type",
        "skills_used",
        "start_date",
        "end_date",
        "location",
        "description",
    }

    for experience in experiences:
        experience_id = experience.pop("experience_id", None)
        payload = {field: value for field, value in experience.items() if field in allowed_fields}
        if experience_id:
            existing_row = existing.get(experience_id)
            if not existing_row:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid experience_id for user: {experience_id}",
                )
            for field, value in payload.items():
                setattr(existing_row, field, value)
            seen_ids.add(experience_id)
            continue

        db.add(
            ExperienceSchema(
                experience_id=str(uuid4()),
                user_id=user_id,
                **payload,
            )
        )

    ids_to_delete = [exp_id for exp_id in existing if exp_id not in seen_ids]
    if ids_to_delete:
        await db.execute(
            delete(ExperienceSchema).where(ExperienceSchema.experience_id.in_(ids_to_delete))
        )


async def _sync_educations(db: AsyncSession, user_id: str, educations_payload: list):
    educations = _normalize_date_fields(educations_payload, ("start_date", "end_date"))
    result = await db.execute(select(EducationSchema).where(EducationSchema.user_id == user_id))
    existing = {row.education_id: row for row in result.scalars().all()}
    seen_ids = set()
    allowed_fields = {
        "institute_name",
        "degree",
        "grade",
        "courses",
        "start_date",
        "end_date",
    }

    for education in educations:
        education_id = education.pop("education_id", None)
        payload = {field: value for field, value in education.items() if field in allowed_fields}
        if education_id:
            existing_row = existing.get(education_id)
            if not existing_row:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid education_id for user: {education_id}",
                )
            for field, value in payload.items():
                setattr(existing_row, field, value)
            seen_ids.add(education_id)
            continue

        db.add(
            EducationSchema(
                education_id=str(uuid4()),
                user_id=user_id,
                **payload,
            )
        )

    ids_to_delete = [edu_id for edu_id in existing if edu_id not in seen_ids]
    if ids_to_delete:
        await db.execute(
            delete(EducationSchema).where(EducationSchema.education_id.in_(ids_to_delete))
        )


async def _sync_projects(db: AsyncSession, user_id: str, projects_payload: list):
    if any(not isinstance(project, dict) for project in projects_payload):
        raise HTTPException(
            status_code=422,
            detail="Invalid payload item type. Each item must be an object.",
        )

    result = await db.execute(select(ProjectSchema).where(ProjectSchema.user_id == user_id))
    existing = {row.project_id: row for row in result.scalars().all()}
    seen_ids = set()
    allowed_fields = {"title", "description", "skills_used", "github_url", "deployed_url"}

    for project in projects_payload:
        payload = dict(project)
        project_id = payload.pop("project_id", None)
        payload = {field: value for field, value in payload.items() if field in allowed_fields}
        if project_id:
            existing_row = existing.get(project_id)
            if not existing_row:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid project_id for user: {project_id}",
                )
            for field, value in payload.items():
                setattr(existing_row, field, value)
            seen_ids.add(project_id)
            continue

        db.add(ProjectSchema(project_id=str(uuid4()), user_id=user_id, **payload))

    ids_to_delete = [proj_id for proj_id in existing if proj_id not in seen_ids]
    if ids_to_delete:
        await db.execute(
            delete(ProjectSchema).where(ProjectSchema.project_id.in_(ids_to_delete))
        )


async def _sync_leaderships(db: AsyncSession, user_id: str, leaderships_payload: list):
    leaderships = _normalize_date_fields(leaderships_payload, ("start_date", "end_date"))
    result = await db.execute(
        select(LeadershipSchema).where(LeadershipSchema.user_id == user_id)
    )
    existing = {row.leadership_id: row for row in result.scalars().all()}
    seen_ids = set()
    allowed_fields = {
        "committee_name",
        "position",
        "skills_used",
        "description",
        "start_date",
        "end_date",
    }

    for leadership in leaderships:
        leadership_id = leadership.pop("leadership_id", None)
        payload = {field: value for field, value in leadership.items() if field in allowed_fields}
        if leadership_id:
            existing_row = existing.get(leadership_id)
            if not existing_row:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid leadership_id for user: {leadership_id}",
                )
            for field, value in payload.items():
                setattr(existing_row, field, value)
            seen_ids.add(leadership_id)
            continue

        db.add(
            LeadershipSchema(
                leadership_id=str(uuid4()),
                user_id=user_id,
                **payload,
            )
        )

    ids_to_delete = [lead_id for lead_id in existing if lead_id not in seen_ids]
    if ids_to_delete:
        await db.execute(
            delete(LeadershipSchema).where(LeadershipSchema.leadership_id.in_(ids_to_delete))
        )


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

    # Sync experiences only if provided in patch payload
    if "experiences" in user_profile:
        await _sync_experiences(db, user_id, user_profile.get("experiences") or [])

    # Sync educations only if provided in patch payload
    if "educations" in user_profile:
        await _sync_educations(db, user_id, user_profile.get("educations") or [])

    # Sync projects only if provided in patch payload
    if "projects" in user_profile:
        await _sync_projects(db, user_id, user_profile.get("projects") or [])

    # Sync leaderships only if provided in patch payload
    if "leaderships" in user_profile:
        await _sync_leaderships(db, user_id, user_profile.get("leaderships") or [])

    await db.commit()
    logger.info("update_user_profile controller succeeded for user_id=%s", user_id)
    return True
