from contextlib import asynccontextmanager
from typing import AsyncGenerator

import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.middleware import LoggingMiddleware
from app.routers import auth, calendar_events, chat_rooms, families, media, members


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Initialize Firebase Admin SDK once at startup
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    yield


app = FastAPI(
    title="Family App API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(LoggingMiddleware)

_ALLOWED_ORIGINS = (
    ["http://localhost:3000"]
    if not settings.is_production
    else settings.ALLOWED_ORIGINS
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(families.router, prefix="/api/v1/families", tags=["families"])
app.include_router(members.router, prefix="/api/v1/families", tags=["members"])
app.include_router(chat_rooms.router, prefix="/api/v1/families", tags=["chat"])
app.include_router(calendar_events.router, prefix="/api/v1/families", tags=["calendar"])
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
