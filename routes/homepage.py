from fastapi import APIRouter,HTTPException,Query,Depends,Form
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request
import pandas as pd
from typing import List, Dict

import asyncio
import httpx
import plotly.tools as tls  # For converting matplotlib to plotly
import json


templates = Jinja2Templates(directory="frontend")



router = APIRouter()

@router.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
