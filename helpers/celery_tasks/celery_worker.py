from celery import Celery
import os
from ..secret_manager.secrets import SecretManager
secret_manager=SecretManager()

CELERY_BROKER_URL = secret_manager.get_from_env("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
