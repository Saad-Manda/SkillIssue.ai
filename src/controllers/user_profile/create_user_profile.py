import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from typing import Optional, List
from fastapi import HTTPException

from ...models.user_model import User as UserModel
from ...schemas.user import User as UserSchema
from ...schemas.experience import Experience as ExperienceSchema
from ...schemas.education import Education as EducationSchema
from ...schemas.project import Project as ProjectSchema
from ...schemas.leadership import Leadership as LeadershipSchema

async def create_user_profile(db: AsyncSession, user_profile: dict):
    user = UserSchema(
        user_id = str(uuid4()),
        name = user_profile.get("name"),
        email = user_profile.get("email"),
        mobile = user_profile.get("mobile"),
        github_url = user_profile.get("github_url"),
        linkedin_url = user_profile.get("linkedin_url"),
        skills = user_profile.get("skills", [])
    )
    db.add(user)

    for experience in user_profile.get("experiences", []):
        exp = ExperienceSchema(
            experience_id = str(uuid4()),
            role = experience.get("role"),
            company = experience.get("company"),
            emp_type = experience.get("emp_type"),
            loc_type = experience.get("loc_type"),
            skills_used = experience.get("skills_used", []),
            start_date = experience.get("start_date"),
            end_date = experience.get("end_date"),
            location = experience.get("location"),
            description = experience.get("description"),
            
            user_id = user.user_id
        )
        db.add(exp)


    for education in user_profile.get("educations", []):
        edu = EducationSchema(
            education_id = str(uuid4()),
            institute_name = education.get("institute_name"),
            degree = education.get("degree"),
            courses = education.get("courses", []),
            start_date = education.get("start_date"),
            end_date = education.get("end_date"),

            user_id = user.user_id
        )
        db.add(edu)


    for project in user_profile.get("projects", []):
        proj = ProjectSchema(
            project_id = str(uuid4()),
            title = project.get("title"),
            description = project.get("description"),
            skills_used = project.get("skills_used", []),
            github_url = project.get("github_url"),
            deployed_url = project.get("deployed_url"),

            user_id = user.user_id
        )
        db.add(proj)


    for leadership in user_profile.get("leaderships", []):
        lead = LeadershipSchema(
            leadership_id = str(uuid4()),
            committee_name = leadership.get("committee_name"),
            position = leadership.get("position"),
            skills_used = leadership.get("skills_used", []),
            description = leadership.get("description"),
            start_date = leadership.get("start_date"),
            end_date = leadership.get("end_date"),

            user_id = user.user_id
        )
        db.add(lead)

    await db.commit()
    await db.refresh(user)
    return user