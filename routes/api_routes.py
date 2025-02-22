from fastapi import APIRouter,HTTPException,Query,Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from helpers.database_work_model.database import get_db
from helpers.celery_tasks.tasks import process_user_query
from celery.result import AsyncResult
from helpers.celery_tasks.celery_worker import celery_app
from helpers.chat.chat import ChatResponse

class QueryRequest(BaseModel):
    query: str

router = APIRouter()

#testing routes
@router.get('/test')
async def test_app():
    return {"message":"running"}


@router.post("/generate_table_from_sql")
def run_sql(query_data:QueryRequest,db:Session=Depends(get_db)):
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
    inst=ChatResponse(provider=provider)
    question= query
    res=inst.handle_chat(question,"gghh-3dded")
    return res


@router.post("/test_sql_gen/")
def submit_query(request: QueryRequest):
    print(f"I am here, {request.query}")
    task = process_user_query.apply_async(args=[request.query])
    return {"task_id": task.id}


@router.get("/result/{task_id}")
def get_result(task_id: str):
    task_result = AsyncResult(task_id,app=celery_app)
    if task_result.state == "PENDING":
        return {"status": "Processing...","processing":True}
    elif task_result.state == "SUCCESS":
        return {"result":task_result.result,"processing":False}
    else:
        return {"status": task_result.state,"processing":True}