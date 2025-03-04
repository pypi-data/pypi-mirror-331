import tkinter as tk
from tkinter import ttk, PhotoImage
import os

class App:
    def __init__(self, name = None, resolution = None, theme = None, icon = None, developer = False):
        if (name is None):
            name = "GladUI"
        if (resolution is None):
            resolution = "240x120"
        if (theme is None):
            theme = "dark"

        self.root = tk.Tk()
        self.root.title(name)
        self.root.geometry(resolution)
        
        if (theme.lower() == "dark"):
            self.bg = "#222222"
            self.fg = "white"
        elif (theme.lower() == "light"):
            self.bg = "white"
            self.fg = "black"
        else:
            raise ValueError("Invalid theme. Valid themes are: 'light', 'dark'")

        self.root.configure(bg=self.bg)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        if icon is None:
            try:
                default_icon_path = "GladUI.png"
                if os.path.exists(default_icon_path):
                    default_icon = PhotoImage(file = default_icon_path)
                    self.root.iconphoto(True, default_icon)
                else:
                    if developer:
                        print("Warning: Default icon 'GladUI.png' not found.")
            except Exception as e:
                if developer:
                    print(f"Failed to load default icon: {e}")
        else:
            try:
                custom_icon = PhotoImage(file = icon)
                self.root.iconphoto(True, custom_icon)
            except Exception as e:
                if (developer):
                    print(f"Error: Failed to load custom icon '{icon}'. {e}")

    def run(self):
        self.root.mainloop()
