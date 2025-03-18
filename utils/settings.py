import json
import os

# Default settings
DEFAULT_SETTINGS = {
    "language": "English",
    "data_center": "North-America",
    "world": "All",
    "discord_webhook_url": "",
    "discord_alerts_enabled": False
}

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")

def load_settings():
    """
    Load user settings from the settings file.
    If the file doesn't exist, create it with default settings.
    
    Returns:
        dict: The user settings
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        else:
            # Create default settings file
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """
    Save user settings to the settings file.
    
    Args:
        settings (dict): The settings to save
    """
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")
