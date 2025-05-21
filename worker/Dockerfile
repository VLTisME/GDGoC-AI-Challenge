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
