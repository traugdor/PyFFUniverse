import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import time
import datetime
import asyncio
import aiohttp
import threading
import os

# Settings file path
SETTINGS_FILE = "pyffu_settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "language": "English",
    "data_center": "Aether",
    "world": "All"
}

# Function to load settings
def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

# Function to save settings
def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

XIVAPIBaseURL = "https://xivapi.com/item/"
DCURL = "https://xivapi.com/servers/dc"

UbaseUrl = "https://universalis.app/api/v2/"
dataCentersU = "data-centers"
worldsU = "worlds"
marketableU = "marketable"

marketableItems = []
itemDictionary = []
printableItems = []
allItemsResponse = {}
itemDB = json.loads('[]')

# Custom print function to replace sg.Print
def custom_print(text):
    if hasattr(custom_print, 'window'):
        custom_print.window.insert(tk.END, str(text) + "\n")
        custom_print.window.see(tk.END)
        custom_print.window.update()  # Force update the text widget
    else:
        print(text)

def open_about():
    about_window = tk.Toplevel()
    about_window.title("PyFFUniverse")
    about_window.grab_set()  # Make it modal
    
    about_text = "This software is copyright 2025 traugdor. All rights are reserved. No portion of this software may be reproduced or copied without express written permission by the author. All data displayed in this software is subject to change without notice. The author of this software bears no responsiblity for the accuracy of the data contained therein. This software is to be used for educational purposes only. If you have enjoyed the use of this software, and would like to donate, please feel free to send donations to Cetiri Mjeseca on Aether-Jenova."
    
    about_label = tk.Label(about_window, text="About PyFFUniverse", font=("Arial", 12, "bold"))
    about_label.pack(pady=10)
    
    text_widget = tk.Text(about_window, wrap=tk.WORD, width=50, height=15)
    text_widget.insert(tk.END, about_text)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(padx=10, pady=10)
    
    exit_button = tk.Button(about_window, text="Exit", command=about_window.destroy)
    exit_button.pack(pady=10)

