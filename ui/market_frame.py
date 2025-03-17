import tkinter as tk
from tkinter import ttk
from utils.translations import get_text
from utils.translation_widgets import create_label, create_button, create_labelframe, create_radiobutton, create_checkbutton

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
    notebook.add(watched_listings_frame, text=get_text("market.watched_listings", "Watched Listings"))
    
    # Title and description
    title_label = create_label(watched_listings_frame, "market.current_listings", "Current Listings", font=("Arial", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))
    
    description_label = create_label(watched_listings_frame, "market.view_listings", "View current market listings for this item.")
    description_label.pack(anchor="w", pady=(0, 15))
    
    # Price alert settings
    alert_frame = create_labelframe(watched_listings_frame, "alerts.price_alerts", "Price Alerts")
    alert_frame.pack(fill=tk.X, pady=(0, 15))
    
    alert_grid = ttk.Frame(alert_frame)
    alert_grid.pack(fill=tk.X, padx=10, pady=10)
    
    # Min price alert
    create_label(alert_grid, "alerts.min_price", "Min Price:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    min_price_var = tk.StringVar()
    ttk.Entry(alert_grid, textvariable=min_price_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    # Max price alert
    create_label(alert_grid, "alerts.max_price", "Max Price:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
    max_price_var = tk.StringVar()
    ttk.Entry(alert_grid, textvariable=max_price_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=2)
    
    # Set alert button
    set_alert_button = create_button(alert_grid, "alerts.set_alert", "Set Alert")
    set_alert_button.grid(row=0, column=4, padx=10, pady=2)
    
    # Active alerts frame
    active_alerts_frame = ttk.Frame(alert_frame)
    active_alerts_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
    
    create_label(active_alerts_frame, "alerts.active_alerts", "Active Alerts:", font=("Arial", 9, "bold")).pack(anchor="w")
    
    # Create active alerts listbox with scrollbar
    active_alerts_list_frame = ttk.Frame(active_alerts_frame)
    active_alerts_list_frame.pack(fill=tk.X, pady=5)
    
    active_alerts_listbox = tk.Listbox(active_alerts_list_frame, height=3)
    active_alerts_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    active_alerts_scrollbar = ttk.Scrollbar(active_alerts_list_frame, orient=tk.VERTICAL, command=active_alerts_listbox.yview)
    active_alerts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    active_alerts_listbox.config(yscrollcommand=active_alerts_scrollbar.set)
    
    # Delete alert button
    delete_alert_button = create_button(active_alerts_frame, "alerts.delete_alert", "Delete Selected Alert")
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
    notebook.add(price_history_frame, text=get_text("market.price_history", "Price History"))
    
    # Title and description
    title_label = create_label(price_history_frame, "market.price_history", "Price History", font=("Arial", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))
    
    description_label = create_label(price_history_frame, "market.view_history", "View historical price trends and predictions for this item.")
    description_label.pack(anchor="w", pady=(0, 15))
    
    # Controls frame (left side)
    controls_frame = ttk.Frame(price_history_frame)
    controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    
    # Time range selection
    time_frame = create_labelframe(controls_frame, "market.time_range", "Time Range")
    time_frame.pack(fill=tk.X, pady=5)
    
    time_ranges = [get_text("market.24_hours", "24 Hours"), 
                  get_text("market.7_days", "7 Days"), 
                  get_text("market.30_days", "30 Days"), 
                  get_text("market.90_days", "90 Days"), 
                  get_text("market.all_time", "All Time")]
    time_range_var = tk.StringVar(value=time_ranges[1])  # Default to 7 Days
    
    for i, range_text in enumerate(time_ranges):
        create_radiobutton(time_frame, f"market.{['24_hours', '7_days', '30_days', '90_days', 'all_time'][i]}", range_text, 
                         variable=time_range_var, value=range_text).pack(anchor="w", padx=10, pady=2)
    
    # Chart options
    options_frame = create_labelframe(controls_frame, "market.chart_options", "Chart Options")
    options_frame.pack(fill=tk.X, pady=10)
    
    # Checkboxes for chart options
    show_peaks_var = tk.BooleanVar(value=True)
    create_checkbutton(options_frame, "market.show_peaks", "Show Peaks/Valleys", 
                     variable=show_peaks_var).pack(anchor="w", padx=10, pady=2)
    
    show_trend_var = tk.BooleanVar(value=True)
    create_checkbutton(options_frame, "market.show_trend", "Show Trend Line", 
                     variable=show_trend_var).pack(anchor="w", padx=10, pady=2)
    
    show_avg_var = tk.BooleanVar(value=True)
    create_checkbutton(options_frame, "market.show_avg", "Show Average Price", 
                     variable=show_avg_var).pack(anchor="w", padx=10, pady=2)
    
    # Chart frame (right side)
    chart_frame = ttk.Frame(price_history_frame)
    chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Placeholder for chart
    chart_placeholder = create_label(chart_frame, "market.loading_data", "Price history chart will be displayed here", 
                                   font=("Arial", 12), anchor="center")
    chart_placeholder.pack(fill=tk.BOTH, expand=True)
    
    # Create tab for sale history
    sale_history_frame = ttk.Frame(notebook)
    notebook.add(sale_history_frame, text=get_text("market.sale_history", "Sale History"))
    
    # Title and description
    title_label = create_label(sale_history_frame, "market.sale_history", "Sale History", font=("Arial", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))
    
    description_label = create_label(sale_history_frame, "market.view_sales", "View recent sales and volume trends for this item.")
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

    # All Alerts TAB
    all_alerts_frame = ttk.Frame(notebook)
    notebook.add(all_alerts_frame, text=get_text("market.all_alerts", "All Alerts"))

    # Title and description
    title_label = create_label(all_alerts_frame, "market.all_alerts", "All Alerts", font=("Arial", 12, "bold"))
    title_label.pack(anchor="w", pady=(0, 10))
    
    description_label = create_label(all_alerts_frame, "market.view_alerts", "View all active alerts.")
    description_label.pack(anchor="w", pady=(0, 15))

    # Create active alerts listbox with scrollbar
    all_active_alerts_listbox = tk.Listbox(all_alerts_frame, font=("Courier New", 10))
    all_active_alerts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    all_active_alerts_scrollbar = ttk.Scrollbar(all_alerts_frame, orient=tk.VERTICAL, command=all_active_alerts_listbox.yview)
    all_active_alerts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    all_active_alerts_listbox.config(yscrollcommand=all_active_alerts_scrollbar.set)

    # Delete alert button
    all_delete_alert_button = create_button(all_alerts_frame, "alerts.delete_alert", "Delete Selected Alert")
    all_delete_alert_button.pack(anchor="e", pady=(5, 0))    
    
    # Return a dictionary with all the components
    return {
        "watched_listings_frame": watched_listings_frame,
        "price_history_frame": price_history_frame,
        "sale_history_frame": sale_history_frame,
        "listings_listbox": listings_listbox,
        "min_price_var": min_price_var,
        "max_price_var": max_price_var,
        "set_alert_button": set_alert_button,
        "active_alerts_listbox": active_alerts_listbox,
        "delete_alert_button": delete_alert_button,
        "time_range_var": time_range_var,
        "show_peaks_var": show_peaks_var,
        "show_trend_var": show_trend_var,
        "show_avg_var": show_avg_var,
        "chart_placeholder": chart_placeholder,
        "sale_history_listbox": sale_history_listbox,
        "all_alerts_frame": all_alerts_frame,
        "all_active_alerts_listbox": all_active_alerts_listbox,
        "all_delete_alert_button": all_delete_alert_button
    }
