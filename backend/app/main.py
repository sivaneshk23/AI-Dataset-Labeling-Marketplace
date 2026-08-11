from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.datasets import router as dataset_router


app = FastAPI(
    title="AI Dataset Labeling Marketplace API",
    description=(
        "Backend API for the AI Dataset "
        "Labeling Marketplace."
    ),
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(dataset_router)


@app.get("/")
def root():
    return {
        "message": "AI Dataset Labeling Marketplace API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }