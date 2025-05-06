import pytest
import tkinter as tk
import ttkbootstrap as ttk  # Import ttk
from unittest.mock import Mock

# Assuming ToolbarPanel will be in src/easymanim/gui/toolbar_panel.py
# We'll need to adjust the import path if the structure differs or use editable install.
# For now, let's assume it's findable.
from easymanim.gui.toolbar_panel import ToolbarPanel
# UIManager might not be directly needed if we just mock its interface
# from easymanim.ui.ui_manager import UIManager # Keep commented unless needed

# Fixture to create a root window for tests needing GUI elements
@pytest.fixture(scope="function")
def root():
    # Use ttkbootstrap Themed Tk for consistency if needed, though Tk() often works
    # root = ttk.Window()
    root = tk.Tk()
    root.withdraw() # Hide the main window during tests
    yield root
    root.destroy()

def test_toolbar_add_circle_button_command(root, mocker):
    """Test that clicking the 'Add Circle' button calls the correct UIManager method."""
    mock_ui_manager = mocker.Mock()

    # Create the panel instance
    toolbar_panel = ToolbarPanel(root, mock_ui_manager)
    toolbar_panel.pack() # Necessary for widget geometry/finding

    # Find the 'Add Circle' button - brittle, depends on implementation details
    # A better way might be to store button references on the instance if needed often
    add_circle_button = None
    for widget in toolbar_panel.winfo_children():
        # Check for ttk.Button instead of tk.Button
        if isinstance(widget, ttk.Button) and widget.cget("text") == "Add Circle":
            add_circle_button = widget
            break

    assert add_circle_button is not None, "'Add Circle' button not found"

    # Simulate the button click
    add_circle_button.invoke()

    # Assert that the UIManager method was called correctly
    mock_ui_manager.handle_add_object_request.assert_called_once_with('Circle')

# Placeholder for future tests
def test_toolbar_add_square_button_command(root, mocker):
    """Test that clicking the 'Add Square' button calls the correct UIManager method."""
    mock_ui_manager = mocker.Mock()
    toolbar_panel = ToolbarPanel(root, mock_ui_manager)
    toolbar_panel.pack()

    add_square_button = None
    for widget in toolbar_panel.winfo_children():
        if isinstance(widget, ttk.Button) and widget.cget("text") == "Add Square":
            add_square_button = widget
            break
    assert add_square_button is not None, "'Add Square' button not found"

    add_square_button.invoke()
    mock_ui_manager.handle_add_object_request.assert_called_once_with('Square')

def test_toolbar_add_text_button_command(root, mocker):
    """Test that clicking the 'Add Text' button calls the correct UIManager method."""
    mock_ui_manager = mocker.Mock()
    toolbar_panel = ToolbarPanel(root, mock_ui_manager)
    toolbar_panel.pack()

    add_text_button = None
    for widget in toolbar_panel.winfo_children():
        if isinstance(widget, ttk.Button) and widget.cget("text") == "Add Text":
            add_text_button = widget
            break
    assert add_text_button is not None, "'Add Text' button not found"

    add_text_button.invoke()
    mock_ui_manager.handle_add_object_request.assert_called_once_with('Text') 