import tkinter as tk
import ttkbootstrap as ttk
from typing import Optional

class TimelinePanel(ttk.Frame):
    """A panel that displays object blocks on a timeline canvas."""

    def __init__(self, parent, ui_manager):
        """Initialize the TimelinePanel.

        Args:
            parent: The parent widget.
            ui_manager: The UIManager instance to handle selections.
        """
        super().__init__(parent, padding=5)
        self.ui_manager = ui_manager
        self.canvas = None
        self.object_canvas_items = {} # Map canvas item ID -> obj_id
        self._placeholder_id = None

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        """Create the canvas and initial placeholder text."""
        # Use a standard tk.Canvas for drawing
        self.canvas = tk.Canvas(self, bg="white", bd=1, relief="sunken")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw placeholder text initially - centered
        # We need to wait until the canvas has a size to center properly,
        # so we bind to the <Configure> event.
        self._draw_placeholder_text()

    def _bind_events(self):
        """Bind events for the canvas."""
        # Redraw placeholder when canvas size changes
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # Handle clicks on the canvas
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _draw_placeholder_text(self, event=None):
        """Draw or redraw the placeholder text centered on the canvas."""
        if self.canvas is None:
            return

        # Delete previous placeholder if it exists
        if self._placeholder_id:
            self.canvas.delete(self._placeholder_id)
            self._placeholder_id = None

        # Only draw if no actual objects are present (check mapping)
        print(f"_draw_placeholder_text: Checking condition: not self.object_canvas_items = {not self.object_canvas_items}") # Debug
        if not self.object_canvas_items:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            print(f"_draw_placeholder_text: Canvas size reported = ({canvas_width}, {canvas_height})") # Debug

            # Fallback: Use configured size if reported size is invalid (e.g., 1x1 during init)
            if canvas_width <= 1:
                canvas_width = self.canvas.cget("width")
                print(f"_draw_placeholder_text: Using configured width: {canvas_width}") # Debug
            if canvas_height <= 1:
                canvas_height = self.canvas.cget("height")
                print(f"_draw_placeholder_text: Using configured height: {canvas_height}") # Debug
            
            # Ensure canvas has a valid size before drawing (convert cget result to int)
            try:
                canvas_width = int(canvas_width)
                canvas_height = int(canvas_height)
            except ValueError:
                 print("_draw_placeholder_text: Error converting configured size to int") # Debug
                 return # Cannot draw if size is not numerical

            if canvas_width > 1 and canvas_height > 1:
                placeholder_text = "Timeline - Add objects using the toolbar"
                # Tag the item so the test can find it
                self._placeholder_id = self.canvas.create_text(
                    canvas_width / 2,
                    canvas_height / 2,
                    text=placeholder_text,
                    fill="grey",
                    tags=("placeholder_text",) # Assign tag
                )
                print(f"_draw_placeholder_text: Created placeholder with ID {self._placeholder_id}") # Debug
            else:
                print("_draw_placeholder_text: Condition (width > 1 and height > 1) failed.") # Debug
        else:
            print("_draw_placeholder_text: Condition (not self.object_canvas_items) failed.") # Debug

    def _on_canvas_configure(self, event):
        """Handle canvas resize events, redraw placeholder if needed."""
        # Redraw placeholder AND existing blocks if needed (e.g., width changes)
        self._draw_placeholder_text()
        # TODO: Consider redrawing/adjusting existing blocks if canvas width changes significantly

    # --- Public Methods (to be called by UIManager) ---

    def add_block(self, obj_id: str, obj_type: str):
        """Add a visual block representing an object to the timeline."""
        if self.canvas is None:
            return # Should not happen if initialized correctly

        # 1. Remove placeholder if it exists
        if self._placeholder_id:
            self.canvas.delete(self._placeholder_id)
            self._placeholder_id = None

        # 2. Calculate position for the new block
        num_blocks = len(self.object_canvas_items)
        block_height = 30  # Configurable height for each block
        padding = 5
        y_start = padding + num_blocks * (block_height + padding)
        x_start = padding
        # Use current canvas width for the block width
        # Note: might need adjustments if canvas resizes later
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1: canvas_width = 200 # Default width if not rendered yet
        x_end = canvas_width - padding
        y_end = y_start + block_height

        # Define tags for easy finding/grouping
        obj_tag = f"obj_{obj_id}"
        block_tag = "timeline_block" # General tag for all blocks

        # 3. Draw Rectangle
        rect_id = self.canvas.create_rectangle(
            x_start, y_start, x_end, y_end,
            fill="lightblue",        # Default fill
            activefill="skyblue",    # Fill when mouse is over
            outline="black",
            tags=(obj_tag, block_tag) # Apply both tags
        )

        # 4. Draw Text inside the rectangle
        text_content = f"{obj_type}: {obj_id}"
        text_id = self.canvas.create_text(
            x_start + padding, y_start + block_height / 2,
            anchor=tk.W,             # Anchor text to the West (left)
            text=text_content,
            tags=(obj_tag, block_tag) # Apply both tags
        )

        # 5. Store mapping (using rectangle ID as the primary reference)
        self.object_canvas_items[rect_id] = obj_id
        # Optionally store text_id too if needed later, maybe map obj_id -> (rect_id, text_id)

        # 6. Update scroll region (important for potential future scrolling)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def highlight_block(self, selected_obj_id: Optional[str]):
        """Highlight the block corresponding to selected_obj_id, deselect others."""
        if not self.canvas:
            return

        default_outline = "black"
        default_width = 1
        highlight_outline = "red"
        highlight_width = 2

        # Iterate through all managed object blocks
        for rect_id, obj_id in self.object_canvas_items.items():
            try:
                # Check if item still exists and is a rectangle
                if self.canvas.type(rect_id) == "rectangle":
                    if obj_id == selected_obj_id:
                        # Apply highlight style
                        self.canvas.itemconfig(rect_id, outline=highlight_outline, width=highlight_width)
                        # Optional: Raise the selected item to the top
                        # self.canvas.tag_raise(rect_id)
                        # if text_id: self.canvas.tag_raise(text_id) # Need text_id mapping too
                    else:
                        # Apply default style
                        self.canvas.itemconfig(rect_id, outline=default_outline, width=default_width)
            except tk.TclError:
                # Item might have been deleted externally? Log or ignore.
                print(f"[TimelinePanel Warning] Could not configure item {rect_id} during highlight.")
                continue

    # --- Event Handlers ---

    def _on_canvas_click(self, event):
        """Handle clicks on the timeline canvas to select objects."""
        if not self.canvas:
            return

        # Find items directly overlapping the click coordinates
        overlapping_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)

        selected_obj_id = None
        if overlapping_items:
            # Iterate overlapping items (usually just one, but check just in case)
            for item_id in overlapping_items:
                tags = self.canvas.gettags(item_id)
                print(f"_on_canvas_click: Click near ({event.x}, {event.y}), found overlapping item {item_id} with tags: {tags}") # Debug
                # Find the object ID from the specific object tag
                for tag in tags:
                    print(f"_on_canvas_click: Checking tag: {tag}") # Debug
                    if tag.startswith("obj_"):
                        selected_obj_id = tag[4:] # Extract the ID after "obj_"
                        print(f"_on_canvas_click: Found obj_id: {selected_obj_id} from item {item_id}") # Debug
                        break # Found the relevant tag for this item
                if selected_obj_id:
                    break # Found the object ID from one of the overlapping items

        if selected_obj_id:
            # Found an object block (rect or text) under the cursor
            print(f"Timeline item {item_id} clicked, selecting obj_id={selected_obj_id}") # Debug
            self.ui_manager.handle_timeline_selection(selected_obj_id)
        else:
            # No item with an "obj_" tag was directly under the cursor
            print(f"Timeline background clicked at ({event.x}, {event.y})") # Debug
            self.ui_manager.handle_timeline_selection(None) 