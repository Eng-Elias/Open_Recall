import os
import time
import threading
from datetime import datetime, timezone
from typing import List, Optional
import mss
import numpy as np
from PIL import Image
import platform
import psutil

# Try to import Windows-specific modules with fallback for other platforms
try:
    import win32gui
    import win32process
    WINDOWS_MODULES_AVAILABLE = True
except ImportError:
    WINDOWS_MODULES_AVAILABLE = False

from .db_utils import get_db, screenshot_crud
from .ocr_utils import process_image_ocr
from .summarization import generate_summary
from .settings import BASE_DIR, settings_manager

class ScreenshotManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, storage_path: str = None, capture_interval: int = None):
        if not hasattr(self, 'initialized'):
            self.storage_path = storage_path or self._get_default_storage_path()
            # Get capture interval from settings or use default
            self.capture_interval = capture_interval or settings_manager.get_setting("capture_interval", 300)
            self.last_screenshot = None
            self.is_running = False
            self.thread = None
            self._ensure_storage_path()
            self.initialized = True

    def _get_default_storage_path(self):
        """Get default storage path based on OS"""
        return os.path.join(BASE_DIR, "data", "screenshots")

    def _ensure_storage_path(self):
        """Ensure screenshot storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def _get_active_window_info(self) -> tuple:
        """Get active window information"""
        # Check if running on Windows and if Windows modules are available
        if platform.system() == "Windows" and WINDOWS_MODULES_AVAILABLE:
            try:
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                app_name = psutil.Process(pid).name()
                window_title = win32gui.GetWindowText(hwnd)
                return app_name, window_title
            except Exception as e:
                print(f"Error getting window info: {e}")
                return "unknown", "unknown"
        else:
            # Fallback for non-Windows platforms or when modules aren't available
            try:
                # Try to get at least the process name using psutil
                current_process = psutil.Process()
                app_name = current_process.name()
                return app_name, "Open_Recall"
            except:
                return "Open_Recall", "Open_Recall"

    def _calculate_image_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate structural similarity between two images"""
        if img1 is None or img2 is None:
            return 0.0

        # Convert to grayscale for faster comparison
        def rgb2gray(img):
            return 0.2989 * img[..., 0] + 0.5870 * img[..., 1] + 0.1140 * img[..., 2]

        img1_gray = rgb2gray(img1)
        img2_gray = rgb2gray(img2)

        # Calculate mean squared error
        mse = np.mean((img1_gray - img2_gray) ** 2)
        if mse == 0:
            return 1.0
        
        # Convert MSE to similarity score (0-1)
        similarity = 1 / (1 + mse)
        return similarity

    def _is_significant_change(self, current: np.ndarray) -> bool:
        """Check if the current screenshot is significantly different from the last one"""
        if self.last_screenshot is None:
            return True
        
        similarity = self._calculate_image_similarity(current, self.last_screenshot)
        return similarity < 0.95  # Threshold for significant change

    def _capture_screenshot(self) -> Optional[tuple]:
        """Capture screenshot and return image array with metadata"""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = np.array(sct.grab(monitor))
                # Convert from BGRA to RGB
                screenshot = screenshot[:, :, :3]
                # Ensure the array is in uint8 format
                if screenshot.dtype != np.uint8:
                    screenshot = (screenshot * 255).astype(np.uint8)
                return screenshot
        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            return None

    def _save_screenshot(self, image_array: np.ndarray) -> Optional[str]:
        """Save screenshot and return filename only"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.webp"
            filepath = os.path.join(self.storage_path, filename)
            
            image = Image.fromarray(image_array)
            image.save(filepath, format="webp", quality=90, method=6)
            # Return only filename, not full path
            # NOTE: When accessing this file later, you must join it with the storage_path
            # For example, when deleting files, use os.path.join(storage_path, file_path)
            return filename
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None

    def _process_and_save(self):
        """Process screenshot and save to database"""
        if not self.is_running:
            return

        screenshot_array = self._capture_screenshot()
        if screenshot_array is None:
            return

        if not self._is_significant_change(screenshot_array):
            return

        filename = self._save_screenshot(screenshot_array)
        if not filename:
            return

        app_name, window_title = self._get_active_window_info()
        
        # Process OCR
        extracted_text, confidence = process_image_ocr(screenshot_array)
        
        # Generate summary only if enabled in settings
        summary = ""
        if settings_manager.get_setting("enable_summarization", False):
            summary = generate_summary(f"""
            Active App Name: {app_name}
            Screenshot Extracted Text: {extracted_text}
            """)
        
        # Save to database
        with next(get_db()) as db:
            screenshot_data = {
                "file_path": filename,
                "timestamp": datetime.now(timezone.utc),
                "app_name": app_name,
                "window_title": window_title,
                "extracted_text": extracted_text,
                "confidence_score": float(confidence),
                "summary": summary
            }
            screenshot_crud.create(db, data=screenshot_data)

        self.last_screenshot = screenshot_array

    def _screenshot_loop(self):
        """Main screenshot capture loop"""
        while self.is_running:
            try:
                self._process_and_save()
            except Exception as e:
                print(f"Error in screenshot loop: {e}")
            
            if not self.is_running:
                break
            
            for _ in range(int(self.capture_interval)):
                if not self.is_running:
                    break
                time.sleep(1)

    def start(self):
        """Start screenshot capture thread"""
        if self.is_running:
            return
        
        print("Starting screenshot manager...")
        self.is_running = True
        self.thread = threading.Thread(target=self._screenshot_loop, daemon=True)
        self.thread.start()
        print("Screenshot manager started")

    def stop(self):
        """Stop screenshot capture thread"""
        if not self.is_running:
            return

        print("Stopping screenshot manager...")
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=10)
                if self.thread.is_alive():
                    print("Warning: Screenshot thread did not stop gracefully")
            except Exception as e:
                print(f"Error stopping screenshot thread: {e}")
        
        self.thread = None
        print("Screenshot manager stopped")

    def __del__(self):
        """Ensure resources are cleaned up"""
        self.stop()

# Global screenshot manager instance
screenshot_manager = ScreenshotManager()
