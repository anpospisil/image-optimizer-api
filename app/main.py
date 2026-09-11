import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import process

app = FastAPI(
    title="Image Optimizer API",
    description="Resize, crop, watermark, and optionally apply content moderation to images for social media platforms.",
    version="0.1.0",
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.head("/health")
def health_check_head():
    return {"status": "ok"}