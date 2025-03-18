import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import datetime
import threading
import time
import sys
from api.xivapi import get_item_details
from api.universalis import get_market_data, get_data_centers, get_marketable_items, format_listing, get_price_history
from ui.item_frame import create_item_frame
from ui.item_list import create_item_list
from ui.market_frame import create_market_frame
from utils.alerts import load_alerts, set_alert, delete_alert, get_alerts_for_item, check_all_alerts
from utils.market_analysis import is_hot_item, find_arbitrage_opportunities, custom_print
from utils.translations import get_text, set_language, get_language_code
from utils.translation_widgets import create_label, create_button, create_labelframe, set_translation_key
from utils.settings import load_settings, save_settings
from utils.data_processing import create_item_dictionary, filter_items_by_search
from utils.graph_utils import create_price_history_graph, get_time_range_days, create_chart_tooltip
from utils.discord_webhook import send_discord_alert, save_discord_settings, load_discord_settings
from plyer import notification
from win10toast import ToastNotifier
from win11toast import toast as ToastNotifier11
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def check_os():
    if sys.platform == "win32":
        return "Windows"
    elif sys.platform == "darwin":
        return "macOS"
    elif sys.platform == "linux":
        return "Linux"
    else:
        return "Unknown"

class PyFFUniverseApp:
    def __init__(self, root):
        # Create initial window
        self.root = root
        self.root.title(get_text("app.title", "PyFFUniverse"))
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Start maximized
        
        # Load settings
        self.settings = load_settings()
        
        # Set initial language
        set_language(get_language_code(self.settings["language"]))
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left panel for item list and search
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Create search frame
        self.search_frame = self.create_search_frame(left_panel)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create item listbox with scrollbar
        self.item_listbox = create_item_list(left_panel, self.on_item_select)
        
        # Create right panel for item details and market data
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create settings frame at the top
        settings_frame = ttk.Frame(right_panel)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language dropdown
        create_label(settings_frame, "app.language", "Language:").pack(side=tk.LEFT, padx=(0, 5))
        languages = ["English", "Deutsch", "日本語", "Français"]
        self.language_var = tk.StringVar(value=self.settings["language"])
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, values=languages, state="readonly", width=10)
        language_combo.pack(side=tk.LEFT, padx=(0, 10))
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Data center dropdown
        create_label(settings_frame, "app.data_center", "Data Center:").pack(side=tk.LEFT, padx=(0, 5))
        data_centers = ["Aether", "Primal", "Crystal", "Dynamis"]
        self.dc_var = tk.StringVar(value=self.settings["data_center"])
        dc_combo = ttk.Combobox(settings_frame, textvariable=self.dc_var, values=data_centers, state="readonly", width=15)
        dc_combo.pack(side=tk.LEFT, padx=(0, 10))
        dc_combo.bind("<<ComboboxSelected>>", self.on_dc_change)
        
        # World dropdown
        create_label(settings_frame,"app.world", "World:").pack(side=tk.LEFT, padx=(0, 5))
        self.world_var = tk.StringVar(value=self.settings["world"])
        self.world_combo = ttk.Combobox(settings_frame, textvariable=self.world_var, state="readonly", width=15)
        self.world_combo.pack(side=tk.LEFT)
        self.world_combo.bind("<<ComboboxSelected>>", self.on_world_change)
        
        # Discord settings button
        discord_button = create_button(settings_frame, "app.discord_settings", "Discord Settings", command=self.open_discord_settings)
        discord_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Create item details frame
        self.item_frame = create_item_frame(right_panel)
        
        # Create notebook for market data tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create market data tabs
        self.market_frame = create_market_frame(self.notebook)
        
        # Initialize variables for item details
        self.item_desc_html = self.item_frame["desc_html"]
        self.hot_item_var = self.item_frame["hot_item_label"]
        self.arbitrage_info_var = self.item_frame["arbitrage_info_label"]
        
        # Initialize variables for market data
        self.listings_listbox = self.market_frame["listings_listbox"]
        self.min_price_var = self.market_frame["min_price_var"]
        self.max_price_var = self.market_frame["max_price_var"]
        self.set_alert_button = self.market_frame["set_alert_button"]
        self.active_alerts_listbox = self.market_frame["active_alerts_listbox"]
        self.delete_alert_button = self.market_frame["delete_alert_button"]
        self.all_active_alerts_listbox = self.market_frame["all_active_alerts_listbox"]
        self.all_delete_alert_button = self.market_frame["all_delete_alert_button"]
        
        # Initialize variables for hot item and arbitrage
        self.check_arbitrage_button = self.item_frame["check_arbitrage_button"]
        
        # Configure the set alert button
        self.set_alert_button.config(command=self.on_set_alert)
        
        # Configure the delete alert button
        self.delete_alert_button.config(command=self.on_delete_alert)
        
        # Configure the check arbitrage button
        self.check_arbitrage_button.config(command=self.on_check_arbitrage)

        # Configure the all delete alert button
        self.all_delete_alert_button.config(command=self.on_delete_all_alerts)
        
        # Variable to track the currently selected item
        self.current_item_id = None
        self.current_item_name = None
        
        # Dictionary to track alert indices
        self.alert_indices = {}
        
        # Load data
        self.display_all_alerts()
        self.load_data()
        self.start_alerts_monitor()
        
        # Set up close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_alerts_monitor(self):
        """
        Start the alerts monitor thread.
        """
        self.alerts_running = True
        self.alerts_thread = threading.Thread(target=self.alerts_monitor, daemon=True)
        self.alerts_thread.start()

    def alerts_monitor(self):
        """
        Monitor active alerts and check for price changes.
        """
        while self.alerts_running:
            all_alerts = check_all_alerts()
            for alert in all_alerts:
                # Create alert message
                alert_message = f"{alert['item_name']} is now {alert['pricePerUnit']} gil in {alert['source']} which is {alert['direction']} the your set threshold."
                
                # Send desktop notification
                if check_os() == "Linux" or check_os() == "macOS":
                    notification.notify(
                        title="Price Alert",
                        message=alert_message,
                        timeout=10,
                        app_name="PyFFUniverse",
                        toast=True
                    )
                else:
                    toast = MyToastNotifier()
                    try:
                        toast.show_toast(
                            "PyFFUniverse - Price Alert",
                            alert_message,
                            duration=10
                        )
                    except TypeError as e:
                        pass
                
                # Send Discord alert if configured
                send_discord_alert(
                    "PyFFUniverse - Price Alert",
                    alert_message,
                    color=0xFF5733  # Orange color
                )
            
            self.alerts_sleep(600)

    def alerts_sleep(self, seconds):
        """
        Sleep for a specified number of seconds.
        
        Args:
            seconds (int): The number of seconds to sleep
        """
        # Get the time now
        start_time = time.time()
        sleep_time = 1
        loop_start_time = start_time
        loop_end_time = loop_start_time
        for i in range(seconds):
            loop_start_time = time.time()
            if not self.alerts_running:
                break
            sleep_time = min(1, sleep_time - (loop_end_time - loop_start_time))
            # If remaining time is less than 1 second, sleep for remaining time
            if(seconds - (loop_end_time - start_time) < 1):
                sleep_time = seconds - (loop_end_time - start_time)
            if sleep_time < 0:
                sleep_time = 1
            time.sleep(sleep_time)
            loop_end_time = time.time()
            # if we have exceeded the sleep time, break
            if loop_end_time - start_time > seconds:
                break
        
    def create_search_frame(self, parent):
        """
        Create the search frame with search bar and filters
        
        Args:
            parent: The parent widget
            
        Returns:
            ttk.Frame: The search frame
        """
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search label and entry
        search_label = create_label(search_frame, "app.search", "Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<Return>", self.on_search)
        
        # Search button
        search_button = create_button(search_frame, "app.search", "Search", command=self.on_search)
        search_button.pack(side=tk.LEFT, padx=(0, 20))
        
        return search_frame

    def load_data(self):
        try:
            # Show loading screen
            self.show_loading_screen(get_text("app.loading", "Loading item data..."))
            
            # Get marketable items directly from Universalis
            self.update_loading_progress(20, get_text("app.loading", "Fetching marketable items from Universalis..."))
            
            # Use the Universalis marketable endpoint
            marketable_ids = get_marketable_items()
            self.update_loading_progress(40, get_text("app.loading", "Fetching item details..."), f"Found {len(marketable_ids)} marketable items")
            
            # Process item data
            self.update_loading_progress(60, get_text("app.loading", "Processing item data..."))
            
            # Create item dictionary and printable items list
            global itemDictionary, printableItems
            itemDictionary, printableItems = create_item_dictionary(marketable_ids)
            
            # Update item list
            self.update_item_list(printableItems)
            
            # Initialize the world dropdown based on the saved data center
            self.initialize_world_dropdown()
            
            self.update_loading_progress(100, get_text("app.loading", "Item data loaded successfully"), f"Loaded {len(itemDictionary)} items")
            
            # Hide loading screen
            self.hide_loading_screen()
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"Failed to load data: {e}")
            if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
                self.hide_loading_screen()

    def show_loading_screen(self, message):
        """
        Show a loading screen with progress bar.
        
        Args:
            message (str): The loading message to display
        """
        # Create a loading screen
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title(get_text("app.loading", "Loading"))
        self.loading_window.geometry("400x200")
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        
        # Center the loading window
        self.loading_window.update_idletasks()
        width = self.loading_window.winfo_width()
        height = self.loading_window.winfo_height()
        x = (self.loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.loading_window.winfo_screenheight() // 2) - (height // 2)
        self.loading_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Create a frame for the close button
        close_frame = ttk.Frame(self.loading_window)
        close_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add close button in the top-right corner
        close_button = ttk.Button(close_frame, text="X", width=3, command=self.hide_loading_screen)
        close_button.pack(side=tk.RIGHT)
        
        # Add loading message
        self.loading_label = tk.Label(self.loading_window, text=message, font=("Arial", 12))
        self.loading_label.pack(pady=20)
        
        # Add progress bar
        self.loading_progress = ttk.Progressbar(self.loading_window, length=300, mode="determinate")
        self.loading_progress.pack(pady=10)
        
        # Add details label
        self.loading_details = tk.Label(self.loading_window, text=get_text("app.loading", "Initializing..."))
        self.loading_details.pack(pady=10)
        
        # Update UI
        self.loading_window.update()
    
    def update_loading_progress(self, percent, message, details=None):
        """
        Update the loading progress bar and message.
        
        Args:
            percent (int): The progress percentage (0-100)
            message (str): The loading message to display
            details (str, optional): Additional details to display
        """
        if hasattr(self, 'loading_progress'):
            self.loading_progress["value"] = percent
            self.loading_label.config(text=message)
            if details:
                self.loading_details.config(text=details)
            self.loading_window.update()
    
    def hide_loading_screen(self):
        """
        Hide and destroy the loading screen.
        """
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
    
    def initialize_world_dropdown(self):
        """
        Initialize the world dropdown based on the selected data center.
        """
        try:
            # Get the saved data center
            dc = self.dc_var.get()
            
            # Fetch servers for the data center
            dc_response = json.loads(requests.get("https://xivapi.com/servers/dc").text)
            servers = dc_response[str(dc)]
            servers.insert(0, "All")
            
            # Update the world dropdown
            self.world_combo.config(values=servers)
            
            # Set the world to the saved value if it exists in the list, otherwise default to "All"
            saved_world = self.settings["world"]
            if saved_world in servers:
                self.world_var.set(saved_world)
            else:
                self.world_var.set("All")
                self.settings["world"] = "All"
                save_settings(self.settings)
        except Exception as e:
            print(f"Failed to initialize world dropdown: {e}")
            self.world_var.set("All")
    
    def update_item_list(self, items):
        """
        Update the item listbox with the given items.
        
        Args:
            items (list): List of item names to display
        """
        self.item_listbox.delete(0, tk.END)
        for item in items:
            self.item_listbox.insert(tk.END, item)
    
    def on_search(self, event=None):
        """
        Handle search button click.
        """
        search_string = self.search_var.get()
        updated_list = filter_items_by_search(printableItems, search_string)
        self.update_item_list(updated_list)
    
    def on_language_change(self, event):
        """
        Handle language change event.
        
        Args:
            event: The event object
        """
        try:
            # Get the selected language
            language = self.language_var.get()
            
            # Save the language setting
            self.settings["language"] = language
            self.settings["lang_code"] = get_language_code(language)
            save_settings(self.settings)
            
            # Update the language in the translator
            set_language(get_language_code(language))
            
            # Update UI text elements
            self.update_ui_text()
            
            # Refresh the current item if one is selected
            selected_indices = self.item_listbox.curselection()
            if selected_indices:
                self.on_item_select(None)
            
            # change language of individual widgets not updated by update_ui_text
            self.item_desc_html.set_html(f"<p>{get_text('item.select_description', 'Select an item to view its description.')}</p>")

            # reload data
            self.display_all_alerts()
            self.load_data()

        except Exception as e:
            messagebox.showerror(get_text("errors.api_error", "Error"), f"Failed to save language setting: {e}")
    
    def update_ui_text(self):
        """
        Update all UI text elements with the current language
        """
        # Update window title
        self.root.title(get_text("app.title", "PyFFUniverse"))
        
        # Update labels
        for widget in self.root.winfo_children():
            self.update_widget_text(widget)
    
    def update_widget_text(self, widget):
        """
        Recursively update text in widgets
        
        Args:
            widget: The widget to update
        """
        # Update text in labels, buttons, etc.
        if hasattr(widget, 'cget') and hasattr(widget, 'config'):
            if 'text' in widget.config():
                # First check if widget has a translation key
                if hasattr(widget, '_translation_key'):
                    widget.config(text=get_text(widget._translation_key, widget._translation_default))
        
        # Recursively process child widgets
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                self.update_widget_text(child)
    
    def on_dc_change(self, event):
        """
        Handle data center change event.
        
        Args:
            event: The event object
        """
        try:
            dc = self.dc_var.get()
            dc_response = json.loads(requests.get("https://xivapi.com/servers/dc").text)
            servers = dc_response[str(dc)]
            servers.insert(0, "All")
            
            self.world_combo.config(values=servers)
            self.world_combo.update()
            self.world_var.set("All")
            
            # Save the data center setting
            self.settings["data_center"] = dc
            self.settings["world"] = "All"  # Reset world to All when DC changes
            save_settings(self.settings)
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"Failed to load data center information: {e}")
    
    def on_world_change(self, event):
        """
        Handle world change event.
        
        Args:
            event: The event object
        """
        try:
            # Save the world setting
            self.settings["world"] = self.world_var.get()
            save_settings(self.settings)
            
            # Refresh the item details if an item is selected
            selected_indices = self.item_listbox.curselection()
            if selected_indices:
                self.on_item_select(None)
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"Failed to save world setting: {e}")
    
    def on_item_select(self, event):
        """
        Handle item selection from the search results.
        
        Args:
            event: The event object
        """
        language = self.language_var.get()
        lang_codes = {
            "English": {
                "name": "Name_en",
                "description": "Description_en"
            },
            "Deutsch": {
                "name": "Name_de",
                "description": "Description_de"
            },
            "日本語": {
                "name": "Name_ja",
                "description": "Description_ja"
            },
            "Français": {
                "name": "Name_fr",
                "description": "Description_fr"
            }
        }
        name_code = lang_codes.get(language, "en")["name"]
        description_code = lang_codes.get(language, "en")["description"]
        try:
            # Get the selected item
            selected_index = self.item_listbox.curselection()
            if not selected_index:
                return
                
            selected_item = self.item_listbox.get(selected_index)
            
            # Get the item ID
            item_id = None
            for item in itemDictionary:
                if item[1] == selected_item:
                    item_id = item[0]
                    break
            
            if item_id:
                # Get the selected world or data center
                world = self.world_var.get()
                dc = self.dc_var.get()
                
                # Determine the market location
                market_location = dc if world == "All" else world
                
                # Clear the item description
                self.item_desc_html.set_html("<p>Loading item details...</p>")
                
                # Clear the listings
                self.listings_listbox.delete(0, tk.END)
                self.listings_listbox.insert(tk.END, "Loading market data...")
                
                # Fetch item details
                item_details = get_item_details(item_id)
                
                if item_details:
                    # Create HTML description
                    description = f"<p>{item_details[name_code]}</p>"
                    
                    # Add item description if available
                    if description_code in item_details:
                        description += f"<p>{item_details[description_code]}</p>"
                    
                    # Update the item description
                    self.item_desc_html.set_html(description)
                    
                    # Update the current item ID and name
                    self.current_item_id = item_id
                    self.current_item_name = selected_item
                    
                    # Display alerts for the selected item
                    self.display_alerts_for_current_item()
                    
                    # Reset hot item and arbitrage indicators
                    self.hot_item_var.config( text = "")
                    self.arbitrage_info_var.config( text = "")
                    
                    # Fetch market data in a separate thread to avoid freezing the UI
                    self.fetch_market_data(item_id, market_location)
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"Failed to load item details: {e}")
    
    def fetch_market_data(self, item_id, market_location):
        """
        Fetch market data for an item from a specific location.
        
        Args:
            item_id (int): The ID of the item
            market_location (str): The world or data center name
        """
        try:
            # Clear the listings listbox
            self.listings_listbox.delete(0, tk.END)
            
            # Show loading message
            self.listings_listbox.insert(tk.END, "Loading market data...")
            self.root.update_idletasks()  # Update the UI to show loading message
            check_all_alerts()
            
            # Update the price history chart
            self.update_price_history_chart(item_id, market_location)
            
            # Define a function to fetch market data in a separate thread
            def fetch_data():
                try:
                    # Fetch market data
                    market_response = get_market_data(item_id, market_location)
                    
                    # Update the UI in the main thread
                    self.root.after(0, lambda: self.update_market_data(market_response, market_location))
                except Exception as e:
                    # Update the UI in the main thread
                    self.root.after(0, lambda: self.show_market_error(str(e)))
            
            # Start a new thread to fetch market data
            threading.Thread(target=fetch_data).start()
        except Exception as e:
            self.listings_listbox.delete(0, tk.END)
            self.listings_listbox.insert(tk.END, f"Error fetching market data: {str(e)}")

    def update_price_history_chart(self, item_id=None, market_location=None):
        """
        Update the price history chart for the given item and market location.
        If no item_id or market_location is provided, use the currently selected ones.
        
        Args:
            item_id (int, optional): The ID of the item. If None, use current_item_id.
            market_location (str, optional): The world or data center name. If None, use current market location.
        """
        try:
            # Use current item and market location if not provided
            if item_id is None:
                item_id = self.current_item_id
            if market_location is None:
                # Determine market location based on settings
                if self.settings.get("use_dc", False):
                    market_location = self.dc_var.get()
                else:
                    world = self.world_var.get()
                    market_location = world if world != "All" else self.dc_var.get()
            
            # If no item is selected, return
            if not item_id:
                return
            
            # Get the chart frame from the market frame
            chart_frame = self.market_frame.get("chart_frame")
            chart_placeholder = self.market_frame["chart_placeholder"]
            
            # Get the selected time range
            time_range = self.market_frame["time_range_var"].get()
            
            # Get the chart options
            show_peaks = self.market_frame["show_peaks_var"].get()
            show_trend = self.market_frame["show_trend_var"].get()
            show_avg = self.market_frame["show_avg_var"].get()
            
            # Convert time range to days
            days = get_time_range_days(time_range)
            
            # Clear previous chart if it exists and destroy the widget
            if hasattr(self, 'chart_canvas_widget') and self.chart_canvas_widget.winfo_exists():
                self.chart_canvas_widget.pack_forget()
                self.chart_canvas_widget.destroy()
                
            # Show loading message in chart placeholder
            chart_placeholder.config(text=get_text("market.loading_chart", "Loading price history..."))
            chart_placeholder.pack(fill=tk.BOTH, expand=True)
            
            # Update the UI to show the loading message
            self.root.update_idletasks()
            
            # Fetch price history data
            price_history_response = get_price_history(item_id, market_location, days)
            
            # Store the price history data for tooltip functionality
            self.price_history_data = price_history_response
            
            # Create the price history graph
            fig, chart_data = create_price_history_graph(
                price_history_response, 
                time_range, 
                show_peaks=show_peaks, 
                show_trend=show_trend, 
                show_avg=show_avg
            )
            
            # Store the chart data for interactive features
            self.chart_data = chart_data
            
            # Hide the placeholder text
            chart_placeholder.config(text="")
            chart_placeholder.pack_forget()
            
            # Create a new FigureCanvasTkAgg widget
            self.figure_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            self.figure_canvas.draw()
            self.chart_canvas_widget = self.figure_canvas.get_tk_widget()
            self.chart_canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # Create a tooltip for the chart if it doesn't exist yet
            if not hasattr(self, 'chart_tooltip') or not hasattr(self.chart_tooltip, 'winfo_exists') or not self.chart_tooltip.winfo_exists():
                if chart_frame:
                    # Use the function from graph_utils.py to create the tooltip
                    self.chart_tooltip, self.chart_motion_handler = create_chart_tooltip(self.chart_canvas_widget, chart_frame)
            
            # Set up event handlers for the chart options if not already done
            if not hasattr(self, "_chart_options_initialized"):
                # Time range radio buttons
                self.market_frame["time_range_var"].trace_add("write", lambda *args: self.update_price_history_chart())
                
                # Chart option checkboxes
                self.market_frame["show_peaks_var"].trace_add("write", lambda *args: self.update_price_history_chart())
                self.market_frame["show_trend_var"].trace_add("write", lambda *args: self.update_price_history_chart())
                self.market_frame["show_avg_var"].trace_add("write", lambda *args: self.update_price_history_chart())
                
                self._chart_options_initialized = True
            
            # Set up mouse events for the chart
            self.chart_canvas_widget.bind("<Motion>", lambda event: self.on_chart_motion(event))
            self.chart_canvas_widget.bind("<Leave>", lambda event: self.chart_tooltip.place_forget())
            
        except Exception as e:
            # Show error message in chart placeholder
            chart_placeholder = self.market_frame["chart_placeholder"]
            chart_placeholder.config(text=f"Error: {str(e)}")
            print(f"Error updating price history chart: {e}")
    
    def on_chart_motion(self, event):
        """
        Handle mouse motion over the chart to show tooltips with price data.
        
        Args:
            event: The mouse event
        """
        if hasattr(self, 'chart_motion_handler') and hasattr(self, 'chart_data') and hasattr(self, 'chart_tooltip'):
            self.chart_motion_handler(event, self.chart_data, self.chart_tooltip)
    
    def update_market_data(self, market_response, market_location):
        """
        Update the UI with market data.
        
        Args:
            market_response (dict): The market data response
            market_location (str): The world or data center name
        """
        # Clear the loading message
        self.listings_listbox.delete(0, tk.END)
        
        # Check if there are listings
        if "listings" in market_response and market_response["listings"]:
            # Add header with translations
            header_format = get_text("market.listings_header_format", "{price} | {qty} | {total} | {world} | {last_updated}")
            header = header_format.format(
                price=get_text("market.price_header", "Price").center(10),
                qty=get_text("market.quantity_header", "Qty").center(6),
                total=get_text("market.total_header", "Total").center(10),
                world=get_text("market.world_header", "World").center(10),
                last_updated=get_text("market.last_updated_header", "Last Updated").center(20)
            )
            self.listings_listbox.insert(tk.END, header)
            self.listings_listbox.insert(tk.END, "-" * 65)
            
            # Add each listing
            for listing in market_response["listings"]:
                listing_text = format_listing(listing, market_location)
                self.listings_listbox.insert(tk.END, listing_text)
                
            # Update market statistics
            self.update_market_statistics(market_response)
        else:
            self.listings_listbox.insert(tk.END, get_text("market.no_listings", "No listings found for this item."))
            
            # Clear market statistics
            self.clear_market_statistics()
    
    def update_market_statistics(self, market_response):
        """
        Update the market statistics in the UI.
        
        Args:
            market_response (dict): The market data response
        """
        try:
            # Get statistics from the market response
            current_price = market_response["listings"][0]["pricePerUnit"] if market_response["listings"] else 0
            avg_price = market_response.get("currentAveragePrice", 0)
            avg_volume = market_response.get("regularSaleVelocity", 0)
            avg_daily_price = market_response.get("averagePrice", 0)
            
            # Update the UI
            self.item_frame["current_price_var"].set(f"{current_price:,}")
            self.item_frame["avg_price_var"].set(f"{avg_price:,.0f}")
            self.item_frame["avg_volume_var"].set(f"{avg_volume:.1f}")
            self.item_frame["avg_daily_price_var"].set(f"{avg_daily_price:,.0f}")
            
            # Check if the item is hot (high sale velocity)
            if is_hot_item(market_response):
                self.hot_item_var.config( text = get_text("app.hot_item", "HOT ITEM! This item sells frequently."))
            else:
                self.hot_item_var.config( text = "")
            
            # Check for arbitrage opportunities
            self.check_arbitrage_opportunities(market_response)
        except Exception as e:
            print(f"Error updating market statistics: {e}")
            self.clear_market_statistics()
    
    def clear_market_statistics(self):
        """
        Clear the market statistics in the UI.
        """
        self.item_frame["current_price_var"].set("--")
        self.item_frame["avg_price_var"].set("--")
        self.item_frame["avg_volume_var"].set("--")
        self.item_frame["avg_daily_price_var"].set("--")
        self.hot_item_var.config( text = "")
        self.arbitrage_info_var.config( text = "")
    
    def check_arbitrage_opportunities(self, market_response):
        """
        Check for arbitrage opportunities within the current data center.
        
        Args:
            market_response (dict): The market data response
        """
        try:
            # Make sure we have the necessary data
            if not self.current_item_id or not market_response.get("listings"):
                return
                
            # Get the current world and data center
            current_world = self.world_var.get()
            data_center = self.dc_var.get()
            
            # If we're viewing all worlds in a data center, we can check for arbitrage
            if current_world == "All" and data_center != "All":
                # Find arbitrage opportunities
                arbitrage = find_arbitrage_opportunities(
                    item_id=self.current_item_id,
                    current_world=None,  # We'll analyze all worlds
                    data_center=data_center
                )
                
                if arbitrage:
                    # Format the arbitrage information
                    message = f"{get_text('app.arbitrage', 'HOT ITEM! Arbitrage Opportunity!')} Buy from {arbitrage['lowest_price_world']}@{arbitrage['lowest_price_dc']} for {arbitrage['lowest_price']:,} gil and sell on {arbitrage['current_world']} for {arbitrage['current_price']:,} gil. Potential profit: {arbitrage['potential_profit']:,} gil ({arbitrage['profit_percentage']:.1f}%)."
                    self.arbitrage_info_var.config( text = message)
                else:
                    self.arbitrage_info_var.config( text = get_text("app.no_arbitrage", "No significant price differences found between worlds."))
            else:
                self.arbitrage_info_var.config( text = get_text("app.select_dc", "Select 'All' worlds in a specific data center to check for arbitrage opportunities."))
        except Exception as e:
            print(f"Error checking arbitrage opportunities: {e}")
            self.arbitrage_info_var.config( text = f"{get_text('app.error', 'Error checking arbitrage:')} {str(e)}")
    
    def show_market_error(self, error_message):
        """
        Show an error message in the listings listbox.
        
        Args:
            error_message (str): The error message to display
        """
        self.listings_listbox.delete(0, tk.END)
        self.listings_listbox.insert(tk.END, f"{get_text('app.error', 'Error fetching market data:')} {error_message}")
        
        # Clear market statistics when there's an error
        self.clear_market_statistics()
    
    def on_check_arbitrage(self):
        """
        Handle check arbitrage button click.
        """
        try:
            # Check if an item is selected
            if not self.current_item_id:
                messagebox.showwarning(get_text("app.no_item", "No Item Selected"), get_text("app.select_item", "Please select an item first."))
                return
            
            # Get the current data center
            data_center = self.dc_var.get()
            if data_center == "All":
                messagebox.showinfo(get_text("app.select_dc", "Select Data Center"), get_text("app.select_dc_info", "Please select a specific data center to check for arbitrage opportunities."))
                return
            
            # Show loading message
            self.arbitrage_info_var.config( text = get_text("app.checking_arbitrage", "Checking all servers for arbitrage opportunities..."))
            self.root.update_idletasks()
            
            # Get arbitrage opportunities
            world = self.world_var.get()
            if world == "All":
                messagebox.showinfo(get_text("app.select_world", "Select World"), get_text("app.select_world_info", "Please select a specific world to check for arbitrage opportunities."))
                return

            arbitrage = find_arbitrage_opportunities(
                item_id=self.current_item_id,
                current_world=world,
                data_center=data_center
            )
            
            # Display arbitrage info
            if arbitrage:
                message = f"{get_text('app.arbitrage', 'HOT ITEM! Arbitrage Opportunity!')} Buy from {arbitrage['lowest_price_world']}@{arbitrage['lowest_price_dc']} for {arbitrage['lowest_price']:,} gil and sell on {arbitrage['current_world']} for {arbitrage['current_price']:,} gil. Potential profit: {arbitrage['potential_profit']:,} gil ({arbitrage['profit_percentage']:.1f}%)."
                self.arbitrage_info_var.config( text = message)
            else:
                self.arbitrage_info_var.config( text = get_text("app.no_arbitrage", "No significant price differences found between worlds."))
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"{get_text('app.error_arbitrage', 'An error occurred while checking for arbitrage opportunities:')} {str(e)}")
            self.arbitrage_info_var.config( text = get_text("app.error_arbitrage", "Error checking arbitrage opportunities."))

    
    def on_set_alert(self):
        """
        Handle set alert button click.
        """
        try:
            # Check if an item is selected
            if not self.current_item_id or not self.current_item_name:
                messagebox.showwarning(get_text("app.no_item", "No Item Selected"), get_text("app.select_item", "Please select an item first."))
                return
            
            # Get the min and max price values
            min_price = self.min_price_var.get().strip()
            max_price = self.max_price_var.get().strip()
            
            # Validate that at least one price is set
            if not min_price and not max_price:
                messagebox.showwarning(get_text("app.no_price", "No Price Set"), get_text("app.set_price", "Please set at least one price threshold."))
                return
            
            # Get the world and data center
            world = self.world_var.get()
            data_center = self.dc_var.get() if world == "All" else None
            
            # Create the alert
            success = set_alert(
                item_id=self.current_item_id,
                item_name=self.current_item_name,
                min_price=min_price if min_price else None,
                max_price=max_price if max_price else None,
                world=world if world != "All" else None,
                data_center=data_center
            )
            
            if success:
                # Clear the input fields
                self.min_price_var.set("")
                self.max_price_var.set("")
                
                # Show success message
                messagebox.showinfo(get_text("app.alert_set", "Alert Set"), f"{get_text('app.alert_set_info', 'Price alert for')} {self.current_item_name} {get_text('app.alert_set_info2', 'has been set.').lower()}")
                
                # Refresh alerts for the current item
                self.display_alerts_for_current_item()
                self.display_all_alerts()
            else:
                messagebox.showerror(get_text("app.error", "Error"), get_text("app.error_alert", "Failed to set the alert. Please check your inputs."))
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"{get_text('app.error_alert', 'An error occurred while setting the alert:')} {str(e)}")

    def on_delete_all_alerts(self):
        """
        Handle delete alerts button click from all alerts tab
        """
        try:
            # Delete selected alert in all alerts tab
            selected_index = self.all_active_alerts_listbox.curselection()
            if not selected_index:
                messagebox.showwarning(get_text("app.no_alert", "No Alert Selected"), get_text("app.select_alert", "Please select an alert to delete."))
                return
            
            selection = selected_index[0]
            alert_uuid = self.all_alert_uuids[selection]
            delete_alert(self.current_item_id, 0, alert_uuid)
            self.display_all_alerts()
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"{get_text('app.error_delete', 'An error occurred while deleting the alert:')} {str(e)}")
            return
            

    def display_alerts_for_current_item(self):
        """
        Display alerts for the currently selected item.
        """
        if not self.current_item_id:
            return
            
        # Get alerts for the current item
        alerts = get_alerts_for_item(self.current_item_id)
        
        # Clear the listbox and alert indices
        self.active_alerts_listbox.delete(0, tk.END)
        self.alert_indices = {}
        
        # If no alerts, show a message
        if not alerts:
            self.active_alerts_listbox.insert(tk.END, get_text("app.no_alerts", "No active alerts for this item."))
            return
        
        # Add each alert to the listbox
        for i, alert in enumerate(alerts):
            # Format the alert display text
            alert_text = self.format_alert_text(alert)
            
            # Add to listbox
            self.active_alerts_listbox.insert(tk.END, alert_text)
            
            # Store the alert index
            self.alert_indices[i] = i

    def display_all_alerts(self):
        """
        Display all active alerts.
        """
        # get language from settings

        # Get all alerts
        all_alerts = load_alerts()
        
        # Clear the listbox and alert indices
        self.all_active_alerts_listbox.delete(0, tk.END)
        self.all_alert_indices = {}
        self.all_alert_uuids = {}
        
        # If no alerts, show a message
        if not all_alerts:
            self.all_active_alerts_listbox.insert(tk.END, get_text("app.no_alerts", "No active alerts."))
            return
        
        # Add each alert to the listbox
        counter = 0
        for i, item in enumerate(all_alerts):
            for j, alert in enumerate(all_alerts[item]):
                # Format the alert display text
                parts = []
                parts.append(f"Item: {alert['item_name']}")
                # Add min price if set
                if "min_price" in alert:
                    parts.append(f"Min: {alert['min_price']:,}")
                
                # Add max price if set
                if "max_price" in alert:
                    parts.append(f"Max: {alert['max_price']:,}")
                
                # Add location
                if "world" in alert:
                    parts.append(f"World: {alert['world']}")
                elif "data_center" in alert:
                    parts.append(f"DC: {alert['data_center']}")
                
                # Add created date
                if "created_at" in alert:
                    parts.append(f"Created: {alert['created_at']}")
                
                # Add active status
                if "active" in alert:
                    parts.append(f"Active: {'Yes' if alert['active'] else 'No'}")
                
                alert_text = " | ".join(parts)
                # Add to listbox
                self.all_active_alerts_listbox.insert(tk.END, alert_text)
                
                # Store the alert index
                self.all_alert_indices[counter] = i
                self.all_alert_uuids[counter] = alert["uuid"]
                counter +=1
                
    
    def format_alert_text(self, alert):
        """
        Format an alert for display in the listbox.
        
        Args:
            alert (dict): The alert data
            
        Returns:
            str: Formatted alert text
        """
        parts = []
        
        # Add min price if set
        if "min_price" in alert:
            parts.append(f"Min: {alert['min_price']:,}")
        
        # Add max price if set
        if "max_price" in alert:
            parts.append(f"Max: {alert['max_price']:,}")
        
        # Add location
        if "world" in alert:
            parts.append(f"World: {alert['world']}")
        elif "data_center" in alert:
            parts.append(f"DC: {alert['data_center']}")
        
        # Add created date
        if "created_at" in alert:
            parts.append(f"Created: {alert['created_at']}")
        
        return " | ".join(parts)
    
    def on_delete_alert(self):
        """
        Handle delete alert button click.
        """
        try:
            # Check if an item is selected
            if not self.current_item_id:
                messagebox.showwarning(get_text("app.no_item", "No Item Selected"), get_text("app.select_item", "Please select an item first."))
                return
                
            # Get the selected alert index
            selected_indices = self.active_alerts_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning(get_text("app.no_alert", "No Alert Selected"), get_text("app.select_alert", "Please select an alert to delete."))
                return
            
            # Get the alert index from the alert indices dictionary
            alert_index = self.alert_indices[selected_indices[0]]
            
            # Delete the alert
            success = delete_alert(self.current_item_id, alert_index)
            if success:
                # Show success message
                messagebox.showinfo(get_text("app.alert_deleted", "Alert Deleted"), get_text("app.alert_deleted_info", "The alert has been deleted."))
                
                # Refresh the alerts display
                self.display_alerts_for_current_item()
                self.display_all_alerts()
            else:
                messagebox.showerror(get_text("app.error", "Error"), get_text("app.error_delete", "Failed to delete the alert."))
        except Exception as e:
            messagebox.showerror(get_text("app.error", "Error"), f"{get_text('app.error_delete', 'An error occurred while deleting the alert:')} {str(e)}")

    def on_close(self):
        """
        Handle application close event to ensure proper cleanup.
        """
        # Stop the alerts monitor
        self.alerts_running = False

        # Close all matplotlib figures
        plt.close('all')
        
        # Destroy the root window
        self.root.destroy()
        
        # Force exit if needed
        self.root.quit()

    def open_discord_settings(self):
        """
        Open the Discord settings window.
        """
        discord_settings_window = tk.Toplevel(self.root)
        discord_settings_window.title(get_text("app.discord_settings", "Discord Settings"))
        discord_settings_window.geometry("500x150")
        discord_settings_window.resizable(False, False)
        
        # Create Discord settings form
        discord_webhook_label = create_label(discord_settings_window, "app.discord_webhook", "Discord Webhook URL:")
        discord_webhook_label.pack(padx=10, pady=(10, 5))
        
        discord_webhook_entry = tk.Entry(discord_settings_window, width=50)
        discord_webhook_entry.insert(0, load_discord_settings())
        discord_webhook_entry.pack(padx=10, pady=(0, 10))
        
        # Create help text
        help_text = ttk.Label(discord_settings_window, text=get_text("app.discord_webhook_help", "Enter your Discord webhook URL to receive alerts in Discord."), wraplength=480)
        help_text.pack(padx=10, pady=(0, 10))
        
        # Create buttons frame
        buttons_frame = ttk.Frame(discord_settings_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create test button
        test_button = create_button(buttons_frame, "app.test_discord", "Test", command=lambda: self.test_discord_webhook(discord_webhook_entry.get()))
        test_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create save button
        save_button = create_button(buttons_frame, "app.save", "Save", command=lambda: self.save_discord_webhook(discord_webhook_entry.get(), discord_settings_window))
        save_button.pack(side=tk.LEFT)

    def test_discord_webhook(self, webhook_url):
        """
        Test the Discord webhook.
        
        Args:
            webhook_url (str): The Discord webhook URL to test
        """
        if not webhook_url:
            messagebox.showwarning(get_text("app.missing_webhook", "Missing Webhook URL"), get_text("app.enter_webhook", "Please enter a webhook URL."))
            return
            
        # Temporarily save the webhook URL
        save_discord_settings(webhook_url)
        
        # Send a test message
        success = send_discord_alert(
            "PyFFUniverse - Test Alert",
            get_text("app.discord_test_message", "This is a test alert from PyFFUniverse."),
            color=0x00FF00  # Green color
        )
        
        if success:
            messagebox.showinfo(get_text("app.test_success", "Test Successful"), get_text("app.discord_test_success", "Test message sent successfully to Discord."))
        else:
            messagebox.showerror(get_text("app.test_failed", "Test Failed"), get_text("app.discord_test_failed", "Failed to send test message to Discord. Please check your webhook URL."))

    def save_discord_webhook(self, webhook_url, window=None):
        """
        Save the Discord webhook URL.
        
        Args:
            webhook_url (str): The Discord webhook URL
            window (Toplevel, optional): The window to close after saving
        """
        # Save the webhook URL
        save_discord_settings(webhook_url)
        
        # Show success message
        messagebox.showinfo(get_text("app.settings_saved", "Settings Saved"), get_text("app.discord_settings_saved", "Discord webhook settings have been saved."))
        
        # Close the window if provided
        if window:
            window.destroy()

import platform

if check_os() not in ["Linux","macOS"]:
    version_info = platform.version()
    major_version = int(version_info.split('.')[0])

    if major_version == 10:
        class MyToastNotifier(ToastNotifier):
            def __init__(self):
                super().__init__()

            def on_destroy(self, hwnd, msg, wparam, lparam):
                super().on_destroy(hwnd, msg, wparam, lparam)
                return 0
    elif major_version == 11:
        class MyToastNotifier(ToastNotifier11):
            def __init__(self):
                super().__init__()

            def on_destroy(self, hwnd, msg, wparam, lparam):
                super().on_destroy(hwnd, msg, wparam, lparam)
                return 0
    else:
        class MyToastNotifier():
            def __init__(self):
                pass
            
            def show_toast(self, title, message, duration=10, app_name="PyFFUniverse", toast_icon=None, toast_duration="short", toast_duration_type="short"):
                messagebox.showinfo(title, message)
else:
    class MyToastNotifier():
        def __init__(self):
            pass
        
        def show_toast(self, title, message, duration=10, app_name="PyFFUniverse", toast_icon=None, toast_duration="short", toast_duration_type="short"):
            messagebox.showinfo(title, message)