import tkinter as tk
import ttkbootstrap as ttk
from typing import Callable, Any

# Core Logic
from .logic.scene_builder import SceneBuilder

# Interface
from .interface.manim_interface import ManimInterface

# UI Manager
from .ui.ui_manager import UIManager

# GUI Panels
from .gui.toolbar_panel import ToolbarPanel
from .gui.timeline_panel import TimelinePanel
from .gui.properties_panel import PropertiesPanel
from .gui.preview_panel import PreviewPanel
from .gui.statusbar_panel import StatusBarPanel

class MainApplication(ttk.Window):
    """The main application window and orchestrator."""

    def __init__(self):
        """Initialize the application."""
        # Use a ttkbootstrap theme
        super().__init__(themename="darkly") # Or another theme like "litera", "cosmo"

        self.title("EasyManim Editor V0.1")
        self.geometry("1200x800") # Initial size
        
        print("Initializing core components...")
        # --- Initialize Core Components ---
        self.scene_builder = SceneBuilder()
        self.manim_interface = ManimInterface(self) # Pass app for scheduling
        self.ui_manager = UIManager(self, self.scene_builder, self.manim_interface)
        print("Core components initialized.")

        print("Creating widgets...")
        # --- Create GUI Widgets ---
        self._create_widgets()
        print("Widgets created.")

    def _create_widgets(self):
        """Create and layout all the GUI panels."""
        
        # --- Configure Main Window Grid ---
        self.columnconfigure(0, weight=1) # Left column group (Timeline/Props)
        self.columnconfigure(1, weight=3) # Right column group (Preview) - 3x wider
        self.rowconfigure(0, weight=0) # Toolbar row (fixed height)
        self.rowconfigure(1, weight=1) # Main content row (expands)
        self.rowconfigure(2, weight=0) # Status bar row (fixed height)
        
        # --- Create Panel Instances ---
        print("  Instantiating panels...")
        # Toolbar
        toolbar = ToolbarPanel(self, self.ui_manager)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.ui_manager.register_panel("toolbar", toolbar)

        # Left Pane Frame (for Timeline and Properties)
        left_pane = ttk.Frame(self)
        left_pane.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=(0, 5))
        left_pane.rowconfigure(0, weight=1) # Timeline expands
        left_pane.rowconfigure(1, weight=1) # Properties expands
        left_pane.columnconfigure(0, weight=1)
        
        # Timeline
        timeline = TimelinePanel(left_pane, self.ui_manager)
        timeline.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        self.ui_manager.register_panel("timeline", timeline)

        # Properties
        properties = PropertiesPanel(left_pane, self.ui_manager)
        properties.grid(row=1, column=0, sticky="nsew")
        self.ui_manager.register_panel("properties", properties)

        # Preview (Right Pane)
        preview = PreviewPanel(self, self.ui_manager)
        preview.grid(row=1, column=1, sticky="nsew", padx=(2, 5), pady=(0, 5))
        self.ui_manager.register_panel("preview", preview)
        
        # Status Bar
        statusbar = StatusBarPanel(self, self.ui_manager)
        statusbar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(2, 5))
        self.ui_manager.register_panel("statusbar", statusbar)
        print("  Panels instantiated and gridded.")

    def schedule_task(self, callback: Callable[..., Any], *args: Any):
        """Schedule a task (callback) to be run in the main Tkinter thread.
        
        This is crucial for updating the GUI from background threads (like ManimInterface).
        Args:
            callback: The function to call.
            *args: Arguments to pass to the callback.
        """
        # print(f"Scheduling task: {callback.__name__} with args: {args}") # Debug
        self.after(0, lambda: callback(*args))

    def run(self):
        """Start the Tkinter main event loop."""
        print("Starting main application loop...")
        self.mainloop()

# Entry point will be in a separate main.py or handled by packaging
# if __name__ == "__main__":
#     app = MainApplication()
#     app.run() 