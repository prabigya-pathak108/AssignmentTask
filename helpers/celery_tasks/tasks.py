from .celery_worker import celery_app
from chat.chat import ChatResponse



@celery_app.task
def process_user_query(natural_language_query: str,provider:str="gemini"):
    inst=ChatResponse(provider=provider)
    question= natural_language_query
    res=inst.handle_chat(question)
    return res
