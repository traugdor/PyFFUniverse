import tkinter as tk
from ui.app import PyFFUniverseApp

def main():    
    # Create the root window
    root = tk.Tk()
    
    # Create the application
    app = PyFFUniverseApp(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
