import requests
import json
import statistics
from api.universalis import UNIVERSALIS_BASE_URL

def get_all_dc_data(item_id, data_centers):
    """
    Get market data for an item across all data centers.
    
    Args:
        item_id (int): The ID of the item
        data_centers (list): List of data center names
        
    Returns:
        dict: Market data by data center
    """
    dc_data = {}
    
    for dc in data_centers:
        try:
            url = f"{UNIVERSALIS_BASE_URL}{dc}/{item_id}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                dc_data[dc] = response.json()
        except Exception as e:
            print(f"Error fetching data for {dc}: {e}")
    
    return dc_data

def get_world_data_in_dc(item_id, data_center):
    """
    Get market data for an item across all worlds in a data center.
    
    Args:
        item_id (int): The ID of the item
        data_center (str): The data center name
        
    Returns:
        dict: Market data by world
    """
    try:
        # First get the data center data to get the list of worlds
        dc_url = f"{UNIVERSALIS_BASE_URL}{data_center}/{item_id}"
        dc_response = requests.get(dc_url, timeout=30)
        
        if dc_response.status_code != 200:
            return {}
            
        dc_data = dc_response.json()
        
        # Extract unique worlds from the listings
        worlds = set()
        for listing in dc_data.get("listings", []):
            if "worldName" in listing:
                worlds.add(listing["worldName"])
        
        # Get data for each world
        world_data = {}
        for world in worlds:
            # Filter the listings for this world
            world_listings = [listing for listing in dc_data.get("listings", []) if listing.get("worldName") == world]
            
            # Create a data structure similar to the API response
            world_data[world] = {
                "listings": world_listings,
                "worldName": world,
                "dcName": data_center,
                "averagePrice": dc_data.get("averagePrice", 0),
                "averagePriceNQ": dc_data.get("averagePriceNQ", 0),
                "averagePriceHQ": dc_data.get("averagePriceHQ", 0),
                "regularSaleVelocity": dc_data.get("regularSaleVelocity", 0),
                "nqSaleVelocity": dc_data.get("nqSaleVelocity", 0),
                "hqSaleVelocity": dc_data.get("hqSaleVelocity", 0)
            }
            
            # Calculate world-specific average price
            if world_listings:
                prices = [listing["pricePerUnit"] for listing in world_listings]
                world_data[world]["currentAveragePrice"] = sum(prices) / len(prices)
            else:
                world_data[world]["currentAveragePrice"] = 0
        
        return world_data
    except Exception as e:
        print(f"Error fetching world data: {e}")
        return {}

def find_arbitrage_opportunities(item_id, current_world, data_center):
    """
    Find arbitrage opportunities for an item across worlds in a data center.
    
    Args:
        item_id (int): The ID of the item
        current_world (str): The current world name
        data_center (str): The data center name
        
    Returns:
        dict: Arbitrage opportunities
    """
    try:
        # Get market data for all worlds in the data center
        world_data = get_world_data_in_dc(item_id, data_center)
        
        if not world_data or current_world not in world_data:
            return None
        
        # Get the current world's lowest price
        current_world_data = world_data[current_world]
        if not current_world_data.get("listings"):
            return None
            
        current_world_price = current_world_data["listings"][0]["pricePerUnit"]
        
        # Find the world with the lowest price
        lowest_price = float('inf')
        lowest_price_world = None
        lowest_price_listing = None
        
        for world, data in world_data.items():
            if world == current_world or not data.get("listings"):
                continue
                
            world_price = data["listings"][0]["pricePerUnit"]
            
            if world_price < lowest_price:
                lowest_price = world_price
                lowest_price_world = world
                lowest_price_listing = data["listings"][0]
        
        # Check if there's a significant price difference (at least 10%)
        if lowest_price_world and lowest_price < current_world_price * 0.9:
            # Calculate potential profit
            potential_profit = current_world_price - lowest_price
            profit_percentage = (potential_profit / lowest_price) * 100
            
            return {
                "current_world": current_world,
                "current_price": current_world_price,
                "lowest_price_world": lowest_price_world,
                "lowest_price": lowest_price,
                "potential_profit": potential_profit,
                "profit_percentage": profit_percentage,
                "sale_velocity": current_world_data.get("regularSaleVelocity", 0)
            }
        
        return None
    except Exception as e:
        print(f"Error finding arbitrage opportunities: {e}")
        return None

def is_hot_item(market_data, threshold=5.0):
    """
    Determine if an item is 'hot' based on its sale velocity.
    
    Args:
        market_data (dict): Market data for the item
        threshold (float): Sale velocity threshold to consider an item 'hot'
        
    Returns:
        bool: True if the item is hot, False otherwise
    """
    try:
        # Check if the sale velocity is above the threshold
        sale_velocity = market_data.get("regularSaleVelocity", 0)
        return sale_velocity >= threshold
    except Exception as e:
        print(f"Error determining if item is hot: {e}")
        return False
