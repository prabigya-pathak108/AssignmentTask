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
from database_work_model.database import get_db

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
