from fastapi import FastAPI


app = FastAPI(
    title="AI Dataset Labeling Marketplace API",
    description=(
        "Backend API for the AI Dataset "
        "Labeling Marketplace."
    ),
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Dataset Labeling Marketplace API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }