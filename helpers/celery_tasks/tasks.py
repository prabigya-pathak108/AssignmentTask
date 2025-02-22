from .celery_worker import celery_app
from helpers.chat.chat import ChatResponse
from helpers.logging_mechanism.logger import log_message
import uuid



@celery_app.task
def process_user_query(natural_language_query: str,provider:str="gemini"):
    inst=ChatResponse(provider=provider)
    question= natural_language_query
    unique_id=uuid.uuid4()
    log_message(str(unique_id),natural_language_query)

    res=inst.handle_chat(question,unique_id)
    return res
