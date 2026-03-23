import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .routes import (
    routes_auth,
    routes_health_check,
    routes_jd,
    routes_session,
    routes_user,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client, mongo_db
    mongo_client = MongoClient(os.getenv("ATLAS_DB_URI"))
    mongo_db = mongo_client["skillissue"]
    logging.info("MongoDB Connected....")

    yield

    mongo_client.close()
    logging.info("MongoDB connection closed")

app = FastAPI(title="SkillIssue.ai", lifespan=lifespan)

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
app.include_router(routes_session.router, tags=["interviews"])
app.include_router(routes_health_check.router, tags=["health_check"])
