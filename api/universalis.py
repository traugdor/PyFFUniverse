import requests
import json
import datetime

# Universalis API Base URL
UNIVERSALIS_BASE_URL = "https://universalis.app/api/v2/"

# Data Center URL
DC_URL = "https://raw.githubusercontent.com/xivapi/ffxiv-datamining/master/csv/World.csv"

def get_data_centers():
    """
    Get a dictionary of data centers and their worlds.
    
    Returns:
        dict: A dictionary mapping data center names to lists of worlds
    """
    try:
        response = requests.get(DC_URL, timeout=30)
        if response.status_code == 200:
            # Parse the CSV data
            dc_data = {}
            lines = response.text.strip().split('\n')
            for line in lines[1:]:  # Skip header
                parts = line.split(',')
                if len(parts) >= 3:
                    world = parts[1].strip('"')
                    dc = parts[2].strip('"')
                    if dc not in dc_data:
                        dc_data[dc] = []
                    dc_data[dc].append(world)
            return dc_data
        else:
            raise Exception(f"Failed to fetch data centers: HTTP Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching data centers: {e}")
        return {}

def get_marketable_items():
    """
    Get a list of all marketable item IDs from Universalis.
    
    Returns:
        list: A list of marketable item IDs
    """
    try:
        url = f"{UNIVERSALIS_BASE_URL}marketable"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch marketable items: HTTP Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching marketable items: {e}")
        return []

def get_market_data(item_id, location):
    """
    Get market data for an item from a specific world or data center.
    
    Args:
        item_id (int): The ID of the item
        location (str): The world or data center name
        
    Returns:
        dict: Market data for the item
    """
    try:
        url = f"{UNIVERSALIS_BASE_URL}{location}/{item_id}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch market data: HTTP Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return {}

def format_listing(listing, market_location):
    """
    Format a market listing for display.
    
    Args:
        listing (dict): The listing data
        market_location (str): The default market location
        
    Returns:
        str: Formatted listing string
    """
    price = listing.get("pricePerUnit", 0)
    quantity = listing.get("quantity", 0)
    total = price * quantity
    world_name = listing.get("worldName", market_location)
    
    # Format the last review time
    last_review_time = listing.get("lastReviewTime", 0)
    if last_review_time:
        # Convert timestamp to datetime
        review_time = datetime.datetime.fromtimestamp(last_review_time / 1000)
        formatted_time = review_time.strftime("%Y-%m-%d %H:%M")
    else:
        formatted_time = "Unknown"
    
    # Format and return the listing
    return f"{price:>10,} | {quantity:^6} | {total:>10,} | {world_name:^10} | {formatted_time:^20}"
