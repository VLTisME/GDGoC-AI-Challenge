from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

class TaskResponse(BaseModel):
    """Response model for task creation"""
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    status: str
    result: Optional[Dict[str, Any]] = None

class PredictionResult(BaseModel):
    """Model for prediction results"""
    segmentation_image: str  # Base64 encoded image
    cdf_plot: str  # Base64 encoded image
    fragment_count: int
    stats: Dict[str, Any]
