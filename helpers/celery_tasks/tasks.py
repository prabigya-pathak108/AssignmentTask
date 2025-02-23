from .celery_worker import celery_app
from helpers.chat.chat import ChatResponse
from helpers.secret_manager.secrets import SecretManager
from helpers.logging_mechanism.logger import log_message
import uuid

manager=SecretManager()


@celery_app.task
def process_user_query(natural_language_query: str,provider:str=None):
    if provider is None:
        provider = manager.get_from_env("MODEL_TO_USE", "gemini")
    inst=ChatResponse(provider=provider)
    unique_id=uuid.uuid4()
    log_message(str(unique_id),natural_language_query)

    res=inst.handle_chat(natural_language_query,unique_id)
    return res
