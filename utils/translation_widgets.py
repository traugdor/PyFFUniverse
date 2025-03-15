import tkinter as tk
from tkinter import ttk
from utils.translations import get_text

def create_label(parent, key, default, **kwargs):
    """
    Create a label with translation support
    
    Args:
        parent: The parent widget
        key: The translation key
        default: The default text (English)
        **kwargs: Additional arguments for the label widget
        
    Returns:
        ttk.Label: The created label with translation support
    """
    widget = ttk.Label(parent, text=get_text(key, default), **kwargs)
    widget._translation_key = key
    widget._translation_default = default
    return widget

def create_button(parent, key, default, **kwargs):
    """
    Create a button with translation support
    
    Args:
        parent: The parent widget
        key: The translation key
        default: The default text (English)
        **kwargs: Additional arguments for the button widget
        
    Returns:
        ttk.Button: The created button with translation support
    """
    widget = ttk.Button(parent, text=get_text(key, default), **kwargs)
    widget._translation_key = key
    widget._translation_default = default
    return widget

def create_checkbutton(parent, key, default, **kwargs):
    """
    Create a checkbutton with translation support
    
    Args:
        parent: The parent widget
        key: The translation key
        default: The default text (English)
        **kwargs: Additional arguments for the checkbutton widget
        
    Returns:
        ttk.Checkbutton: The created checkbutton with translation support
    """
    widget = ttk.Checkbutton(parent, text=get_text(key, default), **kwargs)
    widget._translation_key = key
    widget._translation_default = default
    return widget

def create_radiobutton(parent, key, default, **kwargs):
    """
    Create a radiobutton with translation support
    
    Args:
        parent: The parent widget
        key: The translation key
        default: The default text (English)
        **kwargs: Additional arguments for the radiobutton widget
        
    Returns:
        ttk.Radiobutton: The created radiobutton with translation support
    """
    widget = ttk.Radiobutton(parent, text=get_text(key, default), **kwargs)
    widget._translation_key = key
    widget._translation_default = default
    return widget

def create_labelframe(parent, key, default, **kwargs):
    """
    Create a labelframe with translation support
    
    Args:
        parent: The parent widget
        key: The translation key
        default: The default text (English)
        **kwargs: Additional arguments for the labelframe widget
        
    Returns:
        ttk.LabelFrame: The created labelframe with translation support
    """
    widget = ttk.LabelFrame(parent, text=get_text(key, default), **kwargs)
    widget._translation_key = key
    widget._translation_default = default
    return widget

def set_translation_key(widget, key, default):
    """
    Set translation key for an existing widget
    
    Args:
        widget: The widget to set the translation key for
        key: The translation key
        default: The default text (English)
    """
    widget._translation_key = key
    widget._translation_default = default
    if hasattr(widget, 'config') and 'text' in widget.config():
        widget.config(text=get_text(key, default))
