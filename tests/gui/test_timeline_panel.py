import pytest
import tkinter as tk
import ttkbootstrap as ttk
from unittest.mock import Mock

# Assuming TimelinePanel will be in src/easymanim/gui/timeline_panel.py
from easymanim.gui.timeline_panel import TimelinePanel

# Fixture to create a root window for tests needing GUI elements
@pytest.fixture(scope="module")
def root():
    root = tk.Tk()
    root.withdraw() # Hide the main window during tests
    yield root
    root.destroy()

def test_timeline_panel_init_shows_placeholder(root, mocker):
    """Test that the TimelinePanel shows placeholder text on initialization."""
    mock_ui_manager = mocker.Mock()

    # Create the panel instance
    timeline_panel = TimelinePanel(root, mock_ui_manager)
    timeline_panel.pack(fill=tk.BOTH, expand=True) # Need layout for canvas size

    # Find the Canvas widget
    canvas = None
    for widget in timeline_panel.winfo_children():
        if isinstance(widget, tk.Canvas):
            canvas = widget
            break
    assert canvas is not None, "Canvas widget not found in TimelinePanel"

    # Explicitly set a size for the canvas in the test
    canvas.config(width=300, height=200)

    # Force tkinter to update geometry/layout so canvas has dimensions
    root.update_idletasks()
    root.update()

    # Explicitly call draw method after update to ensure text is drawn
    # Handles potential timing issues with <Configure> event in tests
    timeline_panel._draw_placeholder_text()
    root.update() # Force full update after drawing

    # Find the placeholder text item by tag (assuming we implement it with this tag)
    placeholder_tag = "placeholder_text"
    placeholder_items = canvas.find_withtag(placeholder_tag)

    assert len(placeholder_items) == 1, f"Expected 1 item with tag '{placeholder_tag}', found {len(placeholder_items)}"

    placeholder_id = placeholder_items[0]
    placeholder_text = canvas.itemcget(placeholder_id, "text")

    expected_text = "Timeline - Add objects using the toolbar"
    assert placeholder_text == expected_text, f"Expected placeholder text '{expected_text}', but got '{placeholder_text}'"

# Placeholder for future tests
def test_timeline_panel_add_block_creates_items(root, mocker):
    """Test that add_block adds rectangle and text items to the canvas."""
    mock_ui_manager = mocker.Mock()
    timeline_panel = TimelinePanel(root, mock_ui_manager)
    timeline_panel.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()
    canvas = timeline_panel.canvas

    # Ensure placeholder is there initially
    # Explicitly call draw method after update to ensure text is drawn
    timeline_panel._draw_placeholder_text()
    assert canvas.find_withtag("placeholder_text"), "Placeholder should exist initially"

    # Call add_block
    test_id = "circle_abc"
    test_type = "Circle"
    timeline_panel.add_block(obj_id=test_id, obj_type=test_type)
    root.update_idletasks() # Ensure drawing updates

    # Assert placeholder is gone
    assert not canvas.find_withtag("placeholder_text"), "Placeholder should be removed after adding a block"

    # Assert block items exist (assuming a common tag 'timeline_block' and specific id tag)
    block_items = canvas.find_withtag(f"obj_{test_id}")
    assert len(block_items) >= 2, f"Expected at least 2 items (rect, text) for obj_{test_id}, found {len(block_items)}"

    # Find the text item specifically (might need a more specific tag or check item type)
    text_item_id = None
    rect_item_id = None
    for item_id in block_items:
        try: # Check item type safely
            if canvas.type(item_id) == "text":
                text_item_id = item_id
            elif canvas.type(item_id) == "rectangle":
                rect_item_id = item_id
        except tk.TclError: # Item might have been deleted?
            pass 
            
    assert text_item_id is not None, "Text item for the block not found"
    assert rect_item_id is not None, "Rectangle item for the block not found"

    # Check text content
    block_text = canvas.itemcget(text_item_id, "text")
    assert test_id in block_text, f"Block text '{block_text}' should contain object ID '{test_id}'"
    assert test_type in block_text, f"Block text '{block_text}' should contain object type '{test_type}'"

    # Check internal mapping
    # We need to know which item ID (rect or text) is used as the key
    # Let's assume the rectangle ID is the key for now (implementation detail)
    assert rect_item_id in timeline_panel.object_canvas_items, "Rectangle ID not found in internal mapping"
    assert timeline_panel.object_canvas_items[rect_item_id] == test_id, "Internal mapping does not point to the correct object ID"

def test_timeline_panel_click_block_selects(root, mocker):
    """Test clicking a block calls ui_manager.handle_timeline_selection with the object ID."""
    mock_ui_manager = mocker.Mock()
    timeline_panel = TimelinePanel(root, mock_ui_manager)
    timeline_panel.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()
    canvas = timeline_panel.canvas
    timeline_panel._draw_placeholder_text() # Ensure placeholder drawn initially if needed

    # Add a block
    test_id = "circle_xyz"
    timeline_panel.add_block(obj_id=test_id, obj_type="Circle")
    root.update_idletasks()

    # Find the rectangle ID for the added block
    rect_item_id = None
    block_items = canvas.find_withtag(f"obj_{test_id}")
    for item_id in block_items:
        try:
            if canvas.type(item_id) == "rectangle":
                rect_item_id = item_id
                break
        except tk.TclError:
            pass
    assert rect_item_id is not None, "Rectangle for block not found"

    # Get coordinates of the rectangle to simulate a click inside it
    coords = canvas.coords(rect_item_id)
    assert len(coords) == 4, "Expected 4 coordinates for rectangle"
    click_x = (coords[0] + coords[2]) / 2 # Middle X
    click_y = (coords[1] + coords[3]) / 2 # Middle Y

    # Unbind the default configure event temporarily if it interferes
    # canvas.unbind("<Configure>")

    # Simulate the click event
    # We need to ensure the _on_canvas_click handler is bound first (will be done in Green step)
    # For now, we can call it directly if the binding isn't active
    # timeline_panel._on_canvas_click(mocker.Mock(x=click_x, y=click_y))

    # Directly call the handler with a mock event
    mock_event = mocker.Mock()
    mock_event.x = int(click_x)
    mock_event.y = int(click_y)
    timeline_panel._on_canvas_click(mock_event)

    # Assert UIManager was called with the correct ID
    mock_ui_manager.handle_timeline_selection.assert_called_once_with(test_id)

