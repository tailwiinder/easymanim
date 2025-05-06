import tkinter as tk
import ttkbootstrap as ttk

# Assuming UIManager is in src/easymanim/ui/ui_manager.py
# We need it for type hinting potentially, but not runtime logic here
# from ..ui.ui_manager import UIManager # Use relative import

class ToolbarPanel(ttk.Frame):
    """A frame containing buttons to add new objects to the scene."""

    def __init__(self, parent, ui_manager):
        """Initialize the ToolbarPanel.

        Args:
            parent: The parent widget.
            ui_manager: The UIManager instance to handle button actions.
        """
        super().__init__(parent)
        self.ui_manager = ui_manager

        self._create_widgets()

    def _create_widgets(self):
        """Create and layout the widgets for the toolbar."""

        # Configure style for buttons if needed (e.g., padding)
        # style = ttk.Style()
        # style.configure('Toolbar.TButton', padding=5)

        # --- Add Object Buttons ---
        add_circle_btn = ttk.Button(
            self,
            text="Add Circle",
            command=lambda: self.ui_manager.handle_add_object_request('Circle'),
            # style='Toolbar.TButton'
            bootstyle="info"
        )
        add_circle_btn.pack(side=tk.LEFT, padx=5, pady=5)

        add_square_btn = ttk.Button(
            self,
            text="Add Square",
            command=lambda: self.ui_manager.handle_add_object_request('Square'),
            # style='Toolbar.TButton'
            bootstyle="info"
        )
        add_square_btn.pack(side=tk.LEFT, padx=5, pady=5)

        add_text_btn = ttk.Button(
            self,
            text="Add Text",
            command=lambda: self.ui_manager.handle_add_object_request('Text'),
            # style='Toolbar.TButton'
            bootstyle="info"
        )
        add_text_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Add more buttons as needed (e.g., shapes, controls)

        # --- Separator --- (Optional, for visual distinction)
        separator = ttk.Separator(self, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill='y', padx=10, pady=5)

        # --- Render Video Button ---
        render_video_btn = ttk.Button(
            self,
            text="Render Video",
            command=self.ui_manager.handle_render_video_request, # Direct call
            bootstyle="success" # 'success' (green) for a positive final action
        )
        render_video_btn.pack(side=tk.LEFT, padx=5, pady=5) 