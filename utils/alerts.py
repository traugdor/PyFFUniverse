import json
import os
import datetime

# Path to the alerts file
ALERTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alerts.json')

def load_alerts():
    """
    Load alerts from the alerts.json file.
    
    Returns:
        dict: Dictionary of alerts by item ID
    """
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f"Error loading alerts: {e}")
        return {}

def save_alerts(alerts):
    """
    Save alerts to the alerts.json file.
    
    Args:
        alerts (dict): Dictionary of alerts by item ID
    """
    try:
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=4)
    except Exception as e:
        print(f"Error saving alerts: {e}")

def set_alert(item_id, item_name, min_price=None, max_price=None, world=None, data_center=None):
    """
    Set a price alert for an item.
    
    Args:
        item_id (int): The ID of the item
        item_name (str): The name of the item
        min_price (int, optional): The minimum price to alert on
        max_price (int, optional): The maximum price to alert on
        world (str, optional): The world to monitor
        data_center (str, optional): The data center to monitor
        
    Returns:
        bool: True if the alert was set successfully, False otherwise
    """
    try:
        # Load existing alerts
        alerts = load_alerts()
        
        # Convert item_id to string for JSON compatibility
        item_id_str = str(item_id)
        
        # Create alert object
        alert = {
            "item_name": item_name,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "active": True
        }
        
        # Add optional parameters if provided
        if min_price is not None and min_price != "":
            try:
                alert["min_price"] = int(min_price)
            except ValueError:
                print(f"Invalid min price: {min_price}")
                return False
                
        if max_price is not None and max_price != "":
            try:
                alert["max_price"] = int(max_price)
            except ValueError:
                print(f"Invalid max price: {max_price}")
                return False
                
        if world and world != "All":
            alert["world"] = world
        elif data_center:
            alert["data_center"] = data_center
        
        # Add or update the alert
        if item_id_str not in alerts:
            alerts[item_id_str] = []
        
        # Check if a similar alert already exists
        for i, existing_alert in enumerate(alerts[item_id_str]):
            if (existing_alert.get("min_price") == alert.get("min_price") and
                existing_alert.get("max_price") == alert.get("max_price") and
                existing_alert.get("world") == alert.get("world") and
                existing_alert.get("data_center") == alert.get("data_center")):
                # Update the existing alert
                alerts[item_id_str][i] = alert
                save_alerts(alerts)
                return True
        
        # Add the new alert
        alerts[item_id_str].append(alert)
        
        # Save alerts
        save_alerts(alerts)
        
        return True
    except Exception as e:
        print(f"Error setting alert: {e}")
        return False

def get_alerts_for_item(item_id):
    """
    Get all alerts for an item.
    
    Args:
        item_id (int): The ID of the item
        
    Returns:
        list: List of alerts for the item
    """
    try:
        alerts = load_alerts()
        return alerts.get(str(item_id), [])
    except Exception as e:
        print(f"Error getting alerts for item: {e}")
        return []

def delete_alert(item_id, alert_index):
    """
    Delete an alert for an item.
    
    Args:
        item_id (int): The ID of the item
        alert_index (int): The index of the alert to delete
        
    Returns:
        bool: True if the alert was deleted successfully, False otherwise
    """
    try:
        alerts = load_alerts()
        item_id_str = str(item_id)
        
        if item_id_str in alerts and 0 <= alert_index < len(alerts[item_id_str]):
            alerts[item_id_str].pop(alert_index)
            
            # Remove the item if there are no more alerts
            if not alerts[item_id_str]:
                alerts.pop(item_id_str)
                
            save_alerts(alerts)
            return True
        
        return False
    except Exception as e:
        print(f"Error deleting alert: {e}")
        return False

def check_alerts(item_id, current_price):
    """
    Check if any alerts are triggered for an item.
    
    Args:
        item_id (int): The ID of the item
        current_price (int): The current price of the item
        
    Returns:
        list: List of triggered alerts
    """
    try:
        alerts = get_alerts_for_item(item_id)
        triggered_alerts = []
        
        for alert in alerts:
            if not alert.get("active", True):
                continue
                
            min_price = alert.get("min_price")
            max_price = alert.get("max_price")
            
            if (min_price is not None and current_price <= min_price) or \
               (max_price is not None and current_price >= max_price):
                triggered_alerts.append(alert)
                
        return triggered_alerts
    except Exception as e:
        print(f"Error checking alerts: {e}")
        return []
