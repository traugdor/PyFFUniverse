import json
import os

class Translator:
    def __init__(self, language="en"):
        self.language = language
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translations for the current language"""
        try:
            # Get the base directory of the application
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            translation_file = os.path.join(base_dir, 'translations', f'{self.language}.json')
            
            with open(translation_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")
            # If loading fails, try to load English as fallback
            if self.language != "en":
                self.language = "en"
                self.load_translations()
    
    def set_language(self, language):
        """Change the current language"""
        if language in ["en", "de", "jp", "fr"]:
            self.language = language
            self.load_translations()
    
    def get(self, key, default=""):
        """Get a translation by key"""
        # Split the key by dots to navigate nested dictionaries
        parts = key.split('.')
        result = self.translations
        
        try:
            for part in parts:
                result = result[part]
            return result
        except (KeyError, TypeError):
            return default

# Create a global translator instance
translator = Translator()

def get_text(key, default=""):
    """Get translated text for a key"""
    return translator.get(key, default)

def set_language(language):
    """Set the current language"""
    translator.set_language(language)

def get_language_code(language_name):
    """Convert language name to language code"""
    language_map = {
        "English": "en",
        "Deutsch": "de",
        "日本語": "jp",
        "Français": "fr"
    }
    return language_map.get(language_name, "en")
