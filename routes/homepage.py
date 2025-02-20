from fastapi import APIRouter,HTTPException,Query,Depends,Form
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request
import pandas as pd
from typing import List, Dict
from logging_mechanism.logger import logger


import httpx
import plotly.tools as tls  # For converting matplotlib to plotly
import json


templates = Jinja2Templates(directory="frontend")



router = APIRouter()

@router.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @router.post("/send_message", response_class=HTMLResponse)
# async def send_message(message: str = Form(...)):
#     """Returns a simulated chatbot response"""
#     bot_response = f"🤖 Bot: {message[::-1]}" 
#     return f"""
#         <div class="message user">👤 You: {message}</div>
#         <div class="message bot">{bot_response}</div>
#     """

def get_table_data() -> List[Dict]:
    # Example of CSV data reading, replace with your actual SQL query logic
    data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
    })
    # Convert to a list of dictionaries for API response
    return data.to_dict(orient="records")

@router.post("/send_message", response_class=HTMLResponse)
async def send_message(message: str = Form(...)):
    """Simulated chatbot response with explanation and table"""
    print("Message is:",message)
    
    # URL of the /api/query endpoint
    query_url = "http://localhost:8000/api/query"
    
    # Initialize api_response with a default value
    api_response = None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(query_url, json={ "query":message})
            
            if response.status_code == 200:
                # Try to parse the response as JSON
                api_response = response.json()
                logger.info("Function One executed")
            else:
                api_response = {"data": []}  # Default to empty table if response is not 200
                logger.warning("Function Not executed")
    except Exception as e:
        api_response = {"data": []}  # Handle any potential errors (e.g., connection issues)

    # Prepare the response data
    response_data = {
        "explanation": f"🤖 Bot: Here is some data related to '{message}'.",
        "table": api_response.get("data") if api_response else None,
        "plot_data": {
            "x": [1, 2, 3, 4, 5],
            "y": [1, 2, 4, 8, 16]
        } if "plot" in message.lower() else None
    }

    # Generate the HTML response dynamically
    explanation_html = f'<div class="message bot">{response_data["explanation"]}</div>'
    
    # Render the table HTML if there's data
    table_html = ""
    if response_data["table"]:
        table_html += '<div class="message bot"><table><thead><tr>'
        for col in response_data["table"][0].keys():
            table_html += f"<th>{col}</th>"
        table_html += "</tr></thead><tbody>"
        
        for row in response_data["table"]:
            table_html += "<tr>" + "".join(f"<td>{value}</td>" for value in row.values()) + "</tr>"
        
        table_html += "</tbody></table></div>"

    return explanation_html + table_html