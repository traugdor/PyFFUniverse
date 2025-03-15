import tkinter as tk
from tkinter import ttk
from ui.html_compat import HTMLScrolledText
from utils.translations import get_text
from utils.translation_widgets import create_label, create_button, create_labelframe

def create_item_frame(parent):
    """
    Create the item details frame.
    
    Args:
        parent: The parent widget
        
    Returns:
        dict: A dictionary containing the frame and its components
    """
    # Create frame for item details
    item_details_frame = ttk.Frame(parent)
    item_details_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Item name
    name_var = tk.StringVar(value=get_text("item.select_item", "Select an item"))
    item_name_label = ttk.Label(item_details_frame, textvariable=name_var, font=("Arial", 14, "bold"))
    item_name_label.pack(anchor="w", pady=(0, 5))
    
    # Item description - using HTMLScrolledText instead of regular Text widget
    desc_frame = ttk.Frame(item_details_frame)
    desc_frame.pack(fill=tk.X)
    
    # Create HTML viewer for description
    desc_html = HTMLScrolledText(desc_frame, height=6, width=80, background="#f0f0f0")
    desc_html.pack(side=tk.LEFT, fill=tk.X, expand=True)
    desc_html.set_html(f"<p>{get_text('item.select_description', 'Select an item to view its description.')}</p>")
    
    # Item stats
    stats_frame = create_labelframe(item_details_frame, "item.market_statistics", "Market Statistics")
    stats_frame.pack(fill=tk.X, pady=(10, 0))
    
    stats_grid = ttk.Frame(stats_frame)
    stats_grid.pack(fill=tk.X, padx=10, pady=10)
    
    # Row 1
    create_label(stats_grid, "item.current_price", "Current Price:", anchor="w", width=15).grid(row=0, column=0, sticky="w", padx=5, pady=2)
    current_price_var = tk.StringVar(value="--")
    ttk.Label(stats_grid, textvariable=current_price_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    create_label(stats_grid, "item.avg_price", "Avg. Price:", anchor="w", width=15).grid(row=0, column=2, sticky="w", padx=5, pady=2)
    avg_price_var = tk.StringVar(value="--")
    ttk.Label(stats_grid, textvariable=avg_price_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=2)
    
    # Row 2
    create_label(stats_grid, "item.avg_daily_volume", "Avg. Daily Volume:", anchor="w", width=15).grid(row=1, column=0, sticky="w", padx=5, pady=2)
    avg_volume_var = tk.StringVar(value="--")
    ttk.Label(stats_grid, textvariable=avg_volume_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    create_label(stats_grid, "item.avg_daily_price", "Avg. Daily Price:", anchor="w", width=15).grid(row=1, column=2, sticky="w", padx=5, pady=2)
    avg_daily_price_var = tk.StringVar(value="--")
    ttk.Label(stats_grid, textvariable=avg_daily_price_var, width=10).grid(row=1, column=3, sticky="w", padx=5, pady=2)
    
    # Hot item alert frame
    hot_item_frame = ttk.Frame(stats_frame)
    hot_item_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    # Hot item indicator
    hot_item_var = tk.StringVar(value="")
    hot_item_label = ttk.Label(hot_item_frame, textvariable=hot_item_var, foreground="red", font=("Arial", 9, "bold"))
    hot_item_label.pack(anchor="w")
    
    # Arbitrage opportunity frame
    arbitrage_frame = create_labelframe(item_details_frame, "arbitrage.arbitrage_opportunity", "Arbitrage Opportunity")
    arbitrage_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Arbitrage info
    arbitrage_info_var = tk.StringVar(value=get_text("arbitrage.select_all", "Select 'All' worlds in a specific data center to check for arbitrage opportunities."))
    arbitrage_info_label = ttk.Label(arbitrage_frame, textvariable=arbitrage_info_var, wraplength=500, justify="left")
    arbitrage_info_label.pack(fill=tk.X, padx=10, pady=10)
    
    # Check arbitrage button
    check_arbitrage_button = create_button(arbitrage_frame, "arbitrage.check_arbitrage", "Check All Servers")
    check_arbitrage_button.pack(anchor="e", padx=10, pady=(0, 10))
    
    # Return a dictionary with all the components
    return {
        "frame": item_details_frame,
        "name_var": name_var,
        "desc_html": desc_html,  # Changed from desc_text to desc_html
        "current_price_var": current_price_var,
        "avg_price_var": avg_price_var,
        "avg_volume_var": avg_volume_var,
        "avg_daily_price_var": avg_daily_price_var,
        "hot_item_var": hot_item_var,
        "check_arbitrage_button": check_arbitrage_button,
        "arbitrage_info_var": arbitrage_info_var
    }
