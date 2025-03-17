import tkinter as tk
from ui.app import PyFFUniverseApp
import pyuac

def main():
    # Request admin privileges
    # if not pyuac.isUserAdmin():
    #     pyuac.runAsAdmin()
    #     return
    
    # Create the root window
    root = tk.Tk()
    
    # Create the application
    app = PyFFUniverseApp(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
