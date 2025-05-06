import tkinter as tk
import ttkbootstrap as ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import at runtime
    from ..ui.ui_manager import UIManager

class StatusBarPanel(ttk.Frame):
    """A simple status bar panel to display messages."""

    def __init__(self, parent, ui_manager: 'UIManager'):
        """Initialize the StatusBarPanel.

        Args:
            parent: The parent widget.
            ui_manager: The UIManager instance (passed for consistency).
        """
        # Use relief and padding common for status bars
        super().__init__(parent, padding=(5, 2), relief="groove", borderwidth=1)
        self.ui_manager = ui_manager # Store even if not used directly
        
        self.status_var = tk.StringVar(value="Ready") # Default text
        
        status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor=tk.W # Anchor text to the left
        )
        status_label.pack(fill=tk.X, expand=True)

    def set_status(self, text: str):
        """Update the text displayed in the status bar."""
        self.status_var.set(text) 