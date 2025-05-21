import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes import router as api_router
from core.config import settings

print("CELERY_BROKER_URL: main ", os.getenv("CELERY_BROKER_URL"))
print("CELERY_RESULT_BACKEND: main", os.getenv("CELERY_RESULT_BACKEND"))
print("hello: ", os.getenv("MODEL_WEIGHTS_PATH"))
print("aw", os.getenv("PIXEL_SIZE_MM"))


# Create FastAPI app
app = FastAPI(
    title="Rock Fragment Analysis API",
    description="API for rock fragment analysis using Mask R-CNN",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Rock Fragment Analysis API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
