"""
Open_Recall desktop application using Toga and FastAPI
"""
import threading
import uvicorn
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import time
import sys
import multiprocessing
import os
import warnings

# Filter out specific warnings from third-party libraries
warnings.filterwarnings("ignore", category=DeprecationWarning, module="defusedxml")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", module="uvicorn.protocols.websockets")

# Import the FastAPI app
from open_recall.main import app as fastapi_app
from open_recall.utils.settings import BASE_DIR

def run_server():
    """Run the FastAPI server in a separate thread"""
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")

class OpenRecallApp(toga.App):
    def startup(self):
        """
        Construct and show the Toga application with a WebView pointing to the FastAPI app
        """
        # Create main window with a larger size
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.size = (1200, 1000)
        
        # Create a loading screen
        self.create_loading_screen()
        self.main_window.show()
        
        # Start FastAPI server in a background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for the server to start
        self.wait_for_server()
        
        # Switch to the main view with WebView
        self.create_main_view()
    
    def create_loading_screen(self):
        """Create and display a loading screen while the server starts"""
        loading_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment='center'))
        
        # Add app icon
        icon_path = os.path.join(BASE_DIR, "static", "images", "icon.png")
        if os.path.exists(icon_path):
            try:
                icon_image = toga.Image(icon_path)
                icon_view = toga.ImageView(icon_image, style=Pack(width=200, height=200))
                loading_box.add(icon_view)
            except Exception:
                # If image loading fails, just skip it
                pass
        
        # Add loading text
        title_label = toga.Label(
            'Open_Recall',
            style=Pack(text_align='center', font_size=24, padding=(20, 0))
        )
        loading_box.add(title_label)
        
        loading_label = toga.Label(
            'Starting server, please wait...',
            style=Pack(text_align='center', font_size=16, padding=(10, 0))
        )
        loading_box.add(loading_label)
        
        # Add a progress bar
        progress_bar = toga.ProgressBar(max=100, value=0, style=Pack(padding=(20, 0), width=300))
        loading_box.add(progress_bar)
        
        # Set as main content
        self.main_window.content = loading_box
        self.progress_bar = progress_bar
    
    def wait_for_server(self):
        """Wait for the server to start and update progress bar"""
        max_attempts = 30
        for i in range(max_attempts):
            try:
                import requests
                response = requests.get("http://127.0.0.1:8000/")
                if response.status_code == 200:
                    # Server is ready
                    self.progress_bar.value = 100
                    time.sleep(0.5)  # Brief pause to show 100%
                    return
            except Exception:
                pass
            
            # Update progress
            self.progress_bar.value = (i + 1) * (100 / max_attempts)
            time.sleep(0.5)
    
    def create_main_view(self):
        """Create and display the main view with WebView"""
        # Create WebView that fills the entire window
        web_view = toga.WebView(
            url="http://127.0.0.1:8000",
            style=Pack(flex=1)  # This makes it take up all available space
        )
        
        # Create main box with the WebView
        main_box = toga.Box(
            children=[web_view],
            style=Pack(direction=COLUMN, flex=1)  # flex=1 makes it fill the window
        )
        
        # Set as main content
        self.main_window.content = main_box

def main():        
    return OpenRecallApp('Open_Recall', 'com.openrecall.open_recall')

if __name__ == '__main__':
    app = main()
    app.main_loop()
