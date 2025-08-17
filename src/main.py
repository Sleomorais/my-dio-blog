from contextlib import asynccontextmanager

from src.controllers import auth, post
from fastapi import FastAPI
from src.database import database, metadata, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.models.post import posts #noqa
    await database.connect()
    metadata.create_all(engine)
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(post.router)
