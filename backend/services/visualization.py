import numpy as np
import cv2
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image

def create_mask_mosaic(masks, image_bgr):
    """
    Create a colorful mosaic of instance masks
    
    Args:
        masks: Boolean array of shape (N, H, W) where N is the number of instances
        image_bgr: Original image in BGR format
    
    Returns:
        mosaic: Image with colored masks
    """
    # Get image dimensions
    H, W = image_bgr.shape[:2]
    
    # Get number of instances
    N = masks.shape[0]
    
    # Create colormap
    cmap = plt.get_cmap('tab20')
    colors = (np.array([cmap(i/N)[:3] for i in range(N)])*255).astype(np.uint8)
    
    # Create mosaic
    mosaic = np.zeros((H, W, 3), dtype=np.uint8)
    
    # Fill mosaic with colors
    for i, mask in enumerate(masks):
        mosaic[mask] = colors[i]
    
    # Create overlay
    alpha = 0.5
    overlay = cv2.addWeighted(
        cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB),
        1 - alpha,
        mosaic,
        alpha,
        0
    )
    
    return overlay

def create_visualization(image_bgr, instances):
    """
    Create visualization of original image and segmentation results
    
    Args:
        image_bgr: Original image in BGR format
        instances: Detectron2 instances object
    
    Returns:
        visualization_base64: Base64 encoded image
    """
    # Get masks
    masks = instances.pred_masks.numpy()
    
    # Create mosaic
    mosaic = create_mask_mosaic(masks, image_bgr)
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Display original image
    ax1.imshow(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
    ax1.set_title("Original Image")
    ax1.axis('off')
    
    # Display mosaic
    ax2.imshow(mosaic)
    #ax2.set_title(f"Predicted Masks ({len(masks)} fragments)")
    ax2.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    
    # Encode as base64
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return img_base64
