from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from dotenv import load_dotenv

from routes.index import register_routes

# Initialize FastAPI app
app = FastAPI()

# Load environment variables
load_dotenv()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to add processing time header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add X-Process-Time header to every response. This is useful
    for determining how long the request took to process. The time is in
    seconds as a floating point number, with arbitrary precision.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Register routes
register_routes(app)

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
