from fastapi import FastAPI
from app.api import upload

app = FastAPI(version='0.0.1')

app.include_router(upload.router)



@app.get("/")
async def root():
    return {"message": "Up and running"}