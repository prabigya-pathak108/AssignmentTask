from fastapi import APIRouter,HTTPException,Query,Depends
from typing import List,Optional,Dict
from datetime import date, datetime,timedelta, timezone
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
from fastapi.responses import StreamingResponse
from io import StringIO
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging
from db_qa_models.QA_model import QueryRequest
from helpers.database_work_model.database import get_db
from helpers.celery_tasks.tasks import process_user_query
from celery.result import AsyncResult
import requests


router = APIRouter()

#testing routes
@router.get('/test')
async def test_app():
    return {"message":"running"}


@router.post("/query")
def run_sql(query_data:QueryRequest,db:Session=Depends(get_db)):
    try:
        print("Query is: ",query_data.query)
        result = db.execute(text(query_data.query))
        rows = result.fetchall()
        columns = result.keys()

        # Convert to JSON
        result_list = []
        for row in rows:
            # Create a dictionary with proper handling of None (NULL) and empty values
            row_dict = {col: (value if value is not None else "") for col, value in zip(columns, row)}
            result_list.append(row_dict)
        
        return {"status": "success", "data": result_list}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/test_sql_gen/")
def submit_query(query: str):
    task = process_user_query.apply_async(args=[query])
    return {"task_id": task.id}


@router.get("/result/{task_id}")
def get_result(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": "Processing..."}
    elif task_result.state == "SUCCESS":
        return task_result.result
    else:
        return {"status": task_result.state}