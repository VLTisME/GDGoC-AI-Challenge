import numpy as np
import time
import cv2
from celery import Task

from core.celery_app import celery_app
from services.model_service import predict_image
from services.visualization import create_visualization
from services.cdf_service import calculate_cdf

class ModelTask(Task):
    """Task class that keeps the model in memory"""
    _predictor = None
    
    def __init__(self):
        super().__init__()
    
    def __call__(self, *args, **kwargs):
        """
        Override Task.__call__ to ensure the model is loaded
        """
        return self.run(*args, **kwargs)

@celery_app.task(base=ModelTask, name="tasks.inference_tasks.process_image")
def process_image(image_list):
    """
    Process an image with the Mask R-CNN model
    
    Args:
        image_list: List representation of a numpy array (BGR image)
    
    Returns:
        result: Dictionary with segmentation results
    """
    try:
        # Convert list back to numpy array
        image_bgr = np.array(image_list, dtype=np.uint8)
        
        # Record start time
        start_time = time.time()
        
        # Run inference
        instances = predict_image(image_bgr)
        
        # Get masks
        masks = instances.pred_masks.numpy()
        
        # Create visualization
        visualization_base64 = create_visualization(image_bgr, instances)
        
        # Calculate CDF
        stats, cdf_plot_base64 = calculate_cdf(masks)
        
        # Record end time
        processing_time = time.time() - start_time
        
        # Prepare result
        result = {
            "segmentation_image": visualization_base64,
            "cdf_plot": cdf_plot_base64,
            "fragment_count": len(masks),
            "stats": stats,
            "processing_time": processing_time
        }
        
        return result
    
    except Exception as e:
        # Log the error
        print(f"Error processing image: {str(e)}")
        
        # Re-raise the exception
        raise
