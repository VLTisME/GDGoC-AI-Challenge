# 🪨 Rock Fragment Analysis Application

This application analyzes rock fragment images using Mask R-CNN for instance segmentation and generates Cumulative Distribution Function (CDF) plots of fragment sizes.


## Notes:
If possible in time, will add more:
- Tech stack: Auto (Cronjob, MakeFile, Bash Script), Container (k8s), Cloud (GCP), CI/CD (Jenkins), Observable system.
- Features: add a slider to modify threshold, allow users to upload multiple images (but then you have to modify a lot xd).
- Others: Demo, Architecture Visualization.

---

# 📑 Table of Contents

- [🤖 Model](#model)
    - [📚 Dataset](#dataset)
    - [🤝 Mask R-CNN](#mask-r-cnn)
    - [📄 CDF](#cdf)
- [🌐 Architecture Overview](#architecture-overview)
    - [📁 Project Structure](#project-structure)
    - [💻 Frontend](#frontend)
    - [🛠️ Backend](#backend)
    - [🖧 Celery](#celery)
    - [✅ Redis](#redis)
    - [🔧 Docker](#docker)
- [🧑🏻‍💻 How to run](#how-to-run)
    - [📡 On your local machine](#on-your-local-machine)
    - [⚙️ With Docker Compose](#with-docker-compose)
- [🤗 Additional notes](#additional-notes)
- [📔 Acknowledgements](#acknowledgements)

---

## Model

### 📚 Dataset

The dataset and its information can be found [here](https://www.kaggle.com/competitions/gd-go-c-hcmus-aic-fragment-segmentation-track).


### Mask R-CNN

- Mask R-CNN is a model used in Object Detection.
- It is an extension of Faster R-CNN. While Faster R-CNN efficiently locates objects in an image, **Mask R-CNN** takes a step further by generating a high-quality segmentation mask for each image.
- For more details, please refer at this [Blog](https://www.ikomia.ai/blog/ultimate-guide-mask-rcnn-object-detection-segmentation) which I found really helpful.
- In this project, I used Mask R-CNN model from detectron2, an open-source repo, that significantly optimizes traditional Mask R-CNN.

<!-- ### How does it work?

- Mask R-CNN has two stages: Regional Proposals Network (RPN) for locating objects & a network head for both classifying and predicting the segmentation mask. 

[![image.png](https://i.postimg.cc/Xqkx8ZYb/image.png)](https://postimg.cc/64Td6pZj)

#### Backbone Network with FPN
- Usually use a pre-trained CNN like ResNet or ResNeXt used to extract high-level features from the input image.
- Then FPN architecture is 
[![image.png](https://i.postimg.cc/s2gxyvk6/image.png)](https://postimg.cc/21gr788h) -->

### CDF
- How I estimate fragments' size for CDF plotting:
    - For a particular segmented rock, count how many pixels does it occupy in the mask, let's call it $p$.
    - Assume 1 pixel = $x$ centimeters. I set $x = 0.7$ in this project.
    - $Diameter \ estimated = \sqrt{p \cdot x ^ 2}$.

---

## Architecture Overview

### Project Structure

This document outlines the complete project structure for my rock fragment analysis application, which includes Streamlit for the frontend, FastAPI for the backend, Celery for task queuing, and Docker for containerization.

```
rock-fragment-analysis/
├── .env                           # Environment variables
├── .gitignore                     # Git ignore file
├── project_requirements.txt       # Project requirements 
├── local_run.sh                   # Run project outside Docker
├── Makefile                       # Make running project easier
├── LICENSE                        # Project's license
├── README.md                      # Project documentation
├── docker-compose.yml             # Docker Compose configuration
├── frontend/                      # Streamlit frontend application
│   ├── Dockerfile                 # Frontend Docker configuration
│   ├── requirements.txt           # Frontend dependencies
│   ├── .streamlit/               
│   │   └── config.toml            # Streamlit configuration
│   └── app.py                     # Main Streamlit application
├── backend/                       # FastAPI backend application
│   ├── Dockerfile                 # Backend Docker configuration
│   ├── requirements.txt           # Backend dependencies
│   ├── main.py                    # FastAPI main application
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   └── routes.py              # API route definitions
│   ├── core/                      # Core application code
│   │   ├── __init__.py
│   │   ├── config.py              # Application configuration
│   │   └── celery_app.py          # Celery configuration
│   ├── models/                    # Model definitions
│   │   ├── __init__.py
│   │   └── schema.py              # Pydantic schemas
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── model_service.py       # Model loading and inference
│   │   ├── visualization.py       # Visualization functions
│   │   └── cdf_service.py         # CDF calculation
│   └── tasks/                     # Celery tasks
│       ├── __init__.py
│       └── inference_tasks.py     # Inference task definitions
├── model/                         # Model files
│   ├── mask_rcnn_R_50_FPN_3x.yaml # Model configuration
│   └── model_final.pth            # Trained model weights
├── redis/                         # Redis for Celery
│   └── Dockerfile                 # Redis Docker configuration
├── worker/                        # Celery worker
    ├── Dockerfile                 # Worker Docker configuration
    └── requirements.txt           # Worker dependencies
```


### Frontend

The frontend is built with Streamlit, allow users to upload images, view segmentation results, and analyze CDF plots.

#### Key Files:

- **app.py**: Main Streamlit application that handles:
  - Image upload interface
  - Communication with the backend API
  - Display of segmentation results and CDF plots
  - Interactive elements for CDF analysis

- **.streamlit/config.toml**: Configuration for Streamlit appearance and behavior

- **requirements.txt**: Dependencies for the frontend.

- **Dockerfile**: Docker configuration for the frontend:
  ```dockerfile
  FROM python:3.10-slim

  WORKDIR /app

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY . .

  EXPOSE 8501

  CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
  ```

### Backend

The backend is built with FastAPI, providing API endpoints for image processing, model inference, and CDF calculation.

#### Key Files:

- **main.py**: Main FastAPI application entry point

- **api/routes.py**: API route definitions:
  - `/api/health`: Health check endpoint
  - `/api/predict`: Endpoint for image prediction
  - `/api/task/{task_id}`: Endpoint for checking task status

- **core/config.py**: Application configuration

- **core/celery_app.py**: Celery configuration for task queuing

- **models/schema.py**: Pydantic schemas for request/response validation

- **services/model_service.py**: Model loading and inference logic
  - Loads the Mask R-CNN model
  - Performs inference on images
  - Caches the model to avoid reloading

- **services/visualization.py**: Functions for visualizing segmentation results

- **services/cdf_service.py**: Functions for calculating and plotting CDF

- **tasks/inference_tasks.py**: Celery task definitions for asynchronous processing

- **requirements.txt**: Dependencies for the backend.

- **Dockerfile**: Docker configuration for the backend:
  ```dockerfile
  FROM python:3.10-slim

  WORKDIR /app

  # Install system dependencies
  RUN apt-get update && apt-get install -y \
      build-essential \
      git \
      libgl1-mesa-glx \
      libglib2.0-0 \
      && rm -rf /var/lib/apt/lists/*

  COPY requirements.txt .

  RUN pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2

  RUN pip install --no-cache-dir --no-build-isolation 'git+https://github.com/facebookresearch/detectron2.git'

  RUN pip install --no-cache-dir -r requirements.txt

  COPY . .

  EXPOSE 8000

  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

### Celery

The Celery worker handles asynchronous tasks like model inference, which can be time-consuming.

#### Key Files:

- **Dockerfile**: Docker configuration for the Celery worker:
  ```dockerfile
  FROM python:3.10-slim

  WORKDIR /app

  RUN apt-get update && apt-get install -y \
      build-essential \
      git \
      libgl1-mesa-glx \
      libglib2.0-0 \
      && rm -rf /var/lib/apt/lists/*


  RUN pip install pip==22.3.1

  RUN pip --version

  RUN pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2

  RUN pip install --no-cache-dir 'git+https://github.com/facebookresearch/detectron2.git'

  COPY backend/requirements.txt .
  RUN grep -v "torch\|detectron2" requirements.txt > requirements_filtered.txt && \
      pip install --no-cache-dir -r requirements_filtered.txt
  RUN pip install --no-cache-dir pydantic-settings

  COPY backend /app
  COPY model /app/model

  CMD ["celery", "-A", "core.celery_app", "worker", "--loglevel=info"]
  ```

### Redis

Redis is used as a message broker for Celery and for caching.

#### Key Files:

- **Dockerfile**: Docker configuration for Redis:
  ```dockerfile
  FROM redis:7.2-alpine

  EXPOSE 6379

  CMD ["redis-server"]
  ```

### Docker

Docker Compose orchestrates all the services.

#### Key File:

- **docker-compose.yml**: Configuration for all services:
  ```yaml
  version: '3.8'

  services:
    frontend:
      build: ./frontend
      ports:
        - "8501:8501"
      depends_on:
        - backend
      volumes:
        - ./frontend:/app
      environment:
        - BACKEND_URL=http://backend:8000

    backend:
      build: ./backend
      ports:
        - "8000:8000"
      depends_on:
        - redis
      volumes:
        - ./backend:/app
        - ./model:/app/model
      env_file:
        - .env

    worker:
      build:
        context: .
        dockerfile: worker/Dockerfile
      depends_on:
        - redis
        - backend
      volumes:
        - ./backend:/app
        - ./model:/app/model
      env_file:
        - .env

    redis:
      build: ./redis
      ports:
        - "6379:6379"
  ```


## Key Implementation Details

### Model Loading and Optimization

To optimize model loading, which can be time-consuming:

1. **Model Caching**: The model is loaded once when the worker starts and kept in memory.
2. **Lazy Loading**: The model is only loaded when needed for inference.
3. **GPU Utilization**: The model uses GPU if available, falling back to CPU if not.

### Task Queue with Celery

Celery is used to handle asynchronous processing:

1. **Task Creation**: When a user uploads an image, a Celery task is created.
2. **Asynchronous Processing**: The task is processed by a worker while the user can continue using the application.
3. **Status Updates**: The frontend periodically checks the task status and displays results when ready.

### CDF Calculation and Visualization

The CDF calculation and visualization are handled by:

1. **Instance Segmentation**: The Mask R-CNN model identifies individual rock fragments.
2. **Size Calculation**: The size of each fragment is calculated based on pixel area.
3. **CDF Generation**: The CDF is generated based on the fragment sizes
4. **Interactive Visualization**: The CDF plot is displayed with interactive elements.

### User Interface Features

The Streamlit frontend provides:

1. **Image Upload**: Users can upload images of rock fragments.
2. **Results Display**: Segmentation results and CDF plots are displayed.
3. **Interactive Elements**: Users can interact with the CDF plot to analyze specific size thresholds.
4. **Processing Time**: The processing time for each image is displayed.
5. **Multiple Image Analysis**: Users can upload multiple images and compare results.

## Performance Optimizations

1. **Model Caching**: The model is loaded once and kept in memory.
2. **Asynchronous Processing**: Long-running tasks are handled asynchronously.
3. **Result Caching**: Results are cached to avoid reprocessing the same image.
4. **Efficient Image Processing**: Images are processed efficiently using OpenCV.
5. **Parallel Processing**: Multiple workers can process different images in parallel.


## How to run
- Download the model configs and weights, then put it in ```model/``` folder.
- In Terminal, go the to directory of the project.
- (Optional but highly recommended) Create virtual environment (assume you have installed **mamba**):
```bash
mamba create -n fragment-segmentation
```
- Activate the virtual environment:
```bash
mamba activate fragment-segmentation
```
Then you have two running options:

### On your local machine
- Open Terminal and run:
```bash
make local_run
```
- It will download needed packages, libraries to run the project, and will automatically launch the application. If you want to launch manually, after running, you can access your application at [localhost:8501](localhost:8501).

### With Docker Compose
- Make sure your Docker desktop is running by:
```bash
systemctl --user start docker-desktop
```
- Then:
```bash
make docker_run
```

- That's it! Open Docker Desktop and connect to your application.

## Acknowledgements

This project uses [Detectron2](https://github.com/facebookresearch/detectron2) (Copyright Facebook AI Research), which is licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).