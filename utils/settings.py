import os
import json
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default settings
DEFAULT_SETTINGS = {
    "enable_summarization": False,
    "capture_interval": 300  # Default 5 minutes (300 seconds)
}

class SettingsManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.settings_file = self._get_settings_file_path()
            self.settings = self._load_settings()
            self.initialized = True
    
    def _get_settings_file_path(self) -> str:
        """Get the path to the settings file"""
        return os.path.join(BASE_DIR, "settings.json")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create with defaults if file doesn't exist"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Ensure all default settings exist
                    for key, value in DEFAULT_SETTINGS.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            else:
                # Create settings directory if it doesn't exist
                os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
                # Create settings file with defaults
                self._save_settings(DEFAULT_SETTINGS)
                return DEFAULT_SETTINGS.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()
    
    def _save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value and save to file"""
        self.settings[key] = value
        return self._save_settings(self.settings)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def update_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        self.settings.update(settings_dict)
        return self._save_settings(self.settings)

# Global settings manager instance
settings_manager = SettingsManager()
