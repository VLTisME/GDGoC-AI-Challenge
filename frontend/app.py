import streamlit as st
import requests
import time
import io
import json
import base64
import os
import numpy as np
from PIL import Image
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Rock Fragment Analysis",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing results
if 'result' not in st.session_state:
    st.session_state.result = None
if 'diameters' not in st.session_state:
    st.session_state.diameters = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000" )

st.title("Rock Fragment Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload a rock fragment image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.session_state.original_image = image
    
    # Process button
    if st.button("Process Image"):
        with st.spinner("Processing image... This may take a moment."):
            # Convert image to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format=image.format)
            img_bytes = img_bytes.getvalue()
            
            # Send to backend
            files = {"file": ("image.jpg", img_bytes, f"image/{image.format.lower()}")}
            response = requests.post(f"{BACKEND_URL}/api/predict", files=files)
            
            if response.status_code == 202:
                task_id = response.json()["task_id"]
                
                # Poll for results
                complete = False
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                while not complete:
                    task_response = requests.get(f"{BACKEND_URL}/api/task/{task_id}")
                    task_status = task_response.json()
                    
                    if task_status["status"] == "PENDING":
                        status_text.text("Task pending...")
                        progress_bar.progress(25)
                    elif task_status["status"] == "PROCESSING":
                        status_text.text("Processing image...")
                        progress_bar.progress(50)
                    elif task_status["status"] == "SUCCESS":
                        status_text.text("Processing complete!")
                        progress_bar.progress(100)
                        complete = True
                        st.session_state.result = task_status["result"]
                        
                        # Extract diameters for CDF analysis
                        if "stats" in st.session_state.result and "diameters_cm" in st.session_state.result["stats"]:
                            st.session_state.diameters = st.session_state.result["stats"]["diameters_cm"]
                    elif task_status["status"] == "FAILURE":
                        st.error("Processing failed. Please try again.")
                        complete = True
                    
                    time.sleep(1)
            else:
                st.error(f"Error: {response.text}")

# Display results if available
if st.session_state.result is not None:
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Segmentation Results", "CDF Analysis"])
    
    with tab1:
        st.header("Segmentation Results")
        
        # Create two columns of equal width
        col1, col2 = st.columns(2)
        
        with col1:
            # Display original image
            st.image(st.session_state.original_image, caption="Original Image", use_column_width=True)
        
        with col2:
            segmentation_img = Image.open(io.BytesIO(base64.b64decode(st.session_state.result["segmentation_image"])))
            width, height = segmentation_img.size
            right_half = segmentation_img.crop((width//2, 0, width, height))
            st.image(right_half, caption=f"Segmented Image ({st.session_state.result['fragment_count']} fragments)", use_column_width=True)
    
    with tab2:
        st.header("Interactive CDF Exploration")
        
        if st.session_state.diameters:
            # Sort diameters for CDF calculation
            diameters_sorted = sorted(st.session_state.diameters)
            
            # Get min and max for slider
            min_size = round(min(diameters_sorted), 2)
            max_size = round(max(diameters_sorted), 2)
            
            # Create a slider for size threshold
            selected_size = st.slider(
                "Select Size Threshold (cm)", 
                min_value=min_size,
                max_value=max_size,
                value=(min_size + max_size) / 2,
                step=0.1,
                key="size_threshold"  # Important: unique key for session state
            )
            
            # Calculate the percentage of fragments smaller than the selected size
            percentage = sum(1 for d in diameters_sorted if d <= selected_size) / len(diameters_sorted) * 100
            
            # Display the result
            st.info(f"{percentage:.1f}% of fragments are smaller than {selected_size:.1f} cm")
            
            # Create an interactive plot with Plotly
            st.subheader("Interactive CDF Plot")
            
            # Calculate CDF values
            y_values = [i / len(diameters_sorted) * 100 for i in range(1, len(diameters_sorted) + 1)]
            
            # Create Plotly figure
            fig = go.Figure()
            
            # Add CDF curve
            fig.add_trace(go.Scatter(
                x=diameters_sorted,
                y=y_values,
                mode='lines+markers',
                name='CDF',
                line=dict(color='blue', width=2)
            ))
            
            # Add vertical line for selected size
            fig.add_trace(go.Scatter(
                x=[selected_size, selected_size],
                y=[0, percentage],
                mode='lines',
                name=f'Selected Size: {selected_size:.1f} cm',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            # Add horizontal line for percentage
            fig.add_trace(go.Scatter(
                x=[0, selected_size],
                y=[percentage, percentage],
                mode='lines',
                name=f'Percentage: {percentage:.1f}%',
                line=dict(color='green', width=2, dash='dash')
            ))
            
            # Update layout
            fig.update_layout(
                xaxis_title='Fragment Size (cm)',
                yaxis_title='Cumulative Percentage (%)',
                yaxis=dict(range=[0, 100]),
                xaxis=dict(range=[0, max_size * 1.1]),
                legend=dict(x=0.02, y=0.98),
                margin=dict(l=20, r=20, t=20, b=20),
                height=500
            )
            
            # Display the plot
            st.plotly_chart(fig, use_container_width=True)
            
            # Display CDF plot from backend
            st.subheader("CDF Plot from Backend")
            cdf_img = Image.open(io.BytesIO(base64.b64decode(st.session_state.result["cdf_plot"])))
            st.image(cdf_img, use_column_width=True)
            
            # Display statistics
            st.subheader("Fragment Size Statistics")
            stats = st.session_state.result["stats"]
            
            # Create a clean statistics display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Minimum Size (cm)", f"{stats['Dmin']:.2f}")
                st.metric("D10 (cm)", f"{stats['D10']:.2f}")
            with col2:
                st.metric("Average Size (cm)", f"{stats['Average']:.2f}")
                st.metric("D50 (cm)", f"{stats['D50']:.2f}")
            with col3:
                st.metric("Maximum Size (cm)", f"{stats['Dmax']:.2f}")
                st.metric("D90 (cm)", f"{stats['D90']:.2f}")
            
            st.metric("Total Fragments", stats["N"])
