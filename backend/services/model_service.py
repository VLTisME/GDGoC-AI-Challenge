import os
import torch
import numpy as np
import cv2
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
import time
from functools import lru_cache

from core.config import settings

# Global variable to store the predictor
_predictor = None

@lru_cache(maxsize=1)
def get_predictor():
    """
    Get or create the Detectron2 predictor
    Uses lru_cache to ensure the model is only loaded once
    """
    global _predictor
    
    if _predictor is None:
        print("Loading Mask R-CNN model...")
        start_time = time.time()
        
        # Configure Detectron2
        cfg = get_cfg()
        cfg.merge_from_file(
            model_zoo.get_config_file(
                "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
            )
        )
        
        # Update configuration with our settings
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # Only one class (rock fragment)
        cfg.MODEL.WEIGHTS = settings.MODEL_WEIGHTS_PATH
        # cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = settings.SCORE_THRESHOLD
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.4
        
        # Use GPU if available
        cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Create predictor
        _predictor = DefaultPredictor(cfg)
        
        print(f"Model loaded in {time.time() - start_time:.2f} seconds")
    
    return _predictor



def predict_image(image_bgr):
    """
    Run inference on an image
    
    Args:
        image_bgr: OpenCV image in BGR format
    
    Returns:
        instances: Detectron2 instances object
    """
    # Get predictor
    predictor = get_predictor()
    
    # Run inference
    outputs = predictor(image_bgr)
    
    # Get instances
    instances = outputs["instances"].to("cpu")
    
    return instances
