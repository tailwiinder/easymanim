import pytest
import tkinter as tk
import ttkbootstrap as ttk
from unittest.mock import Mock

# Assuming StatusBarPanel will be in src/easymanim/gui/statusbar_panel.py
from easymanim.gui.statusbar_panel import StatusBarPanel

# Fixture to create a root window for tests needing GUI elements
@pytest.fixture(scope="function") # Function scope for isolation
def root():
    root = tk.Tk()
    root.withdraw() # Hide the main window during tests
    yield root
    root.destroy()

def test_statusbar_panel_set_status(root, mocker):
    """Test the initial status and the set_status method."""
    mock_ui_manager = mocker.Mock() # Not really needed, but pass for consistency

    # Create the panel instance
    statusbar_panel = StatusBarPanel(root, mock_ui_manager)
    statusbar_panel.pack(fill=tk.X) # Status bar typically fills horizontally
    root.update_idletasks()

    # Find the Label widget (assuming it's the only direct child)
    children = statusbar_panel.winfo_children()
    assert len(children) == 1, "Expected 1 child widget (status label)"
    status_label = children[0]
    assert isinstance(status_label, ttk.Label), "Expected status widget to be a ttk.Label"

    # Check initial text (assuming starts with "Ready")
    initial_text = "Ready"
    assert status_label.cget("text") == initial_text

    # Call set_status
    new_status = "Processing request..."
    statusbar_panel.set_status(new_status)
    root.update_idletasks()

    # Check updated text
    assert status_label.cget("text") == new_status 