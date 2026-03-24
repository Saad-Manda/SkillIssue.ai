import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import (
    routes_auth,
    routes_health_check,
    routes_jd,
    routes_session,
    routes_user,
    routes_interview
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(title="SkillIssue.ai")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, tags=["auth"])
app.include_router(routes_user.router, tags=["users"])
app.include_router(routes_jd.router, tags=["job_descriptions"])
app.include_router(routes_session.router, tags=["sessions"])
app.include_router(routes_interview.router, tags=["interviews"])
app.include_router(routes_health_check.router, tags=["health_check"])
