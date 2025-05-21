from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import io
import uuid
from PIL import Image
import numpy as np
import cv2
import time
import os

from core.celery_app import celery_app
from models.schema import TaskResponse, TaskStatusResponse
from services.model_service import get_predictor

router = APIRouter()

# Task storage (in a real app, use Redis or a database)
tasks = {}

# print("CELERY_BROKER_URL: routes ", os.getenv("CELERY_BROKER_URL"))
# print("CELERY_RESULT_BACKEND: routes", os.getenv("CELERY_RESULT_BACKEND"))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array (BGR for OpenCV)
        img_array = np.array(image)
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            # Handle grayscale or RGBA images
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create Celery task
        task = celery_app.send_task(
            "tasks.inference_tasks.process_image",
            args=[img_bgr.tolist()],  # Convert numpy array to list for serialization
            task_id=task_id
        )
        
        # Store task info
        tasks[task_id] = {
            "status": "PENDING",
            "result": None
        }
        
        return JSONResponse(
            status_code=202,
            content={"task_id": task_id, "status": "Task created"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    # Print for debugging
    print(f"Checking task status for: {task_id}")
    
    # Get task result directly from Celery
    task = celery_app.AsyncResult(task_id)
    
    # Print task state for debugging
    print(f"Task state: {task.state}")
    if task.ready():
        print("Task is ready, getting result")
        try:
            result = task.get()
            print(f"Result: {result}")
            return {"status": "SUCCESS", "result": result}
        except Exception as e:
            print(f"Error getting result: {e}")
            return {"status": "FAILURE", "result": str(e)}
    else:
        print(f"Task not ready, state: {task.state}")
        return {"status": "PENDING", "result": None}
    