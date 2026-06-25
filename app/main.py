from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import process

app = FastAPI(
    title="Image Optimizer API",
    description="Resize, crop, watermark, and optionally apply content moderation to images for social media platforms.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # Next.js dev
           "http://localhost:3001",
        "https://your-app.vercel.app", # Replace with your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