def switchLanguage(app, Lang):
    global marketableItems
    global itemDictionary
    global printableItems
    global allItemsResponse
    
    if Lang == "English":
        app.lbl_lang.config(text="Language")
        app.lbl_dc.config(text="Data Center")
        app.lbl_world.config(text="World")
        app.lbl_item_list.config(text="List of Items")
        app.btn_search.config(text="Search")
        app.lbl_item_name.config(text="Item Name:")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["en"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        app.update_item_list(printableItems)
        
    elif Lang == "Deutsch":
        app.lbl_lang.config(text="Sprache")
        app.lbl_dc.config(text="Rechenzentrum")
        app.lbl_world.config(text="Welt")
        app.lbl_item_list.config(text="Artikelliste")
        app.btn_search.config(text="Suche")
        app.lbl_item_name.config(text="Artikelname:")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["de"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        app.update_item_list(printableItems)
        
    elif Lang == "日本語":
        app.lbl_lang.config(text="言語")
        app.lbl_dc.config(text="データセンター")
        app.lbl_world.config(text="世界")
        app.lbl_item_list.config(text="詳細")
        app.btn_search.config(text="検索")
        app.lbl_item_name.config(text="項目名:")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["ja"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        app.update_item_list(printableItems)
        
    elif Lang == "Français":
        app.lbl_lang.config(text="Langue")
        app.lbl_dc.config(text="Centre de données")
        app.lbl_world.config(text="Monde")
        app.lbl_item_list.config(text="Liste des articles")
        app.btn_search.config(text="Rechercher")
        app.lbl_item_name.config(text="Nom de l'article:")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["fr"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        app.update_item_list(printableItems)

def filter_by_template_object(json_obj, template_obj):
    """
    Filter a JSON object to match the structure of a template object
    """
    if isinstance(template_obj, dict):
        if not isinstance(json_obj, dict):
            return {}
        return {k: filter_by_template_object(json_obj.get(k), v) 
                for k, v in template_obj.items() 
                if k in json_obj}
    elif isinstance(template_obj, list) and template_obj and json_obj:
        if not isinstance(json_obj, list):
            return []
        template_item = template_obj[0]  # Use the first item as template
        return [filter_by_template_object(item, template_item) for item in json_obj]
    else:
        # For primitive values, return the actual value from json_obj
        return json_obj

async def fetch_item_data_async(session, item_id, data_center, template):
    """Asynchronously fetch data for a single item"""
    url = f"{UbaseUrl}{data_center}/{item_id}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                # Filter the data if template is provided
                if template:
                    return filter_by_template_object(data, template)
                return data
            else:
                return {"error": f"HTTP {response.status}", "itemID": item_id}
    except Exception as e:
        return {"error": str(e), "itemID": item_id}

def run_async_in_thread(async_func, *args):
    """Run an async function in a separate thread and return its result"""
    result_container = []
    
    async def wrapper():
        result = await async_func(*args)
        result_container.append(result)
    
    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the async function and close the loop
    try:
        loop.run_until_complete(wrapper())
    finally:
        loop.close()
    
    # Return the result if available
    return result_container[0] if result_container else None

async def process_items_batch(items, data_center, template, batch_size=50, max_rate=20):
    """Process a batch of items asynchronously with rate limiting"""
    results = []
    # Limit to 8 concurrent connections as per Universalis API limits
    max_connections = 8  # Universalis allows max 8 simultaneous connections per IP
    semaphore = asyncio.Semaphore(max_connections)
    
    # For rate limiting (25 req/s)
    min_delay = 1.0 / max_rate  # Minimum delay between requests to respect rate limit
    
    async def fetch_with_rate_limit(session, item_id):
        async with semaphore:  # This limits the number of concurrent requests
            result = await fetch_item_data_async(session, item_id, data_center, template)
            # Add a small delay to respect rate limits
            await asyncio.sleep(min_delay)
            return result
    
    # Create a ClientSession that will be used for all requests
    async with aiohttp.ClientSession() as session:
        # Create tasks for all items in the batch
        tasks = [fetch_with_rate_limit(session, item) for item in items]
        # Execute all tasks concurrently and gather results
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
    
    return results

def gatherMarketInfo(dataCenter):
    # This function is now simplified to just load the item dictionary
    # We no longer need to gather all market data at startup
    global itemDictionary
    global printableItems
    
    # Create debug window for output
    debug_window = tk.Toplevel()
    debug_window.title("Loading Item Data")
    debug_window.geometry("600x400")
    
    # Add a frame for the progress information
    info_frame = tk.Frame(debug_window)
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Status label
    status_var = tk.StringVar(value="Initializing...")
    status_label = tk.Label(info_frame, textvariable=status_var, anchor="w")
    status_label.pack(fill=tk.X, pady=5)
    
    # Progress bar
    progress_frame = tk.Frame(debug_window)
    progress_frame.pack(fill=tk.X, padx=10, pady=5)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, pady=5)
    
    # Progress details
    details_var = tk.StringVar(value="Preparing to load data...")
    details_label = tk.Label(progress_frame, textvariable=details_var, anchor="w")
    details_label.pack(fill=tk.X, pady=5)
    
    # Log text area
    debug_text = scrolledtext.ScrolledText(debug_window, width=70, height=15)
    debug_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    custom_print.window = debug_text
    
    # Create a separate frame for the close button
    button_frame = tk.Frame(debug_window)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Close button in its own frame
    close_button = tk.Button(button_frame, text="Close", command=debug_window.destroy, width=10, height=1)
    close_button.pack(side=tk.BOTTOM)
    
    # Function to update UI
    def update_progress(percent, status_text, details_text=None):
        progress_var.set(percent)
        status_var.set(status_text)
        if details_text:
            details_var.set(details_text)
        debug_window.update()  # Force window update
    
    # Start the data loading process
    custom_print("Loading item data...")
    update_progress(0, "Loading item data...")
    
    try:
        # Get item data from XIVAPI
        update_progress(20, "Fetching item data from XIVAPI...")
        custom_print("Fetching item data from XIVAPI...")
        
        url = "https://xivapi.com/search?indexes=Item&filters=ItemSearchCategory.ID>=1&columns=ID,Name,Icon,ItemSearchCategory.Name,ItemSearchCategory.ID&limit=3000"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Process item data
            update_progress(60, "Processing item data...", f"Found {len(data['Results'])} items")
            custom_print(f"Found {len(data['Results'])} items")
            
            itemDictionary = []
            for item in data["Results"]:
                itemDictionary.append((item["ID"], item["Name"]))
            
            # Sort items alphabetically
            itemDictionary.sort(key=lambda x: x[1])
            printableItems = itemDictionary
            
            update_progress(100, "Item data loaded successfully", f"Loaded {len(itemDictionary)} items")
            custom_print(f"Item data loaded successfully. {len(itemDictionary)} items available.")
        else:
            update_progress(100, "Error fetching item data", f"HTTP Status: {response.status_code}")
            custom_print(f"Error fetching item data: HTTP Status {response.status_code}")
    except Exception as e:
        update_progress(100, "Error loading item data", str(e))
        custom_print(f"Error loading item data: {e}")
    
    # Return the item dictionary
    return itemDictionary

class PyFFUniverseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyFFUniverse")
        self.root.geometry("1200x700")
        self.root.state('zoomed')  # Start maximized
        
        # Create menu
        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)
        
        # Load user settings
        self.settings = load_settings()
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # Main title and about button
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = tk.Label(title_frame, text="PyFFUniverse", font=("Arial", 14))
        title_label.pack(side=tk.LEFT, expand=True)
        
        about_button = tk.Button(title_frame, text="About", command=open_about)
        about_button.pack(side=tk.RIGHT)
        
        # Application options frame
        options_frame = tk.Frame(self.root)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Language selection
        self.lbl_lang = tk.Label(options_frame, text="Language")
        self.lbl_lang.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.language_var = tk.StringVar(value=self.settings["language"])  # Use saved setting
        self.language_combo = ttk.Combobox(options_frame, textvariable=self.language_var, 
                                         values=["English", "Deutsch", "日本語", "Français"])
        self.language_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Data Center selection
        self.lbl_dc = tk.Label(options_frame, text="Data Center")
        self.lbl_dc.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.dc_var = tk.StringVar(value=self.settings["data_center"])  # Use saved setting
        self.dc_combo = ttk.Combobox(options_frame, textvariable=self.dc_var, 
                                   values=["Aether", "Primal", "Crystal", "Dynamis"])
        self.dc_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.dc_combo.bind("<<ComboboxSelected>>", self.on_dc_change)
        
        # World selection
        self.lbl_world = tk.Label(options_frame, text="World")
        self.lbl_world.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.world_var = tk.StringVar(value=self.settings["world"])  # Use saved setting
        self.world_combo = ttk.Combobox(options_frame, textvariable=self.world_var)
        self.world_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.world_combo.bind("<<ComboboxSelected>>", self.on_world_change)
        
        # Main content frame
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Item list column
        item_list_frame = tk.Frame(content_frame)
        item_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Search area
        search_frame = tk.Frame(item_list_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lbl_item_list = tk.Label(search_frame, text="List of Items")
        self.lbl_item_list.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_search = tk.Button(search_frame, text="Search", command=self.on_search)
        self.btn_search.pack(side=tk.LEFT, padx=5)
        
        # Item listbox
        self.item_listbox = tk.Listbox(item_list_frame, width=40, height=20)
        self.item_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.item_listbox.bind("<<ListboxSelect>>", self.on_item_select)
        
        # Add scrollbar to listbox
        listbox_scrollbar = tk.Scrollbar(self.item_listbox)
        self.item_listbox.config(yscrollcommand=listbox_scrollbar.set)
        listbox_scrollbar.config(command=self.item_listbox.yview)
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Separator
        separator = ttk.Separator(content_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Item details column
        details_frame = tk.Frame(content_frame)
        details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Item name
        name_frame = tk.Frame(details_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lbl_item_name = tk.Label(name_frame, text="Item Name:")
        self.lbl_item_name.pack(side=tk.LEFT, padx=5)
        
        self.item_name_var = tk.StringVar()
        self.item_name_label = tk.Label(name_frame, textvariable=self.item_name_var, width=20)
        self.item_name_label.pack(side=tk.LEFT, padx=5)
        
        # Item description
        desc_label_frame = tk.Frame(details_frame)
        desc_label_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lbl_item_desc = tk.Label(desc_label_frame, text="Item Description:")
        self.lbl_item_desc.pack(side=tk.LEFT, padx=5)
        
        # Description text area
        self.item_desc_text = tk.Text(details_frame, wrap=tk.WORD, width=40, height=5)
        self.item_desc_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Item listings
        listings_label_frame = tk.Frame(details_frame)
        listings_label_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lbl_item_listings = tk.Label(listings_label_frame, text="Item Listings:")
        self.lbl_item_listings.pack(side=tk.LEFT, padx=5)
        
        # Listings listbox
        self.listings_listbox = tk.Listbox(details_frame, width=40, height=10)
        self.listings_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to listings listbox
        listings_scrollbar = tk.Scrollbar(self.listings_listbox)
        self.listings_listbox.config(yscrollcommand=listings_scrollbar.set)
        listings_scrollbar.config(command=self.listings_listbox.yview)
        listings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add another separator
        separator2 = ttk.Separator(content_frame, orient=tk.VERTICAL)
        separator2.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Market analysis section
        analysis_frame = tk.Frame(content_frame)
        analysis_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a notebook with tabs
        self.analysis_notebook = ttk.Notebook(analysis_frame)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Watched Listings
        self.watched_tab = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.watched_tab, text="Watched Listings")
        self.setup_watched_listings_tab()
        
        # Tab 2: Price History
        self.price_history_tab = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.price_history_tab, text="Price History")
        self.setup_price_history_tab()
        
        # Tab 3: Sale History
        self.sale_history_tab = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.sale_history_tab, text="Sale History")
        self.setup_sale_history_tab()
    
    def setup_watched_listings_tab(self):
        watched_frame = tk.Frame(self.watched_tab)
        watched_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and description
        title_label = tk.Label(watched_frame, text="Watched Listings", font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 10))
        
        description_label = tk.Label(watched_frame, text="Set price alerts for up to 8 items. You'll be notified when prices reach your target.")
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Create a frame for the watched items with grid layout
        items_frame = tk.Frame(watched_frame)
        items_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns to maintain consistent widths
        items_frame.columnconfigure(0, weight=2)  # Item name column (wider)
        items_frame.columnconfigure(1, weight=1)  # Current price
        items_frame.columnconfigure(2, weight=1)  # Min price
        items_frame.columnconfigure(3, weight=1)  # Max price
        items_frame.columnconfigure(4, weight=1)  # Alert type
        items_frame.columnconfigure(5, weight=1)  # Actions
        
        # Headers
        tk.Label(items_frame, text="Item", width=20, anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(items_frame, text="Current Price", width=12, anchor="w").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        tk.Label(items_frame, text="Min Price", width=12, anchor="w").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        tk.Label(items_frame, text="Max Price", width=12, anchor="w").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        tk.Label(items_frame, text="Alert Type", width=12, anchor="w").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        tk.Label(items_frame, text="Actions", width=15, anchor="w").grid(row=0, column=5, padx=5, pady=5, sticky="w")
        
        # Separator line
        separator = ttk.Separator(items_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=6, sticky="ew", pady=2)
        
        # Create 8 rows for watched items
        self.watched_items_rows = []
        for i in range(8):
            row_index = i + 2  # Start from row 2 (after headers and separator)
            
            # Item name (read-only)
            item_name = tk.StringVar()
            item_name_entry = tk.Entry(items_frame, textvariable=item_name, width=20, state="readonly")
            item_name_entry.grid(row=row_index, column=0, padx=5, pady=2, sticky="ew")
            
            # Current price (read-only)
            current_price = tk.StringVar()
            current_price_entry = tk.Entry(items_frame, textvariable=current_price, width=12, state="readonly")
            current_price_entry.grid(row=row_index, column=1, padx=5, pady=2, sticky="ew")
            
            # Min price (editable)
            min_price = tk.StringVar()
            min_price_entry = tk.Entry(items_frame, textvariable=min_price, width=12)
            min_price_entry.grid(row=row_index, column=2, padx=5, pady=2, sticky="ew")
            
            # Max price (editable)
            max_price = tk.StringVar()
            max_price_entry = tk.Entry(items_frame, textvariable=max_price, width=12)
            max_price_entry.grid(row=row_index, column=3, padx=5, pady=2, sticky="ew")
            
            # Alert type dropdown
            alert_type = tk.StringVar()
            alert_type_combo = ttk.Combobox(items_frame, textvariable=alert_type, width=10,
                                         values=["Both", "Min Only", "Max Only", "Change %"], state="readonly")
            alert_type_combo.grid(row=row_index, column=4, padx=5, pady=2, sticky="ew")
            
            # Action buttons
            actions_frame = tk.Frame(items_frame)
            actions_frame.grid(row=row_index, column=5, padx=5, pady=2, sticky="w")
            
            add_btn = tk.Button(actions_frame, text="Add", width=5)
            add_btn.pack(side=tk.LEFT, padx=2)
            
            remove_btn = tk.Button(actions_frame, text="Remove", width=7)
            remove_btn.pack(side=tk.LEFT, padx=2)
            
            # Store references to all widgets in this row
            self.watched_items_rows.append({
                "item_name": item_name,
                "current_price": current_price,
                "min_price": min_price,
                "max_price": max_price,
                "alert_type": alert_type,
                "add_btn": add_btn,
                "remove_btn": remove_btn
            })
        
        # Bottom controls
        controls_frame = tk.Frame(watched_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        save_btn = tk.Button(controls_frame, text="Save Alerts")
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_all_btn = tk.Button(controls_frame, text="Clear All")
        clear_all_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_price_history_tab(self):
        price_history_frame = tk.Frame(self.price_history_tab)
        price_history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and description
        title_label = tk.Label(price_history_frame, text="Price History", font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 10))
        
        description_label = tk.Label(price_history_frame, text="View historical price trends and predictions for this item.")
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Controls frame (left side)
        controls_frame = tk.Frame(price_history_frame)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Time range selection
        time_frame = tk.LabelFrame(controls_frame, text="Time Range")
        time_frame.pack(fill=tk.X, pady=5)
        
        time_ranges = ["24 Hours", "7 Days", "30 Days", "90 Days", "All Time"]
        self.time_range_var = tk.StringVar(value=time_ranges[1])  # Default to 7 Days
        
        for i, range_text in enumerate(time_ranges):
            tk.Radiobutton(time_frame, text=range_text, variable=self.time_range_var, 
                          value=range_text).pack(anchor="w", padx=10, pady=2)
        
        # Chart options
        options_frame = tk.LabelFrame(controls_frame, text="Chart Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        # Checkboxes for chart options
        self.show_peaks_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Show Peaks/Valleys", 
                      variable=self.show_peaks_var).pack(anchor="w", padx=10, pady=2)
        
        self.show_trend_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Show Trend Line", 
                      variable=self.show_trend_var).pack(anchor="w", padx=10, pady=2)
        
        self.show_avg_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Show Average Price", 
                      variable=self.show_avg_var).pack(anchor="w", padx=10, pady=2)
        
        # Prediction options
        prediction_frame = tk.LabelFrame(controls_frame, text="Price Prediction")
        prediction_frame.pack(fill=tk.X, pady=10)
        
        # Prediction method
        method_label = tk.Label(prediction_frame, text="Method:")
        method_label.pack(anchor="w", padx=10, pady=2)
        
        prediction_methods = ["Simple Trend", "Moving Average", "Advanced (ARIMA)"]
        self.prediction_method_var = tk.StringVar(value=prediction_methods[0])
        method_combo = ttk.Combobox(prediction_frame, textvariable=self.prediction_method_var, 
                                  values=prediction_methods, state="readonly", width=15)
        method_combo.pack(anchor="w", padx=10, pady=2)
        
        # Prediction timeframe
        timeframe_label = tk.Label(prediction_frame, text="Predict Next:")
        timeframe_label.pack(anchor="w", padx=10, pady=2)
        
        prediction_times = ["24 Hours", "3 Days", "7 Days", "14 Days"]
        self.prediction_time_var = tk.StringVar(value=prediction_times[1])
        time_combo = ttk.Combobox(prediction_frame, textvariable=self.prediction_time_var, 
                               values=prediction_times, state="readonly", width=15)
        time_combo.pack(anchor="w", padx=10, pady=2)
        
        # Update button
        update_btn = tk.Button(controls_frame, text="Update Chart")
        update_btn.pack(pady=15)
        
        # Chart placeholder (right side)
        chart_frame = tk.Frame(price_history_frame, bg="#f0f0f0", width=400, height=300)
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Placeholder text for chart area
        chart_placeholder = tk.Label(chart_frame, text="Price History Chart\nWill Appear Here", 
                                  font=("Arial", 12), bg="#f0f0f0")
        chart_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        # Price prediction results frame (below chart)
        prediction_results_frame = tk.Frame(price_history_frame)
        prediction_results_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        prediction_title = tk.Label(prediction_results_frame, text="Price Prediction Results", 
                                  font=("Arial", 10, "bold"))
        prediction_title.pack(anchor="w")
        
        # Prediction results in a simple format
        self.prediction_result_var = tk.StringVar(value="Select an item and click 'Update Chart' to see price predictions")
        prediction_result = tk.Label(prediction_results_frame, textvariable=self.prediction_result_var, 
                                  justify=tk.LEFT, wraplength=600)
        prediction_result.pack(anchor="w", pady=5)
    
    def setup_sale_history_tab(self):
        sale_history_frame = tk.Frame(self.sale_history_tab)
        sale_history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and description
        title_label = tk.Label(sale_history_frame, text="Sale History", font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 10))
        
        description_label = tk.Label(sale_history_frame, text="Track sales volume and set alerts for optimal selling times.")
        description_label.pack(anchor="w", pady=(0, 15))
        
        # Main content frame with left and right sections
        content_frame = tk.Frame(sale_history_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Controls
        controls_frame = tk.Frame(content_frame)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Time period selection
        time_frame = tk.LabelFrame(controls_frame, text="Time Period")
        time_frame.pack(fill=tk.X, pady=5)
        
        time_periods = ["Last Week", "Last Month", "Last 3 Months"]
        self.sale_time_var = tk.StringVar(value=time_periods[0])
        
        for period in time_periods:
            tk.Radiobutton(time_frame, text=period, variable=self.sale_time_var, 
                          value=period).pack(anchor="w", padx=10, pady=2)
        
        # Display options
        display_frame = tk.LabelFrame(controls_frame, text="Display Options")
        display_frame.pack(fill=tk.X, pady=10)
        
        self.show_daily_var = tk.BooleanVar(value=True)
        tk.Checkbutton(display_frame, text="Show Daily Sales", 
                      variable=self.show_daily_var).pack(anchor="w", padx=10, pady=2)
        
        self.show_weekly_var = tk.BooleanVar(value=False)
        tk.Checkbutton(display_frame, text="Show Weekly Pattern", 
                      variable=self.show_weekly_var).pack(anchor="w", padx=10, pady=2)
        
        self.show_volume_var = tk.BooleanVar(value=True)
        tk.Checkbutton(display_frame, text="Show Volume", 
                      variable=self.show_volume_var).pack(anchor="w", padx=10, pady=2)
        
        # Sale alerts
        alerts_frame = tk.LabelFrame(controls_frame, text="Sale Day Alerts")
        alerts_frame.pack(fill=tk.X, pady=10)
        
        alert_label = tk.Label(alerts_frame, text="Alert me when it's typically a good day to sell:")
        alert_label.pack(anchor="w", padx=10, pady=5)
        
        # Days of the week checkboxes
        days_frame = tk.Frame(alerts_frame)
        days_frame.pack(fill=tk.X, padx=10, pady=5)
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.day_vars = {}
        
        for i, day in enumerate(days):
            self.day_vars[day] = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(days_frame, text=day, variable=self.day_vars[day])
            chk.grid(row=0, column=i, padx=3)
        
        # Threshold settings
        threshold_frame = tk.Frame(alerts_frame)
        threshold_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(threshold_frame, text="Minimum volume:").grid(row=0, column=0, sticky="w")
        self.min_volume_var = tk.StringVar(value="5")
        tk.Entry(threshold_frame, textvariable=self.min_volume_var, width=5).grid(row=0, column=1, padx=5)
        
        tk.Label(threshold_frame, text="Minimum price:").grid(row=1, column=0, sticky="w", pady=5)
        self.min_price_var = tk.StringVar(value="1000")
        tk.Entry(threshold_frame, textvariable=self.min_price_var, width=5).grid(row=1, column=1, padx=5)
        
        # Update button
        update_btn = tk.Button(controls_frame, text="Update Analysis")
        update_btn.pack(pady=15)
        
        # Right side - Chart and statistics
        chart_frame = tk.Frame(content_frame, bg="#f0f0f0")
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Placeholder for chart
        chart_placeholder = tk.Label(chart_frame, text="Sales Volume Chart\nWill Appear Here", 
                                  font=("Arial", 12), bg="#f0f0f0")
        chart_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        # Statistics section at the bottom
        stats_frame = tk.Frame(sale_history_frame)
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        stats_title = tk.Label(stats_frame, text="Sales Statistics", font=("Arial", 10, "bold"))
        stats_title.pack(anchor="w")
        
        # Statistics in a grid layout
        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, pady=5)
        
        # Row 1
        tk.Label(stats_grid, text="Best Day:", anchor="w", width=15).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.best_day_var = tk.StringVar(value="--")
        tk.Label(stats_grid, textvariable=self.best_day_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(stats_grid, text="Worst Day:", anchor="w", width=15).grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.worst_day_var = tk.StringVar(value="--")
        tk.Label(stats_grid, textvariable=self.worst_day_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Row 2
        tk.Label(stats_grid, text="Avg. Daily Volume:", anchor="w", width=15).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.avg_volume_var = tk.StringVar(value="--")
        tk.Label(stats_grid, textvariable=self.avg_volume_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(stats_grid, text="Avg. Daily Price:", anchor="w", width=15).grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.avg_price_var = tk.StringVar(value="--")
        tk.Label(stats_grid, textvariable=self.avg_price_var, width=10).grid(row=1, column=3, sticky="w", padx=5, pady=2)
    
    def load_data(self):
        try:
            # Show loading screen
            self.show_loading_screen("Loading item data...")
            
            # Get marketable items directly from Universalis
            self.update_loading_progress(20, "Fetching marketable items from Universalis...")
            
            # Use the Universalis marketable endpoint
            url = "https://universalis.app/api/v2/marketable"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # This endpoint returns just a list of IDs, so we need to get names separately
                marketable_ids = response.json()
                self.update_loading_progress(40, "Fetching item details...", f"Found {len(marketable_ids)} marketable items")
                
                # Use the items.json from ffxiv-teamcraft for item names
                items_url = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json"
                items_response = requests.get(items_url, timeout=30)
                
                if items_response.status_code == 200:
                    items_data = items_response.json()
                    
                    # Process item data
                    self.update_loading_progress(60, "Processing item data...")
                    
                    global itemDictionary
                    global printableItems
                    
                    # Create the item dictionary as a list of [id, name] pairs
                    itemDictionary = []
                    for item_id in marketable_ids:
                        item_id_str = str(item_id)
                        if item_id_str in items_data and "en" in items_data[item_id_str]:
                            itemDictionary.append([item_id, items_data[item_id_str]["en"]])
                    
                    # Sort by item ID (not alphabetically)
                    itemDictionary.sort(key=lambda x: x[0])
                    
                    # Extract just the names for display
                    printableItems = [item[1] for item in itemDictionary]
                    
                    # Update item list with just the names
                    self.update_item_list(printableItems)
                    
                    # Initialize the world dropdown based on the saved data center
                    self.initialize_world_dropdown()
                    
                    self.update_loading_progress(100, "Item data loaded successfully", f"Loaded {len(itemDictionary)} items")
                else:
                    raise Exception(f"Failed to fetch item details: HTTP Status {items_response.status_code}")
            else:
                raise Exception(f"Failed to fetch marketable items: HTTP Status {response.status_code}")
            
            # Hide loading screen
            self.hide_loading_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            if hasattr(self, 'loading_window') and self.loading_window.winfo_exists():
                self.hide_loading_screen()
    
    def show_loading_screen(self, message):
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
        if hasattr(self, 'loading_progress'):
            self.loading_progress["value"] = percent
            self.loading_label.config(text=message)
            if details:
                self.loading_details.config(text=details)
            self.loading_window.update()
    
    def hide_loading_screen(self):
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
    
    def initialize_world_dropdown(self):
        try:
            # Get the saved data center
            dc = self.dc_var.get()
            
            # Fetch servers for the data center
            dc_response = json.loads(requests.get(DCURL).text)
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
        self.item_listbox.delete(0, tk.END)
        for item in items:
            self.item_listbox.insert(tk.END, item)
    
    def on_search(self):
        search_string = self.search_var.get()
        updated_list = [
            filtered_item
            for filtered_item in printableItems
            if search_string.upper() in filtered_item.upper()
        ]
        self.update_item_list(updated_list)
    
    def on_language_change(self, event):
        try:
            lang = self.language_var.get()
            switchLanguage(self, lang)
            
            # Save the language setting
            self.settings["language"] = lang
            save_settings(self.settings)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch language: {e}")
    
    def on_dc_change(self, event):
        try:
            dc = self.dc_var.get()
            dc_response = json.loads(requests.get(DCURL).text)
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
        try:
            world = self.world_var.get()
            
            # Save the world setting
            self.settings["world"] = world
            save_settings(self.settings)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save world setting: {e}")
    
    def on_item_select(self, event):
        try:
            selected_indices = self.item_listbox.curselection()
            if selected_indices:
                selected_item = self.item_listbox.get(selected_indices[0])
                # Find the item ID for the selected item name
                matching_items = [item for item in itemDictionary if item[1] == selected_item]
                if matching_items:
                    item_id = matching_items[0][0]
                    
                    url = "".join([XIVAPIBaseURL, str(item_id)])
                    item_response = json.loads(requests.get(url).text)
                    
                    lang = self.language_var.get()
                    if lang == "English":
                        self.item_name_var.set(item_response["Name_en"])
                        self.item_desc_text.delete(1.0, tk.END)
                        self.item_desc_text.insert(tk.END, item_response["Description_en"])
                    elif lang == "Deutsch":
                        self.item_name_var.set(item_response["Name_de"])
                        self.item_desc_text.delete(1.0, tk.END)
                        self.item_desc_text.insert(tk.END, item_response["Description_de"])
                    elif lang == "日本語":
                        self.item_name_var.set(item_response["Name_ja"])
                        self.item_desc_text.delete(1.0, tk.END)
                        self.item_desc_text.insert(tk.END, item_response["Description_ja"])
                    elif lang == "Français":
                        self.item_name_var.set(item_response["Name_fr"])
                        self.item_desc_text.delete(1.0, tk.END)
                        self.item_desc_text.insert(tk.END, item_response["Description_fr"])
                    
                    # Fetch market data for the selected item
                    data_center = self.dc_var.get()
                    world = self.world_var.get()
                    
                    # Determine whether to use data center or world for market data
                    market_location = world if world != "All" else data_center
                    
                    # Fetch market data from Universalis API
                    market_url = f"{UbaseUrl}{market_location}/{item_id}"
                    try:
                        # Clear the listings listbox
                        self.listings_listbox.delete(0, tk.END)
                        
                        # Show loading message
                        self.listings_listbox.insert(tk.END, "Loading market data...")
                        self.root.update_idletasks()  # Update the UI to show loading message
                        
                        # Fetch market data
                        market_response = requests.get(market_url).json()
                        
                        # Clear the loading message
                        self.listings_listbox.delete(0, tk.END)
                        
                        # Check if there are listings
                        if "listings" in market_response and market_response["listings"]:
                            # Add header
                            self.listings_listbox.insert(tk.END, f"{'Price':^10} | {'Qty':^6} | {'Total':^10} | {'World':^10} | {'Last Updated':^20}")
                            self.listings_listbox.insert(tk.END, "-" * 65)
                            
                            # Add each listing
                            for listing in market_response["listings"]:
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
                                
                                # Format and add the listing
                                listing_text = f"{price:>10,} | {quantity:^6} | {total:>10,} | {world_name:^10} | {formatted_time:^20}"
                                self.listings_listbox.insert(tk.END, listing_text)
                        else:
                            self.listings_listbox.insert(tk.END, "No listings found for this item.")
                    except Exception as e:
                        self.listings_listbox.delete(0, tk.END)
                        self.listings_listbox.insert(tk.END, f"Error fetching market data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load item details: {e}")

def main():
    root = tk.Tk()
    app = PyFFUniverseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
