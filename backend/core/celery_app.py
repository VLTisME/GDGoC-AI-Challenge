from celery import Celery
import os

# Get Celery configuration from environment variables
broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")


# print("CELERY_BROKER_URL: celery_app ", os.getenv("CELERY_BROKER_URL"))
# print("CELERY_RESULT_BACKEND: celery_app", os.getenv("CELERY_RESULT_BACKEND"))

# Create Celery app
celery_app = Celery(
    "rock_fragment_analysis",
    broker=broker_url,
    backend=result_backend,
    include=["tasks.inference_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_ignore_result=False,
    result_expires=None,  
)

# app = Celery("rock_fragment_analysis", broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("CELERY_RESULT_BACKEND"))
# r = app.AsyncResult('1a7d3ad0-6575-4145-b3cd-fc68d61f1aab')
# print(r.state)
# print(r.result)

# Optional: Define periodic tasks
# celery_app.conf.beat_schedule = {
#     "cleanup-old-tasks": {
#         "task": "tasks.maintenance.cleanup_old_tasks",
#         "schedule": 3600.0,  # Run every hour
#     },
# }
