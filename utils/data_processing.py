import json
import requests
from utils.settings import load_settings

def get_item_names(item_ids, language = None):

    """
    Get item names for a list of item IDs from the FFXIV Teamcraft repository.
    
    Args:
        item_ids (list): List of item IDs
        
    Returns:
        dict: Dictionary mapping item IDs to item names
    """

    if language not in ["en", "de", "ja", "fr"]:
        lang_dict = {
            "English": "en",
            "Deutsch": "de",
            "日本語": "ja",
            "Français": "fr"
        }
        lang_code = lang_dict.get(language, "en")
    else:
        lang_code = language

    try:
        # Use the items.json from ffxiv-teamcraft for item names
        items_url = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json"
        items_response = requests.get(items_url, timeout=30)
        
        if items_response.status_code == 200:
            items_data = items_response.json()
            
            # Create a dictionary of item IDs to names
            item_names = {}
            for item_id in item_ids:
                item_id_str = str(item_id)
                if item_id_str in items_data and lang_code in items_data[item_id_str]:
                    item_names[item_id] = items_data[item_id_str][lang_code]
            
            return item_names
        else:
            raise Exception(f"Failed to fetch item details: HTTP Status {items_response.status_code}")
    except Exception as e:
        print(f"Error fetching item names: {e}")
        return {}

def create_item_dictionary(marketable_ids):
    """
    Create a dictionary of marketable items with their names.
    
    Args:
        marketable_ids (list): List of marketable item IDs
        
    Returns:
        tuple: (itemDictionary, printableItems) where itemDictionary is a list of [id, name] pairs
               and printableItems is a list of item names
    """
    # Get item names using selected language
    # read language from settings.json
    settings = load_settings()
    lang_code = settings["lang_code"]
    item_names = get_item_names(marketable_ids, lang_code)
    
    # Create the item dictionary as a list of [id, name] pairs
    item_dictionary = []
    for item_id in marketable_ids:
        if item_id in item_names:
            item_dictionary.append([item_id, item_names[item_id]])
    
    # Sort by item ID
    item_dictionary.sort(key=lambda x: x[0])
    
    # Extract just the names for display
    printable_items = [item[1] for item in item_dictionary]
    
    return item_dictionary, printable_items

def filter_items_by_search(printable_items, search_string):
    """
    Filter items by a search string.
    
    Args:
        printable_items (list): List of item names
        search_string (str): Search string to filter by
        
    Returns:
        list: Filtered list of item names
    """
    return [
        filtered_item
        for filtered_item in printable_items
        if search_string.upper() in filtered_item.upper()
    ]
