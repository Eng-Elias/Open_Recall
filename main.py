from fastapi import FastAPI, Request, Query, Depends, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from utils.screenshot_utils import screenshot_manager
from utils.db_utils import Base, engine, get_db, Screenshot, Tag
from utils.schemas import TagCreate, TagResponse, ScreenshotResponse, Page
from contextlib import asynccontextmanager
import signal
import sys
import multiprocessing
from datetime import datetime
from typing import List, Optional
from sqlalchemy import and_, or_, func
import math
import os
from fastapi import HTTPException

# Create database tables
Base.metadata.create_all(bind=engine)

# Ensure screenshots directory exists
screenshots_dir = os.path.join(os.path.dirname(__file__), "data", "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

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
app.mount("/data/screenshots", StaticFiles(directory=screenshots_dir), name="screenshots")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/screenshots", response_model=Page[ScreenshotResponse])
async def get_screenshots(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    app_name: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    tag_ids: Optional[List[int]] = Query(None),
    search_text: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    db = Depends(get_db)
):
    # Base query
    query = db.query(Screenshot)
    
    # Apply filters
    if start_date:
        query = query.filter(Screenshot.timestamp >= start_date)
    if end_date:
        query = query.filter(Screenshot.timestamp <= end_date)
    if app_name:
        query = query.filter(Screenshot.app_name == app_name)
    if is_favorite is not None:
        query = query.filter(Screenshot.is_favorite == is_favorite)
    if tag_ids:
        query = query.filter(Screenshot.tags.any(Tag.id.in_(tag_ids)))
    if search_text:
        query = query.filter(Screenshot.extracted_text.ilike(f"%{search_text}%"))
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    pages = math.ceil(total / size)
    start = (page - 1) * size
    
    # Get paginated items
    items = query.order_by(Screenshot.timestamp.desc()).offset(start).limit(size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@app.get("/api/tags", response_model=List[TagResponse])
async def get_tags(db = Depends(get_db)):
    return db.query(Tag).all()

@app.post("/api/tags", response_model=TagResponse)
async def create_tag(tag: TagCreate, db = Depends(get_db)):
    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.put("/api/screenshots/{screenshot_id}/favorite")
async def toggle_favorite(screenshot_id: int, db = Depends(get_db)):
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    if screenshot:
        screenshot.is_favorite = not screenshot.is_favorite
        db.commit()
        return {"success": True}
    return {"success": False}

@app.post("/api/screenshots/{screenshot_id}/tags/{tag_id}")
async def add_tag_to_screenshot(screenshot_id: int, tag_id: int, db = Depends(get_db)):
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if screenshot and tag:
        screenshot.tags.append(tag)
        db.commit()
        return {"success": True}
    return {"success": False}

@app.delete("/api/screenshots/{screenshot_id}/tags/{tag_id}")
async def remove_tag_from_screenshot(screenshot_id: int, tag_id: int, db = Depends(get_db)):
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if screenshot and tag:
        screenshot.tags.remove(tag)
        db.commit()
        return {"success": True}
    return {"success": False}

@app.get("/api/app-names")
async def get_app_names(db = Depends(get_db)):
    """Get unique app names for autocomplete"""
    app_names = db.query(Screenshot.app_name)\
                  .filter(Screenshot.app_name.isnot(None))\
                  .filter(Screenshot.app_name != "")\
                  .distinct()\
                  .order_by(Screenshot.app_name)\
                  .all()
    return [name[0] for name in app_names]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)

# Update existing endpoints to broadcast changes
@app.post("/api/toggle-favorite/{screenshot_id}")
async def toggle_favorite(screenshot_id: int, db = Depends(get_db)):
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    screenshot.is_favorite = not screenshot.is_favorite
    db.commit()
    
    # Broadcast update
    await manager.broadcast({
        "type": "favorite_updated",
        "screenshot_id": screenshot_id,
        "is_favorite": screenshot.is_favorite
    })
    
    return {"success": True}

@app.post("/api/add-tag/{screenshot_id}/{tag_id}")
async def add_tag_to_screenshot(screenshot_id: int, tag_id: int, db = Depends(get_db)):
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not screenshot or not tag:
        raise HTTPException(status_code=404, detail="Screenshot or tag not found")
    
    if tag not in screenshot.tags:
        screenshot.tags.append(tag)
        db.commit()
        
        # Broadcast update
        await manager.broadcast({
            "type": "tag_added",
            "screenshot_id": screenshot_id,
            "tag": {"id": tag.id, "name": tag.name}
        })
    
    return {"success": True}

@app.delete("/api/remove-tag/{screenshot_id}/{tag_id}")
async def remove_tag_from_screenshot(screenshot_id: int, tag_id: int, db = Depends(get_db)):
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not screenshot or not tag:
        raise HTTPException(status_code=404, detail="Screenshot or tag not found")
    
    if tag in screenshot.tags:
        screenshot.tags.remove(tag)
        db.commit()
        
        # Broadcast update
        await manager.broadcast({
            "type": "tag_removed",
            "screenshot_id": screenshot_id,
            "tag_id": tag_id
        })
    
    return {"success": True}

if __name__ == "__main__":
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    try:
        server.run()
    except KeyboardInterrupt:
        print("Received shutdown signal...")
        screenshot_manager.stop()
        sys.exit(0)
