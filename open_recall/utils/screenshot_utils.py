import asyncio
import os
import platform
import threading
import time
from datetime import datetime, timezone
from typing import Optional

import mss
import numpy as np
import psutil
from PIL import Image

from .db_utils import get_db, screenshot_crud
from .ocr_utils import process_image_ocr
from .schemas import EventType
from .settings import BASE_DIR, settings_manager
from .summarization import generate_summary


class ScreenshotManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, storage_path: str = None, capture_interval: int = None):
        if not hasattr(self, "initialized"):
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
        """Get active window information using platform-specific methods"""
        try:
            # Determine the platform
            system = platform.system()

            if system == "Windows":
                return self._get_active_window_info_windows()
            elif system == "Darwin":  # macOS
                return self._get_active_window_info_macos()
            elif system == "Linux":
                return self._get_active_window_info_linux()
            else:
                # Fallback for unknown platforms
                return "Unknown", "Unknown"
        except Exception as e:
            print(f"Error getting window info: {e}")
            return "Unknown", "Unknown"

    def _get_active_window_info_windows(self) -> tuple:
        """Get active window information for Windows"""
        try:
            # Dynamically import Windows-specific libraries
            import ctypes
            from ctypes import wintypes

            # Get the foreground window handle
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return "Unknown", "Unknown"

            # Get the process ID of the foreground window
            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            # Get process information
            try:
                process = psutil.Process(pid.value)
                app_name = process.name()

                # Try to get a better name from the executable path
                try:
                    exe = process.exe()
                    if exe:
                        better_name = os.path.basename(exe)
                        # Remove extension if present
                        better_name = os.path.splitext(better_name)[0]
                        if better_name and better_name != app_name:
                            app_name = better_name
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                # Get window title
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                window_title = buff.value

                # If window title is empty, try to use the process name or command line
                if not window_title:
                    try:
                        cmdline = process.cmdline()
                        window_title = " ".join(cmdline) if cmdline else app_name
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        window_title = app_name

                # Truncate if too long
                if len(window_title) > 100:
                    window_title = window_title[:97] + "..."

                return app_name, window_title

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return "Unknown", "Unknown"

        except Exception as e:
            print(f"Error getting Windows window info: {e}")
            return "Unknown", "Unknown"

    def _get_active_window_info_macos(self) -> tuple:
        """Get active window information for macOS"""
        try:
            # Try to use the AppKit approach first
            try:
                # Dynamically import macOS-specific libraries
                from AppKit import NSWorkspace

                # Get the active application
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                if active_app:
                    app_name = active_app["NSApplicationName"]
                    window_title = app_name  # macOS doesn't easily expose window titles
                    return app_name, window_title
            except (ImportError, Exception) as e:
                print(f"AppKit approach failed: {e}")
                pass

            # Fallback to using the 'osascript' command
            try:
                import subprocess

                # AppleScript to get the frontmost application name
                script = (
                    'tell application "System Events" to get name of first application process whose frontmost is true'
                )
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

                if result.returncode == 0 and result.stdout.strip():
                    app_name = result.stdout.strip()

                    # Try to get window title (might not work for all applications)
                    title_script = """
                    tell application "System Events"
                        set frontApp to first application process whose frontmost is true
                        set frontAppName to name of frontApp
                        tell process frontAppName
                            try
                                set winTitle to name of first window
                            on error
                                set winTitle to frontAppName
                            end try
                        end tell
                    end tell
                    """

                    title_result = subprocess.run(["osascript", "-e", title_script], capture_output=True, text=True)
                    if title_result.returncode == 0 and title_result.stdout.strip():
                        window_title = title_result.stdout.strip()
                    else:
                        window_title = app_name

                    return app_name, window_title
            except Exception as e:
                print(f"osascript approach failed: {e}")
                pass

            # If all else fails, use the psutil approach as a last resort
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                try:
                    proc_info = proc.as_dict(attrs=["pid", "name", "cpu_percent"])
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if processes:
                # Sort by CPU usage (descending)
                processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
                top_process = processes[0]
                return top_process["name"], top_process["name"]

            return "Unknown", "Unknown"

        except Exception as e:
            print(f"Error getting macOS window info: {e}")
            return "Unknown", "Unknown"

    def _get_active_window_info_linux(self) -> tuple:
        """Get active window information for Linux"""
        try:
            # Try using xdotool if available
            try:
                import subprocess

                # Get window ID of active window
                window_id = subprocess.run(["xdotool", "getactivewindow"], capture_output=True, text=True)
                if window_id.returncode == 0 and window_id.stdout.strip():
                    # Get window name/title
                    window_name = subprocess.run(
                        ["xdotool", "getwindowname", window_id.stdout.strip()], capture_output=True, text=True
                    )

                    # Get window PID
                    window_pid = subprocess.run(
                        ["xdotool", "getwindowpid", window_id.stdout.strip()], capture_output=True, text=True
                    )

                    if window_pid.returncode == 0 and window_pid.stdout.strip():
                        try:
                            pid = int(window_pid.stdout.strip())
                            process = psutil.Process(pid)
                            app_name = process.name()

                            # Try to get a better name from the executable path
                            try:
                                exe = process.exe()
                                if exe:
                                    better_name = os.path.basename(exe)
                                    # Remove extension if present
                                    better_name = os.path.splitext(better_name)[0]
                                    if better_name and better_name != app_name:
                                        app_name = better_name
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass

                            window_title = window_name.stdout.strip() if window_name.returncode == 0 else app_name

                            # Truncate if too long
                            if len(window_title) > 100:
                                window_title = window_title[:97] + "..."

                            return app_name, window_title
                        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            except (ImportError, FileNotFoundError) as e:
                print(f"xdotool approach failed: {e}")
                pass

            # Try using wmctrl if available
            try:
                import subprocess

                # Get active window info
                result = subprocess.run(["wmctrl", "-l", "-p"], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    # Parse wmctrl output to find the active window
                    import re

                    # Get the active window ID using xprop
                    active_id = subprocess.run(["xprop", "-root", "_NET_ACTIVE_WINDOW"], capture_output=True, text=True)

                    if active_id.returncode == 0 and active_id.stdout.strip():
                        # Extract the window ID
                        match = re.search(r"window id # (0x[0-9a-f]+)", active_id.stdout.strip())
                        if match:
                            window_id = match.group(1)

                            # Find this window in wmctrl output
                            for line in result.stdout.strip().split("\n"):
                                if window_id.lower() in line.lower():
                                    parts = line.split()
                                    if len(parts) >= 3:
                                        try:
                                            pid = int(parts[2])
                                            process = psutil.Process(pid)
                                            app_name = process.name()

                                            # Try to get a better name from the executable path
                                            try:
                                                exe = process.exe()
                                                if exe:
                                                    better_name = os.path.basename(exe)
                                                    # Remove extension if present
                                                    better_name = os.path.splitext(better_name)[0]
                                                    if better_name and better_name != app_name:
                                                        app_name = better_name
                                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                                pass

                                            # Window title is the rest of the line after the desktop number
                                            window_title = " ".join(parts[4:])

                                            # Truncate if too long
                                            if len(window_title) > 100:
                                                window_title = window_title[:97] + "..."

                                            return app_name, window_title
                                        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
                                            pass
            except (ImportError, FileNotFoundError) as e:
                print(f"wmctrl approach failed: {e}")
                pass

            # If all else fails, use the psutil approach as a last resort
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                try:
                    proc_info = proc.as_dict(attrs=["pid", "name", "cpu_percent"])
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if processes:
                # Sort by CPU usage (descending)
                processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)

                # Filter out system processes
                system_processes = ["Xorg", "xorg", "X", "systemd", "kwin", "gnome-shell", "plasmashell", "xfwm4"]

                for proc in processes:
                    if proc["name"] not in system_processes and proc.get("cpu_percent", 0) > 0.5:
                        return proc["name"], proc["name"]

                # If no suitable process found, return the top one
                return processes[0]["name"], processes[0]["name"]

            return "Unknown", "Unknown"

        except Exception as e:
            print(f"Error getting Linux window info: {e}")
            return "Unknown", "Unknown"

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
            summary = generate_summary(
                f"""
            Active App Name: {app_name}
            Screenshot Extracted Text: {extracted_text}
            """
            )

        # Save to database
        with next(get_db()) as db:
            screenshot_data = {
                "file_path": filename,
                "timestamp": datetime.now(timezone.utc),
                "app_name": app_name,
                "window_title": window_title,
                "extracted_text": extracted_text,
                "confidence_score": float(confidence),
                "summary": summary,
            }
            screenshot = screenshot_crud.create(db, data=screenshot_data)

            # Try to broadcast the new screenshot via WebSocket if available
            try:
                # Import here to avoid circular imports
                from open_recall.main import manager

                # Convert SQLAlchemy model to dict for JSON serialization
                screenshot_dict = {
                    "id": screenshot.id,
                    "file_path": screenshot.file_path,
                    "timestamp": screenshot.timestamp.isoformat(),
                    "app_name": screenshot.app_name,
                    "window_title": screenshot.window_title,
                    "extracted_text": screenshot.extracted_text,
                    "confidence_score": screenshot.confidence_score,
                    "summary": screenshot.summary,
                    "is_favorite": screenshot.is_favorite,
                    "notes": screenshot.notes,
                    "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in screenshot.tags],
                }

                async def broadcast():
                    asyncio.create_task(
                        manager.broadcast({"type": EventType.NEW_SCREENSHOT, "screenshot": screenshot_dict})
                    )

                asyncio.run(broadcast())
            except Exception as e:
                print(f"Failed to broadcast new screenshot: {e}")

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
