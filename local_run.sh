#!/bin/bash

export MODEL_CONFIG_PATH="rock-fragment-app/model/mask_rcnn_R_50_FPN_3x.yaml"
export MODEL_WEIGHTS_PATH="rock-fragment-app/model/model_final.pth"

export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
export PIXEL_SIZE_MM=20.0

pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2
pip install --no-cache-dir --no-build-isolation 'git+https://github.com/facebookresearch/detectron2.git'
pip install -r requirements.txt

(cd frontend && streamlit run app.py --server.address=0.0.0.0) &
(cd backend && redis-server) &
(cd backend && celery -A core.celery_app worker --loglevel=info) &
(cd backend && uvicorn main:app --host 0.0.0.0 --port 8000) &
wait