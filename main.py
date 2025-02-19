from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from utils.screenshot_utils import screenshot_manager
from utils.db_utils import Base, engine
from contextlib import asynccontextmanager
import signal
import sys
import multiprocessing

# Create database tables
Base.metadata.create_all(bind=engine)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("Shutting down screenshot manager...")
    screenshot_manager.stop()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def on_worker_exit(server):
    """Handle worker process exit"""
    print("Worker process exiting, stopping screenshot manager...")
    screenshot_manager.stop()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start the screenshot manager
    if multiprocessing.current_process().name == 'MainProcess':
        screenshot_manager.start()
    yield
    # Shutdown: stop the screenshot manager
    if multiprocessing.current_process().name == 'MainProcess':
        print("FastAPI shutting down, stopping screenshot manager...")
        screenshot_manager.stop()

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("Received shutdown signal...")
        screenshot_manager.stop()
        sys.exit(0)
