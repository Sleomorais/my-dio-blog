from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.controllers import auth, post
from fastapi import FastAPI, Request
from src.database import database
from src.exceptions import NotFoundPostError


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

servers=[
        {"url": "https://stag.example.com", "description": "Staging environment"},
        {"url": "https://prod.example.com", "description": "Production environment"},
    ]
tags_metadata = [
    {
        "name": "auth",
        "description": "Operações para autenticação.",
    },
    {
        "name": "posts",
        "description": "Operações para manter posts",
        "externalDocs": {
            "description": "Documentação externa para Posts.api",
            "url": "https://post-api.com/",
        },
    },
]

app = FastAPI(
    title="Blog API",
    version="1.0.3",
    summary="API para gerenciamento de posts",
    description='''
        A **API** permite criar, ler, atualizar e excluir posts.
        ''',
    openapi_tags=tags_metadata,
    servers=servers,
    redoc_url=None,
    # openapi_url=None, #disable openapi
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(post.router, tags=["posts"])

@app.exception_handler(NotFoundPostError)
async def not_found_exception_handler(request: Request, exc: NotFoundPostError):
    return JSONResponse(
        status_code=exc.status_code, 
        content={"detail": exc.message}
        )
