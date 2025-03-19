import requests
import json
import statistics
import os
import tkinter as tk
from api.universalis import UNIVERSALIS_BASE_URL
from api.xivapi import get_item_details

# Custom print function
def custom_print(text):
        print(f"[Market Analysis] {text}")

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

def get_lowest_price_in_dc(world_data, current_world=None, require_HQ=False):
    # Find the world with the lowest price
    lowest_price = float('inf')
    lowest_price_world = None
    
    for world, data in world_data.items():
        if world == current_world or not data.get("listings"):
            continue
            
        ## if require_HQ is True, only consider HQ listings
        filter_listings = [];
        if require_HQ:
            # print(f"filtering listings to only HQ items for {current_world}")
            filter_listings = [listing for listing in data.get("listings", []) if listing.get("hq")]
        else:
            filter_listings = data.get("listings", [])
        
        # find lowest price from filtered listings
        world_price = min(filter_listings, key=lambda x: x["pricePerUnit"])["pricePerUnit"]
        
        if world_price < lowest_price:
            lowest_price = world_price
            lowest_price_world = world
            
    return lowest_price, lowest_price_world

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
        item_details = get_item_details(item_id)
        require_HQ = False
        if item_details and "CanBeHq" in item_details:
            require_HQ = item_details["CanBeHq"] == 1 # require HQ if it can be HQ

        # Handle current_world = "All"
        if current_world == "All":
            return None
        
        # Get the current world's lowest price
        current_world_data = world_data[current_world]
        if not current_world_data.get("listings"):
            return None
            
        current_world_price = current_world_data["listings"][0]["pricePerUnit"]
        ## if require_HQ is True, only consider HQ listings
        filter_listings = [];
        if require_HQ:
            print("filtering listings to only HQ items")
            filter_listings = [listing for listing in current_world_data.get("listings", []) if listing.get("hq")]
        else:
            filter_listings = current_world_data.get("listings", [])
        
        # find lowest price from filtered listings
        current_world_price = min(filter_listings, key=lambda x: x["pricePerUnit"])["pricePerUnit"]

        current_dc_lowest_price, current_dc_lowest_price_world = get_lowest_price_in_dc(world_data, current_world, require_HQ)
        #custom_print(f"Current world: {current_world}, Current price: {current_world_price}, DC lowest price: {current_dc_lowest_price}, DC lowest price world: {current_dc_lowest_price_world}")

        dc_data = {}
        for dc in ["Aether", "Primal", "Crystal", "Dynamis"]:
            if dc != data_center:
                dc_world_data = get_world_data_in_dc(item_id, dc)
                dc_lowest_price, dc_lowest_price_world = get_lowest_price_in_dc(dc_world_data, current_world)
                dc_data[dc] = {
                    "dc_name": dc,
                    "dc_lowest_price": dc_lowest_price,
                    "dc_lowest_price_world": dc_lowest_price_world
                }
                #custom_print(f"DC: {dc}, DC lowest price: {dc_lowest_price}, DC lowest price world: {dc_lowest_price_world}")
        
        dc_data[data_center] = {
            "dc_name": data_center,
            "dc_lowest_price": current_dc_lowest_price,
            "dc_lowest_price_world": current_dc_lowest_price_world
        }

        # find lowest price across all DCs
        lowest_price = current_world_price
        lowest_price_world = current_world
        lowest_price_dc = data_center
        for dc in dc_data:
            if dc_data[dc]["dc_lowest_price"] < lowest_price:
                lowest_price = dc_data[dc]["dc_lowest_price"]
                lowest_price_world = dc_data[dc]["dc_lowest_price_world"]
                lowest_price_dc = dc_data[dc]["dc_name"]
                custom_print(f"Lowest price found in {dc}: {lowest_price} gil in {lowest_price_world}")
        
        # Check if there's a significant price difference (at least 10%)
        if lowest_price_world and lowest_price < current_world_price * 0.9:
            # Calculate potential profit
            potential_profit = current_world_price - lowest_price
            profit_percentage = (potential_profit / lowest_price) * 100
            
            return {
                "current_world": current_world,
                "current_price": current_world_price,
                "lowest_price_world": lowest_price_world,
                "lowest_price_dc": lowest_price_dc,
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