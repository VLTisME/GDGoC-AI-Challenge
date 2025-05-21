FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for cache layer)
COPY requirements.txt .

# Install torch and torchvision manually
RUN pip install --no-cache-dir torch==2.1.2 torchvision==0.16.2

# Install detectron2 from GitHub
RUN pip install --no-cache-dir --no-build-isolation 'git+https://github.com/facebookresearch/detectron2.git'

# Now install remaining dependencies (they include pydantic-settings)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# remember to try multistage build
# oh wait try uv