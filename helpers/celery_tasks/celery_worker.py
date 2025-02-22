from celery import Celery
import os
from helpers.secret_manager.secrets import SecretManager
secret_manager=SecretManager()

CELERY_BROKER_URL = secret_manager.get_from_env("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_URL = secret_manager.get_from_env("CELERY_RESULT_URL", "redis://127.0.0.1:6379/1")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL,result_backend=CELERY_RESULT_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery_app.autodiscover_tasks(["helpers.celery_tasks"])