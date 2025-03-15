import tkinter as tk
from tkinter import ttk

def create_market_frame(notebook):
    """
    Create the market data tabs and frames.
    
    Args:
        notebook: The notebook widget to add tabs to
        
    Returns:
        dict: A dictionary containing the frames and their components
    """
    # Create tab for watched listings
    watched_listings_frame = ttk.Frame(notebook)
    notebook.add(watched_listings_frame, text="Watched Listings")
    
    # Title and description
    title_label = ttk.Label(watched_listings_frame, text="Current Listings", font=("Arial", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))
    
    description_label = ttk.Label(watched_listings_frame, text="View current market listings for this item.")
    description_label.pack(anchor="w", pady=(0, 15))
    
    # Price alert settings
    alert_frame = ttk.LabelFrame(watched_listings_frame, text="Price Alerts")
    alert_frame.pack(fill=tk.X, pady=(0, 15))
    
    alert_grid = ttk.Frame(alert_frame)
    alert_grid.pack(fill=tk.X, padx=10, pady=10)
    
    # Min price alert
    ttk.Label(alert_grid, text="Min Price:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    min_price_var = tk.StringVar()
    ttk.Entry(alert_grid, textvariable=min_price_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    # Max price alert
    ttk.Label(alert_grid, text="Max Price:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
    max_price_var = tk.StringVar()
    ttk.Entry(alert_grid, textvariable=max_price_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=2)
    
    # Set alert button
    set_alert_button = ttk.Button(alert_grid, text="Set Alert")
    set_alert_button.grid(row=0, column=4, padx=10, pady=2)
    
    # Active alerts frame
    active_alerts_frame = ttk.Frame(alert_frame)
    active_alerts_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
    
    ttk.Label(active_alerts_frame, text="Active Alerts:", font=("Arial", 9, "bold")).pack(anchor="w")
    
    # Create active alerts listbox with scrollbar
    active_alerts_list_frame = ttk.Frame(active_alerts_frame)
    active_alerts_list_frame.pack(fill=tk.X, pady=5)
    
    active_alerts_listbox = tk.Listbox(active_alerts_list_frame, height=3)
    active_alerts_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    active_alerts_scrollbar = ttk.Scrollbar(active_alerts_list_frame, orient=tk.VERTICAL, command=active_alerts_listbox.yview)
    active_alerts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    active_alerts_listbox.config(yscrollcommand=active_alerts_scrollbar.set)
    
    # Delete alert button
    delete_alert_button = ttk.Button(active_alerts_frame, text="Delete Selected Alert")
    delete_alert_button.pack(anchor="e", pady=(5, 0))
    
    # Listings frame
    listings_frame = ttk.Frame(watched_listings_frame)
    listings_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create listings listbox with scrollbar
    listings_listbox = tk.Listbox(listings_frame, font=("Courier New", 10))
    listings_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    listings_scrollbar = ttk.Scrollbar(listings_frame, orient=tk.VERTICAL, command=listings_listbox.yview)
    listings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listings_listbox.config(yscrollcommand=listings_scrollbar.set)
    
    # Create tab for price history
    price_history_frame = ttk.Frame(notebook)
    notebook.add(price_history_frame, text="Price History")
    
    # Title and description
    title_label = ttk.Label(price_history_frame, text="Price History", font=("Arial", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))
    
    description_label = ttk.Label(price_history_frame, text="View historical price trends and predictions for this item.")
    description_label.pack(anchor="w", pady=(0, 15))
    
    # Controls frame (left side)
    controls_frame = ttk.Frame(price_history_frame)
    controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    
    # Time range selection
    time_frame = ttk.LabelFrame(controls_frame, text="Time Range")
    time_frame.pack(fill=tk.X, pady=5)
    
    time_ranges = ["24 Hours", "7 Days", "30 Days", "90 Days", "All Time"]
    time_range_var = tk.StringVar(value=time_ranges[1])  # Default to 7 Days
    
    for i, range_text in enumerate(time_ranges):
        ttk.Radiobutton(time_frame, text=range_text, variable=time_range_var, 
                      value=range_text).pack(anchor="w", padx=10, pady=2)
    
    # Chart options
    options_frame = ttk.LabelFrame(controls_frame, text="Chart Options")
    options_frame.pack(fill=tk.X, pady=10)
    
    # Checkboxes for chart options
    show_peaks_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="Show Peaks/Valleys", 
                  variable=show_peaks_var).pack(anchor="w", padx=10, pady=2)
    
    show_trend_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(options_frame, text="Show Trend Line", 
                  variable=show_trend_var).pack(anchor="w", padx=10, pady=2)
    
    show_avg_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(options_frame, text="Show Average Price", 
                  variable=show_avg_var).pack(anchor="w", padx=10, pady=2)
    
    # Chart frame (right side)
    chart_frame = ttk.Frame(price_history_frame)
    chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Placeholder for chart
    chart_placeholder = ttk.Label(chart_frame, text="Price history chart will be displayed here", 
                                 font=("Arial", 12), anchor="center")
    chart_placeholder.pack(fill=tk.BOTH, expand=True)
    
    # Create tab for sale history
    sale_history_frame = ttk.Frame(notebook)
    notebook.add(sale_history_frame, text="Sale History")
    
    # Title and description
    title_label = ttk.Label(sale_history_frame, text="Sale History", font=("Arial", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))
    
    description_label = ttk.Label(sale_history_frame, text="View recent sales and volume trends for this item.")
    description_label.pack(anchor="w", pady=(0, 15))
    
    # Sale history frame
    sale_history_list_frame = ttk.Frame(sale_history_frame)
    sale_history_list_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create sale history listbox with scrollbar
    sale_history_listbox = tk.Listbox(sale_history_list_frame, font=("Courier New", 10))
    sale_history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    sale_history_scrollbar = ttk.Scrollbar(sale_history_list_frame, orient=tk.VERTICAL, command=sale_history_listbox.yview)
    sale_history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    sale_history_listbox.config(yscrollcommand=sale_history_scrollbar.set)
    
    # Return a dictionary with all the components
    return {
        "watched_listings_frame": watched_listings_frame,
        "price_history_frame": price_history_frame,
        "sale_history_frame": sale_history_frame,
        "listings_listbox": listings_listbox,
        "sale_history_listbox": sale_history_listbox,
        "min_price_var": min_price_var,
        "max_price_var": max_price_var,
        "time_range_var": time_range_var,
        "show_peaks_var": show_peaks_var,
        "show_trend_var": show_trend_var,
        "show_avg_var": show_avg_var,
        "set_alert_button": set_alert_button,
        "active_alerts_listbox": active_alerts_listbox,
        "delete_alert_button": delete_alert_button
    }
