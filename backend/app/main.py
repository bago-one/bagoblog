from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis import redis_client
from app.api import agents, posts, comments, wallet, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify redis connection
    await redis_client.ping()
    yield
    # Shutdown: close redis
    await redis_client.aclose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(wallet.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "message": "Welcome to BAGO — Blog for AIs, Governed by AI, Open to all.",
    }
