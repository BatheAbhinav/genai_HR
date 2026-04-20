from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.documents import router as documents_router
from app.api.routers.query import router as query_router
from app.config.logging import configure_logging
from app.config.settings import settings
from app.db.bootstrap import init_database
from app.observability.phoenix import setup_phoenix


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_phoenix()
    init_database()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/ready")
def ready():
    return {"ready": True}


app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(query_router)
