import requests
import json

# XIVAPI Base URL
XIVAPI_BASE_URL = "https://xivapi.com/Item/"

def get_item_details(item_id):
    """
    Get detailed information about an item from XIVAPI.
    
    Args:
        item_id (int): The ID of the item to retrieve
        
    Returns:
        dict: The item details from XIVAPI
    """
    try:
        url = f"{XIVAPI_BASE_URL}{item_id}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch item details: HTTP Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching item details: {e}")
        return None

def get_item_name(item_id, language="en"):
    """
    Get the name of an item in the specified language.
    
    Args:
        item_id (int): The ID of the item
        language (str): The language code (en, de, fr, ja)
        
    Returns:
        str: The item name in the specified language
    """
    item_details = get_item_details(item_id)
    if item_details:
        lang_map = {
            "en": "Name_en",
            "de": "Name_de",
            "fr": "Name_fr",
            "ja": "Name_ja"
        }
        return item_details.get(lang_map.get(language, "Name_en"), "Unknown Item")
    return "Unknown Item"

def get_item_description(item_id, language="en"):
    """
    Get the description of an item in the specified language.
    
    Args:
        item_id (int): The ID of the item
        language (str): The language code (en, de, fr, ja)
        
    Returns:
        str: The item description in the specified language
    """
    item_details = get_item_details(item_id)
    if item_details:
        lang_map = {
            "en": "Description_en",
            "de": "Description_de",
            "fr": "Description_fr",
            "ja": "Description_ja"
        }
        return item_details.get(lang_map.get(language, "Description_en"), "No description available.")
    return "No description available."
