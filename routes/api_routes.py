from fastapi import APIRouter,HTTPException,Query,Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from helpers.database_work_model.database import get_db
from helpers.celery_tasks.tasks import process_user_query
from celery.result import AsyncResult
from helpers.celery_tasks.celery_worker import celery_app
from helpers.chat.chat import ChatResponse
import uuid

class QueryRequest(BaseModel):
    query: str

router = APIRouter()

#testing routes
@router.get('/test')
async def test_app():
    return {"message":"running"}


@router.post("/generate_table_from_sql")
def run_sql(query_data:QueryRequest,db:Session=Depends(get_db)):
    """
    Executes a SQL query and returns the result as a list of dictionaries.
    The SQL query can be a SELECT statement or any other type of query that returns a result set.
    The function returns a JSON object with a status field set to "success" and a data field containing the result set.
    If the query fails due to a syntax error or a database error, the function returns a JSON object with a status field set to "error" and a detail field containing the error message.
    """
    try:
        result = db.execute(text(query_data.query))
        rows = result.fetchall()
        columns = result.keys()

        result_list = []
        for row in rows:
            # Create a dictionary with proper handling of None (NULL) and empty values
            row_dict = {col: (value if value is not None else "") for col, value in zip(columns, row)}
            result_list.append(row_dict)
        
        return {"status": "success", "data": result_list}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/testing_sql/")
def submit_query(query: str, provider: str = "gemini"):
    """
    Endpoint to test the SQL generation using a language model. The model takes a user query and returns the generated SQL query or an error message.
    It doesnot use celery.

    Args:
    query (str): User query to generate SQL from.
    provider (str): The language model provider to use. Defaults to "gemini".

    Returns:
    dict: A dictionary with the generated SQL query or an error message.
    """
    inst=ChatResponse(provider=provider)
    question= query
    res=inst.handle_chat(question,uuid.uuid4())
    return res


@router.post("/test_sql_gen/")
def submit_query(request: QueryRequest):
    """
    Endpoint to test the SQL generation using a language model. The model takes a user query and returns a task id.
    The model runs in a celery task.

    Args:
    request (QueryRequest): User query to generate SQL from.

    Returns:
    dict: A dictionary with the task id.
    """
    #print(f"I am here, {request.query}")
    task = process_user_query.apply_async(args=[request.query])
    return {"task_id": task.id}


@router.get("/result/{task_id}")
def get_result(task_id: str):
    """
    Get the result of a task. This is the endpoint where frontend polls.

    Args:
    task_id (str): The id of the task.

    Returns:
    dict: A dictionary with the result of the task. If the task is still
    processing, the dictionary contains a "status" field with the value
    "Processing...". If the task has finished, the dictionary contains a
    "result" field with the result of the task and a "processing" field with
    the value False. If the task has failed, the dictionary contains a "status"
    field with the value "FAILURE" and a "processing" field with the value True.
    """
    task_result = AsyncResult(task_id,app=celery_app)
    if task_result.state == "PENDING":
        return {"status": "Processing...","processing":True}
    elif task_result.state == "SUCCESS":
        return {"result":task_result.result,"processing":False}
    else:
        return {"status": task_result.state,"processing":True}