def test_timeline_panel_click_background_deselects(root, mocker):
    """Test clicking the background calls ui_manager.handle_timeline_selection with None."""
    mock_ui_manager = mocker.Mock()
    timeline_panel = TimelinePanel(root, mock_ui_manager)
    # Give the canvas a defined size
    timeline_panel.pack(padx=20, pady=20)
    timeline_panel.config(width=200, height=100)
    canvas = timeline_panel.canvas
    canvas.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()
    timeline_panel._draw_placeholder_text() # Ensure placeholder drawn initially if needed

    # Optional: Add a block to ensure we're not clicking it
    timeline_panel.add_block(obj_id="dummy_id", obj_type="Square")
    root.update_idletasks()

    # Simulate a click far away from any potential blocks (e.g., near corner)
    # Use coordinates guaranteed to be outside the first block
    click_x = 190
    click_y = 90

    # Ensure find_closest at these coordinates returns nothing or the canvas itself
    # This depends slightly on canvas implementation details, but should not find a block
    # items_at_click = canvas.find_closest(click_x, click_y)
    # is_background_click = True
    # if items_at_click:
    #     item_id = items_at_click[0]
    #     tags = canvas.gettags(item_id)
    #     if any(tag.startswith("obj_") for tag in tags):
    #         is_background_click = False
    #
    # assert is_background_click, f"Click at ({click_x},{click_y}) incorrectly found an object block: {items_at_click}"

    # Directly call the handler with a mock event
    mock_event = mocker.Mock()
    mock_event.x = int(click_x)
    mock_event.y = int(click_y)
    timeline_panel._on_canvas_click(mock_event)

    # Assert UIManager was called with None
    mock_ui_manager.handle_timeline_selection.assert_called_once_with(None)

def test_timeline_panel_highlight_block(root, mocker):
    """Test that highlight_block changes the outline of the correct block."""
    mock_ui_manager = mocker.Mock() # Not strictly needed, but keep pattern
    timeline_panel = TimelinePanel(root, mock_ui_manager)
    timeline_panel.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()
    canvas = timeline_panel.canvas
    timeline_panel._draw_placeholder_text()

    # Add two blocks
    id1 = "circle_1"
    id2 = "square_2"
    timeline_panel.add_block(obj_id=id1, obj_type="Circle")
    timeline_panel.add_block(obj_id=id2, obj_type="Square")
    root.update_idletasks()

    # Helper to find rectangle ID for an object ID
    def find_rect_id(obj_id):
        for rect_id, mapped_obj_id in timeline_panel.object_canvas_items.items():
            if mapped_obj_id == obj_id:
                # Verify it's actually a rectangle before returning
                try:
                    if canvas.type(rect_id) == "rectangle":
                        return rect_id
                except tk.TclError:
                    pass # Item might not exist
        return None

    rect_id1 = find_rect_id(id1)
    rect_id2 = find_rect_id(id2)
    assert rect_id1 is not None, f"Rectangle for {id1} not found"
    assert rect_id2 is not None, f"Rectangle for {id2} not found"

    default_outline = "black" # As defined in add_block
    highlight_outline = "red" # Define highlight color
    highlight_width = 2 # Define highlight width
    default_width = 1

    # Initial state: both should have default outline
    assert canvas.itemcget(rect_id1, "outline") == default_outline
    assert canvas.itemcget(rect_id2, "outline") == default_outline
    assert int(float(canvas.itemcget(rect_id1, "width"))) == default_width
    assert int(float(canvas.itemcget(rect_id2, "width"))) == default_width


    # Highlight block 1
    timeline_panel.highlight_block(id1)
    root.update_idletasks()
    assert canvas.itemcget(rect_id1, "outline") == highlight_outline
    assert int(float(canvas.itemcget(rect_id1, "width"))) == highlight_width
    assert canvas.itemcget(rect_id2, "outline") == default_outline # Block 2 unchanged
    assert int(float(canvas.itemcget(rect_id2, "width"))) == default_width

    # Highlight block 2 (should deselect block 1)
    timeline_panel.highlight_block(id2)
    root.update_idletasks()
    assert canvas.itemcget(rect_id1, "outline") == default_outline # Block 1 back to default
    assert int(float(canvas.itemcget(rect_id1, "width"))) == default_width
    assert canvas.itemcget(rect_id2, "outline") == highlight_outline
    assert int(float(canvas.itemcget(rect_id2, "width"))) == highlight_width

    # Deselect all
    timeline_panel.highlight_block(None)
    root.update_idletasks()
    assert canvas.itemcget(rect_id1, "outline") == default_outline
    assert int(float(canvas.itemcget(rect_id1, "width"))) == default_width
    assert canvas.itemcget(rect_id2, "outline") == default_outline
    assert int(float(canvas.itemcget(rect_id2, "width"))) == default_width

# def test_timeline_panel_highlight_block(root, mocker):
#     pass 