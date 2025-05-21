import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.lines import Line2D
from core.config import settings

def calculate_cdf(masks, pixel_size_mm=None):
    """
    Calculate CDF of fragment sizes
    
    Args:
        masks: Boolean array of shape (N, H, W) where N is the number of instances
        pixel_size_mm: Size of one pixel in mm (default: from settings)
    
    Returns:
        stats: Dictionary of CDF statistics
        cdf_plot_base64: Base64 encoded CDF plot
    """
    # Use default pixel size if not provided
    if pixel_size_mm is None:
        pixel_size_mm = settings.PIXEL_SIZE_MM
    
    # Convert mm to cm
    pixel_size_cm = pixel_size_mm / 10.0
    
    # Calculate areas in pixels
    areas_px = masks.sum(axis=(1, 2))
    
    # Convert to cm²
    areas_cm2 = areas_px * (pixel_size_cm**2)
    
    # Calculate diameters in cm
    diam_cm = np.sqrt(areas_cm2)
    
    # Number of fragments
    N = diam_cm.size
    
    # Sort diameters
    d_sorted = np.sort(diam_cm)
    
    # Calculate CDF values
    y_full = np.arange(1, N+1)/N * 100
    
    # Prepend (0,0) for plotting
    d_plot = np.concatenate([[0.0], d_sorted])
    y_plot = np.concatenate([[0.0], y_full])
    
    # Calculate key statistics
    Dmin, Dmax, Dmean = d_sorted[0], d_sorted[-1], d_sorted.mean()
    D10, D50, D90 = np.percentile(d_sorted, [10, 50, 90])
    
    # Create CDF plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot CDF curve
    ax.plot(d_plot, y_plot, '-o', color='blue', label='CDF')
    
    # Add horizontal guides
    for pct, col in zip([10, 50, 90], ['cyan', 'magenta', 'blue']):
        ax.axhline(pct, color=col, linestyle=':', lw=1)
        ax.text(100, pct, f'{pct}%', color=col,
                va=('bottom' if pct==10 else 'top' if pct==90 else 'center'),
                ha='right')
    
    # Add vertical lines
    for dval, pct, col in zip([D10, D50, D90], [10, 50, 90], ['cyan', 'magenta', 'blue']):
        ax.axvline(dval, color=col, linestyle=':', lw=2)
        ax.text(dval, pct, f'D{pct}: {dval:.2f}', color=col, fontsize=9,
                va=('bottom' if pct==10 else 'top' if pct==90 else 'center'),
                ha='left', backgroundcolor='white')
    
    # Add lines for min, mean, max
    ax.axvline(Dmin, color='green', linestyle='--', lw=2)
    ax.axvline(Dmean, color='orange', linestyle='--', lw=2)
    ax.axvline(Dmax, color='red', linestyle='--', lw=2)
    
    # Add text labels
    ax.text(Dmin, 0, f'Dmin: {Dmin:.2f}', color='green', va='bottom', ha='left', fontsize=9)
    ax.text(Dmean, 50, f'Average: {Dmean:.2f}', color='orange', va='center', ha='left', fontsize=9)
    ax.text(Dmax, 100, f'Dmax: {Dmax:.2f}', color='red', va='top', ha='right', fontsize=9)
    
    # Set axis limits and labels
    ax.set_xlim(0, max(100, Dmax * 1.1))
    ax.set_xticks(np.arange(0, max(100, Dmax * 1.1) + 1, 20))
    ax.set_ylim(0, 105)
    ax.set_xlabel('Fragment Size (cm)')
    ax.set_ylabel('Cumulative Percentage (%)')
    ax.set_title(f'CDF of Fragment Sizes (N={N})')
    ax.grid(linestyle='--', linewidth=0.5)
    
    # Add custom legend
    handles = [
        Line2D([0], [0], color='blue', marker='o', linestyle='-', label='CDF'),
        Line2D([0], [0], color='green', linestyle='--', lw=2, label=f'Dmin: {Dmin:.2f}'),
        Line2D([0], [0], color='orange', linestyle='--', lw=2, label=f'Average: {Dmean:.2f}'),
        Line2D([0], [0], color='red', linestyle='--', lw=2, label=f'Dmax: {Dmax:.2f}')
    ]
    ax.legend(handles=handles, loc='lower right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    
    # Encode as base64
    buf.seek(0)
    cdf_plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Prepare statistics
    stats = {
        'N': int(N),
        'Dmin': float(Dmin),
        'D10': float(D10),
        'D50': float(D50),
        'D90': float(D90),
        'Average': float(Dmean),
        'Dmax': float(Dmax),
        'diameters_cm': diam_cm.tolist()  # Convert to list for JSON serialization
    }
    
    return stats, cdf_plot_base64
