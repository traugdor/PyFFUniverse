import requests
import json
import os

# Path to the settings file
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')

def load_discord_settings():
    """
    Load Discord webhook settings from the settings file.
    
    Returns:
        str: Discord webhook URL or None if not configured
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                return settings.get('discord_webhook_url', '')
        return ''
    except Exception as e:
        print(f"Error loading Discord settings: {e}")
        return ''

def save_discord_settings(webhook_url):
    """
    Save Discord webhook URL to the settings file.
    
    Args:
        webhook_url (str): The Discord webhook URL
    """
    try:
        # Load existing settings
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
        
        # Update webhook URL
        settings['discord_webhook_url'] = webhook_url
        
        # Save settings
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
            
        return True
    except Exception as e:
        print(f"Error saving Discord settings: {e}")
        return False

def send_discord_alert(title, message, color=0xFF5733):
    """
    Send an alert to Discord via webhook.
    
    Args:
        title (str): The alert title
        message (str): The alert message
        color (int, optional): The color of the embed. Defaults to orange.
        
    Returns:
        bool: True if the alert was sent successfully, False otherwise
    """
    webhook_url = load_discord_settings()
    if not webhook_url:
        return False
    
    try:
        # Create Discord embed
        embed = {
            "title": title,
            "description": message,
            "color": color
        }
        
        # Create payload
        payload = {
            "embeds": [embed]
        }
        
        # Send to Discord
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        return response.status_code == 204
    except Exception as e:
        print(f"Error sending Discord alert: {e}")
        return False
