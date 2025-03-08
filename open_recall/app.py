"""
Open_Recall desktop application using Toga and FastAPI
"""
import threading
import uvicorn
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import time
import os
import warnings
import socket

# Filter out specific warnings from third-party libraries
warnings.filterwarnings("ignore", category=DeprecationWarning, module="defusedxml")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", module="uvicorn.protocols.websockets")

# Import the FastAPI app
from open_recall.main import app as fastapi_app, load_config
from open_recall.utils.settings import BASE_DIR

# Get configuration
config = load_config()
APP_PORT = int(os.environ.get('OPEN_RECALL_PORT', config['app']['port']))
APP_HOST = os.environ.get('OPEN_RECALL_HOST', config['app']['host'])

def find_free_port():
    """Find a free port if the default port is in use"""
    if is_port_in_use(APP_PORT):
        # Find a free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    return APP_PORT

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((APP_HOST, port))
            return False
        except OSError:
            return True

def run_server(port):
    """Run the FastAPI server in a separate thread"""
    uvicorn.run(fastapi_app, host=APP_HOST, port=port, log_level="info")

class OpenRecallApp(toga.App):
    def startup(self):
        """
        Construct and show the Toga application with a WebView pointing to the FastAPI app
        """
        # Create main window with a larger size
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.size = (1200, 1000)
        
        # Preload the icon image before creating the loading screen
        self.icon_image = self.load_app_icon()
        
        # Find a free port to use
        self.port = find_free_port()
        
        # Create a loading screen and show it immediately
        self.create_loading_screen()
        self.main_window.show()
        
        # Start the server initialization in a background thread
        # This allows the UI to be shown immediately
        threading.Thread(target=self.initialize_server, daemon=True).start()
    
    def initialize_server(self):
        """Initialize the server in the background and then switch to the main view"""
        # Start FastAPI server in a background thread
        server_thread = threading.Thread(target=run_server, args=(self.port,), daemon=True)
        server_thread.start()
        
        # Wait for the server to start
        self.wait_for_server()
        
        # Switch to the main view with WebView
        # This needs to be done on the main thread
        self.add_background_task(self.create_main_view)
    
    def load_app_icon(self):
        """Preload the app icon to ensure it displays correctly"""
        icon_path = os.path.join(BASE_DIR, "static", "images", "icon.png")
        if os.path.exists(icon_path):
            try:
                return toga.Image(icon_path)
            except Exception as e:
                print(f"Error loading icon: {e}")
        return None
    
    def create_loading_screen(self):
        """Create and display a loading screen while the server starts"""
        loading_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment='center'))
        
        # Add app icon if preloaded successfully
        if self.icon_image:
            icon_view = toga.ImageView(self.icon_image, style=Pack(width=200, height=200))
            loading_box.add(icon_view)
        
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
        
        # Force update of the UI
        self.main_window.content.refresh()
    
    def wait_for_server(self):
        """Wait for the server to start and update progress bar"""
        max_attempts = 30
        for i in range(max_attempts):
            try:
                import requests
                response = requests.get(f"http://{APP_HOST}:{self.port}/")
                if response.status_code == 200:
                    # Server is ready
                    self.progress_bar.value = 100
                    time.sleep(0.5)  # Brief pause to show 100%
                    return
            except Exception:
                pass
            
            # Update progress
            self.progress_bar.value = (i + 1) * (100 / max_attempts)
            
            # Force update of the UI - this needs to be done on the main thread
            self.add_background_task(self.update_progress_ui)
            time.sleep(0.5)
    
    def update_progress_ui(self):
        """Update the UI from the main thread"""
        self.main_window.content.refresh()
    
    def create_main_view(self, sender=None):
        """Create and display the main view with WebView"""
        # Create WebView that fills the entire window
        web_view = toga.WebView(
            url=f"http://{APP_HOST}:{self.port}",
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
    return OpenRecallApp(
        formal_name='Open_Recall',
        app_id='org.openrecall.open_recall',
        app_name='Open_Recall',
        author='Eng. Elias Owis',
        version='1.0.0',
        home_page='https://github.com/Eng-Elias/Open_Recall',
        description='Find and analyze anything you\'ve seen on your PC',
        icon=os.path.join(BASE_DIR, "static", "images", "icon")
    )

if __name__ == '__main__':
    app = main()
    app.main_loop()
