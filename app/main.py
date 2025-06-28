from fastapi import FastAPI
from app.api import upload
from contextlib import asynccontextmanager
from app.db.index import init_indexes
from app import initialize_rag_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_indexes()
    initialize_rag_settings()


app = FastAPI(version="0.0.1", lifespan=lifespan)

app.include_router(upload.router)


@app.get("/")
async def root():
    return {"message": "Up and running"}
