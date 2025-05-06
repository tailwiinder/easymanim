import pytest
import tkinter as tk
import ttkbootstrap as ttk
from unittest.mock import Mock
from PIL import Image
import io

# Assuming PreviewPanel will be in src/easymanim/gui/preview_panel.py
from easymanim.gui.preview_panel import PreviewPanel

# Fixture to create a root window for tests needing GUI elements
@pytest.fixture(scope="function")
def root():
    root = tk.Tk()
    root.withdraw() # Hide the main window during tests
    yield root
    root.destroy()

def test_preview_panel_init_state(root, mocker):
    """Test the initial state of the PreviewPanel."""
    mock_ui_manager = mocker.Mock()

    # Create the panel instance
    preview_panel = PreviewPanel(root, mock_ui_manager)
    preview_panel.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()

    # Find Canvas and Button
    canvas = None
    refresh_button = None
    for widget in preview_panel.winfo_children():
        if isinstance(widget, tk.Canvas):
            canvas = widget
        elif isinstance(widget, ttk.Button) and "Refresh" in widget.cget("text"):
            refresh_button = widget
            
    assert canvas is not None, "Canvas widget not found"
    assert refresh_button is not None, "Refresh Preview button not found"
    
    # Check button state (should be enabled initially)
    assert str(refresh_button.cget("state")) == "normal"

    # Check for initial placeholder on canvas (assuming tagged 'placeholder')
    # Explicitly set size and update/draw like in TimelinePanel tests
    canvas.config(width=300, height=200) 
    root.update_idletasks()
    root.update() 
    # Assume a method like _draw_placeholder exists or is called in init
    if hasattr(preview_panel, "_draw_placeholder"):
         preview_panel._draw_placeholder()
         root.update()
         
    placeholder_items = canvas.find_withtag("placeholder")
    assert placeholder_items, "Placeholder item not found on canvas"
    # Optional: Check placeholder text content if needed
    # placeholder_text = canvas.itemcget(placeholder_items[0], "text")
    # assert "refresh" in placeholder_text.lower()

def test_preview_panel_refresh_button_calls_handler(root, mocker):
    """Test that clicking the refresh button calls the UIManager handler."""
    mock_ui_manager = mocker.Mock()

    # Create the panel instance
    preview_panel = PreviewPanel(root, mock_ui_manager)
    preview_panel.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()

    # Find the refresh button
    refresh_button = preview_panel.refresh_button
    assert refresh_button is not None, "Refresh button reference not found on panel instance"
    assert isinstance(refresh_button, ttk.Button), "Refresh widget is not a Button"

    # Simulate button click
    refresh_button.invoke()
    root.update()

    # Assert handler was called
    mock_ui_manager.handle_refresh_preview_request.assert_called_once()

def test_preview_panel_show_rendering_state(root, mocker):
    """Test that show_rendering_state disables button and updates canvas."""
    mock_ui_manager = mocker.Mock()
    preview_panel = PreviewPanel(root, mock_ui_manager)
    preview_panel.pack(fill=tk.BOTH, expand=True)
    canvas = preview_panel.canvas
    refresh_button = preview_panel.refresh_button
    canvas.config(width=300, height=200)
    root.update_idletasks()
    root.update()
    if hasattr(preview_panel, "_draw_placeholder"): # Ensure initial placeholder drawn
         preview_panel._draw_placeholder()
         root.update()

    # Check initial state
    assert str(refresh_button.cget("state")) == "normal"
    assert canvas.find_withtag("placeholder"), "Initial placeholder missing"
    assert not canvas.find_withtag("rendering_text"), "Rendering text should not exist initially"

    # Call the state change method
    preview_panel.show_rendering_state()
    root.update_idletasks()

    # Assert new state
    assert str(refresh_button.cget("state")) == "disabled"
    assert not canvas.find_withtag("placeholder"), "Placeholder should be removed"
    rendering_items = canvas.find_withtag("rendering_text")
    assert rendering_items, "Rendering text not found"
    # Optional: check text content
    # text = canvas.itemcget(rendering_items[0], "text")
    # assert "rendering" in text.lower()

def test_preview_panel_show_idle_state(root, mocker):
    """Test that show_idle_state enables button and restores placeholder/image."""
    mock_ui_manager = mocker.Mock()
    preview_panel = PreviewPanel(root, mock_ui_manager)
    preview_panel.pack(fill=tk.BOTH, expand=True)
    canvas = preview_panel.canvas
    refresh_button = preview_panel.refresh_button
    canvas.config(width=300, height=200)
    root.update_idletasks()
    root.update()

    # Put panel in rendering state first
    preview_panel.show_rendering_state()
    root.update_idletasks()
    assert str(refresh_button.cget("state")) == "disabled", "Button should be disabled in rendering state"
    assert canvas.find_withtag("rendering_text"), "Rendering text missing in rendering state"
    assert not canvas.find_withtag("placeholder"), "Placeholder should be absent in rendering state"

    # Call the state change method back to idle
    preview_panel.show_idle_state()
    root.update_idletasks()
    root.update() # Extra update for drawing
    if hasattr(preview_panel, "_draw_placeholder"): # Ensure placeholder drawn if applicable
         preview_panel._draw_placeholder()
         root.update()

    # Assert idle state
    assert str(refresh_button.cget("state")) == "normal"
    assert not canvas.find_withtag("rendering_text"), "Rendering text should be removed"
    assert canvas.find_withtag("placeholder"), "Placeholder should be restored"

# Helper to create dummy PNG bytes for testing
def create_dummy_png_bytes(width=10, height=10, color="blue") -> bytes:
    img = Image.new('RGB', (width, height), color=color)
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    return byte_arr.getvalue()

def test_preview_panel_display_image(root, mocker):
    """Test that display_image shows the image on the canvas."""
    mock_ui_manager = mocker.Mock()
    preview_panel = PreviewPanel(root, mock_ui_manager)
    preview_panel.pack(fill=tk.BOTH, expand=True)
    canvas = preview_panel.canvas
    canvas.config(width=300, height=200)
    root.update_idletasks()
    root.update()
    if hasattr(preview_panel, "_draw_placeholder"): # Ensure initial placeholder drawn
         preview_panel._draw_placeholder()
         root.update()
         
    # Verify initial state
    assert canvas.find_withtag("placeholder"), "Initial placeholder missing"
    assert not canvas.find_withtag("preview_image"), "Preview image should not exist initially"

    # Create dummy image data
    dummy_bytes = create_dummy_png_bytes(50, 50, "red")

    # Call display_image
    preview_panel.display_image(dummy_bytes)
    root.update_idletasks()

    # Assert state after displaying image
    assert not canvas.find_withtag("placeholder"), "Placeholder should be removed"
    image_items = canvas.find_withtag("preview_image") # Assumes implementation uses this tag
    assert image_items, "Preview image item not found on canvas"
    # Optional: More checks (e.g., check coordinates, although they depend on centering logic)
    # coords = canvas.coords(image_items[0])
    # assert coords == [expected_x, expected_y]

    # Verify internal state update (optional)
    assert preview_panel._image_on_canvas is not None
    assert preview_panel._photo_image is not None

# Placeholders for future tests
# def test_preview_panel_display_image(root, mocker):
#     pass 