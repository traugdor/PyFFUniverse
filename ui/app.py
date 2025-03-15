import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import datetime
import threading

# Import from our modules
from utils.settings import load_settings, save_settings
from utils.alerts import set_alert, get_alerts_for_item, delete_alert
from utils.market_analysis import find_arbitrage_opportunities, is_hot_item
from api.universalis import get_marketable_items, get_market_data, get_data_centers, format_listing
from api.xivapi import get_item_details
from utils.data_processing import create_item_dictionary, filter_items_by_search
from ui.item_frame import create_item_frame
from ui.market_frame import create_market_frame

class PyFFUniverseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyFFUniverse")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Start maximized
        
        # Load settings
        self.settings = load_settings()
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left panel for item list and search
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Create search frame
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add search label and entry
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="Search", command=self.on_search).pack(side=tk.RIGHT)
        
        # Create item listbox with scrollbar
        item_frame = ttk.Frame(left_panel)
        item_frame.pack(fill=tk.BOTH, expand=True)
        
        self.item_listbox = tk.Listbox(item_frame, width=40, height=30)
        self.item_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.item_listbox.bind('<<ListboxSelect>>', self.on_item_select)
        
        scrollbar = ttk.Scrollbar(item_frame, orient=tk.VERTICAL, command=self.item_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_listbox.config(yscrollcommand=scrollbar.set)
        
        # Create right panel for item details and market data
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create settings frame at the top
        settings_frame = ttk.Frame(right_panel)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language dropdown
        ttk.Label(settings_frame, text="Language:").pack(side=tk.LEFT, padx=(0, 5))
        languages = ["English", "Deutsch", "日本語", "Français"]
        self.language_var = tk.StringVar(value=self.settings["language"])
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, values=languages, state="readonly", width=10)
        language_combo.pack(side=tk.LEFT, padx=(0, 10))
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Data center dropdown
        ttk.Label(settings_frame, text="Data Center:").pack(side=tk.LEFT, padx=(0, 5))
        data_centers = ["Aether", "Primal", "Crystal", "Dynamis"]
        self.dc_var = tk.StringVar(value=self.settings["data_center"])
        dc_combo = ttk.Combobox(settings_frame, textvariable=self.dc_var, values=data_centers, state="readonly", width=15)
        dc_combo.pack(side=tk.LEFT, padx=(0, 10))
        dc_combo.bind("<<ComboboxSelected>>", self.on_dc_change)
        
        # World dropdown
        ttk.Label(settings_frame, text="World:").pack(side=tk.LEFT, padx=(0, 5))
        self.world_var = tk.StringVar(value=self.settings["world"])
        self.world_combo = ttk.Combobox(settings_frame, textvariable=self.world_var, state="readonly", width=15)
        self.world_combo.pack(side=tk.LEFT)
        self.world_combo.bind("<<ComboboxSelected>>", self.on_world_change)
        
        # Create item details frame
        self.item_frame = create_item_frame(right_panel)
        
        # Create notebook for market data tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create market data tabs
        self.market_frame = create_market_frame(self.notebook)
        
        # Initialize variables for item details
        self.item_name_var = self.item_frame["name_var"]
        self.item_desc_html = self.item_frame["desc_html"]
        
        # Initialize variables for market data
        self.listings_listbox = self.market_frame["listings_listbox"]
        self.min_price_var = self.market_frame["min_price_var"]
        self.max_price_var = self.market_frame["max_price_var"]
        self.set_alert_button = self.market_frame["set_alert_button"]
        self.active_alerts_listbox = self.market_frame["active_alerts_listbox"]
        self.delete_alert_button = self.market_frame["delete_alert_button"]
        
        # Initialize variables for hot item and arbitrage
        self.hot_item_var = self.item_frame["hot_item_var"]
        self.arbitrage_info_var = self.item_frame["arbitrage_info_var"]
        self.check_arbitrage_button = self.item_frame["check_arbitrage_button"]
        
        # Configure the set alert button
        self.set_alert_button.config(command=self.on_set_alert)
        
        # Configure the delete alert button
        self.delete_alert_button.config(command=self.on_delete_alert)
        
        # Configure the check arbitrage button
        self.check_arbitrage_button.config(command=self.on_check_arbitrage)
        
        # Variable to track the currently selected item
        self.current_item_id = None
        self.current_item_name = None
        
        # Dictionary to track alert indices
        self.alert_indices = {}
        
        # Load data
        self.load_data()
        
    def load_data(self):
        try:
            # Show loading screen
            self.show_loading_screen("Loading item data...")
            
            # Get marketable items directly from Universalis
            self.update_loading_progress(20, "Fetching marketable items from Universalis...")
            
            # Use the Universalis marketable endpoint
            marketable_ids = get_marketable_items()
            self.update_loading_progress(40, "Fetching item details...", f"Found {len(marketable_ids)} marketable items")
            
            # Process item data
            self.update_loading_progress(60, "Processing item data...")
            
            # Create item dictionary and printable items list
            global itemDictionary, printableItems
            itemDictionary, printableItems = create_item_dictionary(marketable_ids)
            
            # Update item list
            self.update_item_list(printableItems)
            
            # Initialize the world dropdown based on the saved data center
            self.initialize_world_dropdown()
            
            self.update_loading_progress(100, "Item data loaded successfully", f"Loaded {len(itemDictionary)} items")
            
            # Hide loading screen
            self.hide_loading_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
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
        self.loading_window.title("Loading")
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
        self.loading_details = tk.Label(self.loading_window, text="Initializing...")
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
    
    def on_search(self):
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
            # Save the language setting
            self.settings["language"] = self.language_var.get()
            save_settings(self.settings)
            
            # Refresh the item details if an item is selected
            selected_indices = self.item_listbox.curselection()
            if selected_indices:
                self.on_item_select(None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save language setting: {e}")
    
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
            messagebox.showerror("Error", f"Failed to load data center information: {e}")
    
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
            messagebox.showerror("Error", f"Failed to save world setting: {e}")
    
    def on_item_select(self, event):
        """
        Handle item selection from the search results.
        
        Args:
            event: The event object
        """
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
                    description = f"<p>{item_details['Name_en']}</p>"
                    
                    # Add item description if available
                    if "Description_en" in item_details:
                        description += f"<p>{item_details['Description_en']}</p>"
                    
                    # Update the item description
                    self.item_desc_html.set_html(description)
                    
                    # Update the current item ID and name
                    self.current_item_id = item_id
                    self.current_item_name = selected_item
                    
                    # Display alerts for the selected item
                    self.display_alerts_for_current_item()
                    
                    # Reset hot item and arbitrage indicators
                    self.hot_item_var.set("")
                    self.arbitrage_info_var.set("")
                    
                    # Fetch market data in a separate thread to avoid freezing the UI
                    self.fetch_market_data(item_id, market_location)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load item details: {e}")
    
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
            # Add header
            self.listings_listbox.insert(tk.END, f"{'Price':^10} | {'Qty':^6} | {'Total':^10} | {'World':^10} | {'Last Updated':^20}")
            self.listings_listbox.insert(tk.END, "-" * 65)
            
            # Add each listing
            for listing in market_response["listings"]:
                listing_text = format_listing(listing, market_location)
                self.listings_listbox.insert(tk.END, listing_text)
                
            # Update market statistics
            self.update_market_statistics(market_response)
        else:
            self.listings_listbox.insert(tk.END, "No listings found for this item.")
            
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
                self.hot_item_var.set("HOT ITEM! This item sells frequently.")
            else:
                self.hot_item_var.set("")
            
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
        self.hot_item_var.set("")
        self.arbitrage_info_var.set("")
    
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
                    message = f"HOT ITEM! Arbitrage Opportunity! Buy from {arbitrage['lowest_price_world']} for {arbitrage['lowest_price']:,} gil and sell on {arbitrage['current_world']} for {arbitrage['current_price']:,} gil. Potential profit: {arbitrage['potential_profit']:,} gil ({arbitrage['profit_percentage']:.1f}%)."
                    self.arbitrage_info_var.set(message)
                else:
                    self.arbitrage_info_var.set("No significant price differences found between worlds.")
            else:
                self.arbitrage_info_var.set("Select 'All' worlds in a specific data center to check for arbitrage opportunities.")
        except Exception as e:
            print(f"Error checking arbitrage opportunities: {e}")
            self.arbitrage_info_var.set(f"Error checking arbitrage: {str(e)}")
    
    def show_market_error(self, error_message):
        """
        Show an error message in the listings listbox.
        
        Args:
            error_message (str): The error message to display
        """
        self.listings_listbox.delete(0, tk.END)
        self.listings_listbox.insert(tk.END, f"Error fetching market data: {error_message}")
        
        # Clear market statistics when there's an error
        self.clear_market_statistics()
    
    def on_check_arbitrage(self):
        """
        Handle check arbitrage button click.
        """
        try:
            # Check if an item is selected
            if not self.current_item_id:
                messagebox.showwarning("No Item Selected", "Please select an item first.")
                return
            
            # Get the current data center
            data_center = self.dc_var.get()
            if data_center == "All":
                messagebox.showinfo("Select Data Center", "Please select a specific data center to check for arbitrage opportunities.")
                return
            
            # Show loading message
            self.arbitrage_info_var.set("Checking all servers for arbitrage opportunities...")
            self.root.update_idletasks()
            
            # Get arbitrage opportunities
            arbitrage = find_arbitrage_opportunities(
                item_id=self.current_item_id,
                current_world=None,  # We'll analyze all worlds
                data_center=data_center
            )
            
            # Display arbitrage info
            if arbitrage:
                message = f"HOT ITEM! Arbitrage Opportunity! Buy from {arbitrage['lowest_price_world']} for {arbitrage['lowest_price']:,} gil and sell on {arbitrage['current_world']} for {arbitrage['current_price']:,} gil. Potential profit: {arbitrage['potential_profit']:,} gil ({arbitrage['profit_percentage']:.1f}%)."
                self.arbitrage_info_var.set(message)
            else:
                self.arbitrage_info_var.set("No significant price differences found between worlds.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while checking for arbitrage opportunities: {str(e)}")
            self.arbitrage_info_var.set("Error checking arbitrage opportunities.")
    
    def on_set_alert(self):
        """
        Handle set alert button click.
        """
        try:
            # Check if an item is selected
            if not self.current_item_id or not self.current_item_name:
                messagebox.showwarning("No Item Selected", "Please select an item first.")
                return
            
            # Get the min and max price values
            min_price = self.min_price_var.get().strip()
            max_price = self.max_price_var.get().strip()
            
            # Validate that at least one price is set
            if not min_price and not max_price:
                messagebox.showwarning("No Price Set", "Please set at least one price threshold.")
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
                messagebox.showinfo("Alert Set", f"Price alert for {self.current_item_name} has been set.")
                
                # Refresh alerts for the current item
                self.display_alerts_for_current_item()
            else:
                messagebox.showerror("Error", "Failed to set the alert. Please check your inputs.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while setting the alert: {str(e)}")
    
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
            self.active_alerts_listbox.insert(tk.END, "No active alerts for this item.")
            return
        
        # Add each alert to the listbox
        for i, alert in enumerate(alerts):
            # Format the alert display text
            alert_text = self.format_alert_text(alert)
            
            # Add to listbox
            self.active_alerts_listbox.insert(tk.END, alert_text)
            
            # Store the alert index
            self.alert_indices[i] = i
    
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
                messagebox.showwarning("No Item Selected", "Please select an item first.")
                return
                
            # Get the selected alert index
            selected_indices = self.active_alerts_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Alert Selected", "Please select an alert to delete.")
                return
            
            # Get the alert index from the alert indices dictionary
            alert_index = self.alert_indices[selected_indices[0]]
            
            # Delete the alert
            success = delete_alert(self.current_item_id, alert_index)
            if success:
                # Show success message
                messagebox.showinfo("Alert Deleted", "The alert has been deleted.")
                
                # Refresh the alerts display
                self.display_alerts_for_current_item()
            else:
                messagebox.showerror("Error", "Failed to delete the alert.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting the alert: {str(e)}")
