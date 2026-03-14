from fastapi import FastAPI

from .routes import routes_user, routes_jd, routes_session, routes_health_check

app = FastAPI(title = "SkillIssue.ai")

app.include_router(routes_user.router, tags=["users"])
app.include_router(routes_jd.router, tags=["job_descriptions"])
app.include_router(routes_session.router, tags=["interviews"])
app.include_router(routes_health_check.router, tags=["health_check"])
