from contextlib import asynccontextmanager

from fastapi import FastAPI

from atlas.db import SessionLocal, engine, ensure_database_current

# Database imports
from atlas.routes import router
from atlas.services.format_versions import ensure_format_version_set


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database_current(engine)
    with SessionLocal() as db:
        ensure_format_version_set(db)
        db.commit()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
