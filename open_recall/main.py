from fastapi import FastAPI, Request, Query, Depends, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from open_recall.utils.screenshot_utils import screenshot_manager
from open_recall.utils.db_utils import Base, engine, get_db, Screenshot, Tag
from open_recall.utils.schemas import TagCreate, TagResponse, ScreenshotResponse, Page, BaseModel
from open_recall.utils.settings import BASE_DIR, settings_manager
from open_recall.utils.summarization import generate_summary, generate_search_results_summary, get_available_models, download_model, is_model_downloaded
from contextlib import asynccontextmanager
import signal
import sys
import multiprocessing
from datetime import datetime
from typing import List, Optional
from sqlalchemy import or_, func
import math
import os
import json
from fastapi import HTTPException
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

# Ensure screenshots directory exists
screenshots_dir = os.path.join(BASE_DIR, "data", "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)
os.makedirs(screenshot_manager.storage_path, exist_ok=True)

# Load configuration from config.json
def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        return {"app": {"port": 8742, "host": "localhost", "debug": False}}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"app": {"port": 8742, "host": "localhost", "debug": False}}

# Get configuration
config = load_config()
APP_PORT = int(os.environ.get('OPEN_RECALL_PORT', config['app']['port']))
APP_HOST = os.environ.get('OPEN_RECALL_HOST', config['app']['host'])
APP_DEBUG = os.environ.get('OPEN_RECALL_DEBUG', '').lower() == 'true'

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
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/data/screenshots", StaticFiles(directory=screenshot_manager.storage_path), name="screenshots")

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

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
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(Screenshot.timestamp >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
            
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            query = query.filter(Screenshot.timestamp <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
            
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

@app.delete("/api/tags/{tag_id}")
async def delete_tag(tag_id: int, db = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if tag is used by any screenshots
    if tag.screenshots:
        # Remove the tag from all screenshots
        for screenshot in tag.screenshots:
            screenshot.tags.remove(tag)
    
    # Delete the tag
    db.delete(tag)
    db.commit()
    
    # Broadcast update
    await manager.broadcast({
        "type": "tag_deleted",
        "tag_id": tag_id
    })
    
    return {"success": True}

@app.put("/api/screenshots/{screenshot_id}/favorite")
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
    
    return {"success": True, "is_favorite": screenshot.is_favorite}

class NotesUpdate(BaseModel):
    notes: str

@app.put("/api/screenshots/{screenshot_id}/notes")
async def update_notes(screenshot_id: int, notes_data: NotesUpdate, db = Depends(get_db)):
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    screenshot.notes = notes_data.notes
    db.commit()
    
    # Broadcast update
    await manager.broadcast({
        "type": "notes_updated",
        "screenshot_id": screenshot_id,
        "notes": screenshot.notes
    })
    
    return {"success": True, "notes": screenshot.notes}

@app.post("/api/tags", response_model=TagResponse)
async def create_tag(tag: TagCreate, db = Depends(get_db)):
    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

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

@app.delete("/api/screenshots/before-date/{date}")
async def delete_screenshots_before_date(
    date: str, 
    exclude_favorites: bool = Query(False),
    exclude_with_notes: bool = Query(False),
    tag_id: Optional[int] = Query(None),
    db = Depends(get_db)
):
    """
    Delete all screenshots before a specific date.
    Date format: YYYY-MM-DD
    
    Optional filters:
    - exclude_favorites: If true, favorite screenshots will be kept
    - exclude_with_notes: If true, screenshots with notes will be kept
    - tag_id: If provided, only screenshots with this tag will be deleted
    """
    try:
        # Convert string date to datetime
        target_date = datetime.fromisoformat(date)
        
        # Start with base query for screenshots before the target date
        query = db.query(Screenshot).filter(Screenshot.timestamp < target_date)
        
        # Apply additional filters
        if exclude_favorites:
            query = query.filter(Screenshot.is_favorite == False)
            
        if exclude_with_notes:
            query = query.filter(or_(
                Screenshot.notes == None,
                Screenshot.notes == "",
                func.length(Screenshot.notes) == 0
            ))
            
        if tag_id:
            query = query.filter(Screenshot.tags.any(Tag.id == tag_id))
        
        # Get all matching screenshots
        screenshots = query.all()
        
        if not screenshots:
            return {"success": True, "message": "No screenshots found matching your criteria", "count": 0}
        
        count = len(screenshots)
        
        # Get the file paths to delete from filesystem
        # Get the screenshots storage path
        file_paths = [os.path.join(screenshot_manager.storage_path, screenshot.file_path) for screenshot in screenshots if screenshot.file_path]
        
        # Delete screenshots from database
        for screenshot in screenshots:
            db.delete(screenshot)
        db.commit()
        
        # Delete the actual files
        deleted_files = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files += 1
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        
        # Construct a message that includes the filter information
        message_parts = [f"Deleted {count} screenshots before {date}"]
        if exclude_favorites:
            message_parts.append("excluding favorites")
        if exclude_with_notes:
            message_parts.append("excluding those with notes")
        if tag_id:
            tag = db.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                message_parts.append(f"with tag '{tag.name}'")
        
        message = " ".join(message_parts)
        
        # Broadcast update
        await manager.broadcast({
            "type": "screenshots_deleted",
            "count": count
        })
        
        return {
            "success": True, 
            "message": message, 
            "count": count,
            "files_deleted": deleted_files
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting screenshots: {str(e)}")

@app.post("/api/summarize-search")
async def summarize_search_results(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    app_name: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    tag_ids: Optional[List[int]] = Query(None),
    search_text: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Summarize the search results based on the provided filters.
    Maximum of 500 screenshots can be summarized at once.
    """
    # Check if summarization is enabled in settings
    if not settings_manager.get_setting("enable_summarization", False):
        return {"summary": "Summarization is disabled in settings. Please enable it to use this feature."}
    
    # Apply filters to get screenshots
    query = db.query(Screenshot)
    
    if start_date:
        query = query.filter(Screenshot.timestamp >= start_date)
    
    if end_date:
        query = query.filter(Screenshot.timestamp <= end_date)
    
    if app_name:
        query = query.filter(Screenshot.app_name == app_name)
    
    if is_favorite is not None:
        query = query.filter(Screenshot.is_favorite == is_favorite)
    
    if tag_ids:
        for tag_id in tag_ids:
            query = query.filter(Screenshot.tags.any(Tag.id == tag_id))
    
    if search_text:
        query = query.filter(Screenshot.extracted_text.contains(search_text))
    
    # Order by timestamp
    query = query.order_by(Screenshot.timestamp.desc())
    
    # Limit to 500 screenshots for performance
    screenshots = query.limit(500).all()
    
    if not screenshots:
        return {"summary": "No screenshots found matching the filters."}
    
    # Group screenshots by day for batch processing
    screenshots_by_day = {}
    for screenshot in screenshots:
        day = screenshot.timestamp.date() # Extract date part
        if day not in screenshots_by_day:
            screenshots_by_day[day] = []
        screenshots_by_day[day].append(screenshot)
    
    # Process each day's screenshots
    batch_summaries = []
    for day, day_screenshots in screenshots_by_day.items():
        # Combine OCR text from all screenshots for this day
        combined_text = ""
        for screenshot in day_screenshots:
            if screenshot.extracted_text:
                timestamp = screenshot.timestamp.isoformat()
                app_name = screenshot.app_name or "Unknown"
                combined_text += f"[{timestamp}] [{app_name}] {screenshot.extracted_text}\n\n"
        
        if combined_text:
            # Generate summary for this day
            batch_summary = generate_summary(combined_text)
            if batch_summary:
                batch_summaries.append(batch_summary)
    
    # Now summarize the batch summaries
    if batch_summaries:
        final_text = "The following are summaries of groups of screenshots:\n\n" + "\n\n".join(batch_summaries)
        final_summary = generate_search_results_summary(final_text, max_length=300)
        return {"summary": final_summary}
    else:
        return {"summary": "Could not generate summary for the selected screenshots."}

# Add API endpoints for settings
@app.get("/api/settings")
async def get_settings():
    """Get all application settings"""
    return settings_manager.get_all_settings()

class SettingsUpdate(BaseModel):
    enable_summarization: Optional[bool] = None
    capture_interval: Optional[int] = None
    summarization_model: Optional[str] = None

@app.put("/api/settings")
async def update_settings(settings: SettingsUpdate):
    """Update application settings"""
    settings_dict = {k: v for k, v in settings.dict().items() if v is not None}
    
    if not settings_dict:
        raise HTTPException(status_code=400, detail="No settings provided")
    
    # Validate capture_interval if provided
    if "capture_interval" in settings_dict and settings_dict["capture_interval"] < 10:
        raise HTTPException(status_code=400, detail="Capture interval must be at least 10 seconds")
    
    # Update settings
    success = settings_manager.update_settings(settings_dict)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update settings")
    
    # Update screenshot manager's capture interval if it was changed
    if "capture_interval" in settings_dict:
        screenshot_manager.capture_interval = settings_dict["capture_interval"]
        screenshot_manager.stop()
        screenshot_manager.start()
    
    # Broadcast settings update
    await manager.broadcast({
        "type": "settings_updated",
        "settings": settings_manager.get_all_settings()
    })
    
    return settings_manager.get_all_settings()

@app.get("/api/summarization/models")
async def get_summarization_models():
    """Get all available summarization models and their download status"""
    return get_available_models()

@app.get("/api/summarization/models/{model_id}/status")
async def check_model_status(model_id: str):
    """Check if a specific model is downloaded"""
    # URL decode the model_id
    from urllib.parse import unquote
    model_id = unquote(model_id)
    
    # Check if the model exists in available models
    from utils.summarization import AVAILABLE_MODELS
    if model_id not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    # Check if the model is downloaded
    is_downloaded = is_model_downloaded(model_id)
    
    return {
        "id": model_id,
        "name": AVAILABLE_MODELS[model_id]["name"],
        "description": AVAILABLE_MODELS[model_id]["description"],
        "downloaded": is_downloaded
    }

@app.post("/api/summarization/models/{model_id}/download")
async def download_summarization_model(model_id: str):
    """Download a specific summarization model"""
    # URL decode the model_id
    from urllib.parse import unquote
    model_id = unquote(model_id)
    
    # Check if the model exists in available models
    from utils.summarization import AVAILABLE_MODELS
    if model_id not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    # Download the model
    success = download_model(model_id)
    
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to download model {model_id}")
    
    # Return updated model list
    return get_available_models()

if __name__ == "__main__":
    config = uvicorn.Config("open_recall.main:app", host=APP_HOST, port=APP_PORT, reload=APP_DEBUG)
    server = uvicorn.Server(config)
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the server
        server.run()
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    finally:
        screenshot_manager.stop()
