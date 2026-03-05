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
        user_id = uuid4(),
        name = user_profile["name"],
        email = user_profile["email"],
        mobile = user_profile["mobile"],
        github_url = user_profile["github_url"],
        linkedin_url = user_profile["linkedin_url"],
        skills = user_profile["skills"]
    )
    db.add(user)

    for experience in user_profile["experiences"]:
        exp = ExperienceSchema(
            experience_id = uuid4(),
            role = experience["role"],
            company = experience["company"],
            emp_type = experience["emp_type"],
            loc_type = experience["loc_type"],
            skills_used = experience["skills_used"],
            start_date = experience["start_date"],
            end_date = experience["end_date"],
            location = experience["location"],
            description = experience["description"],
            
            user_id = user.user_id
        )
        db.add(exp)


    for education in user_profile["educations"]:
        edu = EducationSchema(
            education_id = uuid4(),
            institute_name = education["institute_name"],
            degree = education["degree"],
            courses = education["courses"],
            start_date = education["start_date"],
            end_date = education["end_date"],

            user_id = user.user_id
        )
        db.add(edu)


    for project in user_profile["projects"]:
        proj = ProjectSchema(
            project_id = uuid4(),
            title = project["title"],
            description = project["description"],
            skills_used = project["skills_used"],
            github_url = project["github_url"],
            deployed_url = project["deployed_url"],

            user_id = user.user_id
        )
        db.add(proj)


    for leadership in user_profile["leaderships"]:
        lead = LeadershipSchema(
            leadership_id = uuid4(),
            committee_name = leadership["committee_name"],
            position = leadership["position"],
            skills_used = leadership["skills_used"],
            description = leadership["description"],
            start_date = leadership["start_date"],
            end_date = leadership["end_date"],

            user_id = user.user_id
        )
        db.add(lead)

    await db.commit()
    return True