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
            all_worlds = []
            lines = response.text.strip().split('\n')
            for line in lines[1:]:  # Skip header
                parts = line.split(',')
                if len(parts) >= 3:
                    world = parts[1].strip('"')
                    dc = parts[2].strip('"')
                    if dc not in dc_data:
                        dc_data[dc] = []
                    dc_data[dc].append(world)
                    all_worlds.append(world)
            dc_data["All"] = all_worlds
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

def get_price_history(item_id, location, days=7):
    """
    Get price history data for an item from a specific world or data center.
    
    Args:
        item_id (int): The ID of the item
        location (str): The world or data center name
        days (int): Number of days of history to retrieve
        
    Returns:
        dict: Price history data for the item
    """
    try:
        # Base URL for the history endpoint
        base_url = f"{UNIVERSALIS_BASE_URL}history/{location}/{item_id}"
        
        # Build query parameters as a string
        query_params = []
        
        # Add entries parameter
        query_params.append("entriesToReturn=3600")
        
        # Add time range parameter if days is specified
        if days > 0:
            # Convert days to milliseconds for the API
            # The statsWithin parameter expects milliseconds
            stats_within = days * 24 * 60 * 60 * 1000
            query_params.append(f"statsWithin={stats_within}")
            query_params.append(f"entriesWithin={stats_within}")
        
        # Combine base URL and query parameters
        url = base_url
        if query_params:
            url = f"{base_url}?{'&'.join(query_params)}"
        
        # Make the request
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            history_data = response.json()
            
            # No need to filter entries here, as the graph_utils.py now handles different response structures
            # and will filter based on timestamps if needed
            
            return history_data
        else:
            error_message = f"Failed to fetch price history: HTTP Status {response.status_code}"
            print(error_message)
            if response.status_code == 404:
                print("Item may not exist or have no history data")
            elif response.status_code == 429:
                print("Rate limit exceeded. Try again later.")
            
            try:
                error_content = response.text
                print(f"Error response content: {error_content}")
            except:
                pass
                
            return {"error": error_message, "entries": []}
    except requests.exceptions.Timeout:
        print(f"Timeout while fetching price history for item {item_id} from {location}")
        return {"error": "Request timed out", "entries": []}
    except Exception as e:
        print(f"Error fetching price history: {e}")
        return {"error": str(e), "entries": []}

def format_listing(listing, market_location):
    """
    Format a market listing for display.
    
    Args:
        listing (dict): The listing data
        market_location (str): The default market location
        
    Returns:
        str: Formatted listing string
    """
    from utils.translations import get_text
    
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
        formatted_time = get_text("market.unknown_time", "Unknown")
    
    # Format and return the listing using the translation template
    return get_text("market.listing_format", "{price} | {qty} | {total} | {world} | {time}").format(
        price=f"{price:,}".center(10),
        qty=str(quantity).center(6),
        total=f"{total:,}".center(10),
        world=world_name.center(10),
        time=formatted_time.center(20)
    )
