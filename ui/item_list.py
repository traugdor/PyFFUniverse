import tkinter as tk
from tkinter import ttk
from utils.translations import get_text
from utils.translation_widgets import create_label, create_button, create_labelframe

def create_item_list(parent, callback):
    """
    Create the item list frame.
    
    Args:
        parent: The parent widget
        callback: The callback function to be called when an item is selected
        
    Returns:
        dict: A dictionary containing the frame and its components
    """
    item_list_frame = ttk.Frame(parent)
    item_list_frame.pack(fill=tk.BOTH, expand=True)
    
    item_list_box = tk.Listbox(item_list_frame, width=40, height=30)
    item_list_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    item_list_box.bind('<<ListboxSelect>>', callback)
    
    scrollbar = ttk.Scrollbar(item_list_frame, orient=tk.VERTICAL, command=item_list_box.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    item_list_box.config(yscrollcommand=scrollbar.set)
    
    return item_list_box