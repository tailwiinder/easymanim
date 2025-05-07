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
        self.obj_components = {}  # Map obj_id -> (rect_id, text_id, delete_btn_id)
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

        # 2. Calculate position for the new block - use number of objects to avoid gaps
        num_blocks = len(self.obj_components)  # Count actual objects, not canvas items
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

        # 5. Create Delete Button
        delete_btn_size = 20  # Size of the delete button
        btn_x = x_end - delete_btn_size - padding
        btn_y = y_start + (block_height / 2)
        
        # Draw delete button (a circle with X)
        delete_btn_id = self.canvas.create_oval(
            btn_x - delete_btn_size/2, btn_y - delete_btn_size/2,
            btn_x + delete_btn_size/2, btn_y + delete_btn_size/2,
            fill="red",
            tags=(f"delete_btn_{obj_id}",)  # Only use delete button tag, not obj tag
        )
        
        # Add X mark inside the delete button
        x_mark_id = self.canvas.create_text(
            btn_x, btn_y,
            text="X",
            fill="white",
            font=("Arial", 10, "bold"),
            tags=(f"delete_btn_{obj_id}",)  # Only use delete button tag, not obj tag
        )

        # 6. Store mapping for all canvas items
        self.object_canvas_items[rect_id] = obj_id
        self.object_canvas_items[text_id] = obj_id
        self.object_canvas_items[delete_btn_id] = obj_id
        self.object_canvas_items[x_mark_id] = obj_id
        
        # Store all components related to this object
        self.obj_components[obj_id] = (rect_id, text_id, delete_btn_id, x_mark_id)

        # 7. Update scroll region (important for potential future scrolling)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def highlight_block(self, selected_obj_id: Optional[str]):
        """Highlight the block corresponding to selected_obj_id, deselect others."""
        if not self.canvas:
            return

        default_outline = "black"
        default_width = 1
        highlight_outline = "red"
        highlight_width = 2

        # Get unique object IDs
        unique_obj_ids = set(self.object_canvas_items.values())
        
        # Iterate through all managed object blocks
        for obj_id in unique_obj_ids:
            if obj_id in self.obj_components:
                rect_id = self.obj_components[obj_id][0]  # Get the rectangle ID
                try:
                    # Check if item still exists and is a rectangle
                    if self.canvas.type(rect_id) == "rectangle":
                        if obj_id == selected_obj_id:
                            # Apply highlight style
                            self.canvas.itemconfig(rect_id, outline=highlight_outline, width=highlight_width)
                        else:
                            # Apply default style
                            self.canvas.itemconfig(rect_id, outline=default_outline, width=default_width)
                except tk.TclError:
                    # Item might have been deleted externally? Log or ignore.
                    print(f"[TimelinePanel Warning] Could not configure item {rect_id} during highlight.")
                    continue

    def delete_block(self, obj_id: str):
        """Delete a block from the timeline."""
        if obj_id in self.obj_components:
            # Get all canvas items associated with this object
            components = self.obj_components[obj_id]
            
            # Delete all components from canvas
            for item_id in components:
                try:
                    self.canvas.delete(item_id)
                    # Remove from object_canvas_items mapping
                    if item_id in self.object_canvas_items:
                        del self.object_canvas_items[item_id]
                except tk.TclError:
                    print(f"[TimelinePanel Warning] Could not delete item {item_id}.")
            
            # Remove from obj_components mapping
            del self.obj_components[obj_id]
            
            # Reposition remaining blocks (fill the gap)
            self._reposition_blocks()
            
            # Show placeholder if no blocks left
            if not self.obj_components:
                self._draw_placeholder_text()
                
            # Notify UI manager about deletion
            # We need to be careful about this call - make sure it exists in UIManager
            try:
                # Call handle_object_deleted if it exists
                if hasattr(self.ui_manager, 'handle_object_deleted'):
                    self.ui_manager.handle_object_deleted(obj_id)
                else:
                    # Fallback - simply deselect if the object was selected
                    self.ui_manager.handle_timeline_selection(None)
                    print(f"[TimelinePanel Warning] UIManager has no handle_object_deleted method. Object {obj_id} was deleted from timeline but UIManager wasn't properly notified.")
            except Exception as e:
                print(f"[TimelinePanel Error] Failed to notify UIManager about deletion: {e}")
            
            # Update scroll region
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def _reposition_blocks(self):
        """Reposition all blocks to ensure they're stacked properly without gaps."""
        # Get all object IDs
        obj_ids = list(self.obj_components.keys())
        
        # Sort object IDs by their current Y position to maintain visual order
        obj_ids.sort(
            key=lambda obj_id: self.canvas.coords(self.obj_components[obj_id][0])[1] 
            if obj_id in self.obj_components else float('inf')
        )
        
        block_height = 30  # Same as in add_block
        padding = 5
        
        # Get canvas width for block width
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1: canvas_width = 200  # Default width if not rendered yet
        
        # Reposition each block with consistent spacing - no gaps
        for i, obj_id in enumerate(obj_ids):
            if obj_id in self.obj_components:
                components = self.obj_components[obj_id]
                rect_id, text_id, delete_btn_id, x_mark_id = components
                
                # Calculate new position - consistent spacing between blocks
                y_start = padding + i * (block_height + padding)
                x_start = padding
                x_end = canvas_width - padding
                y_end = y_start + block_height
                
                # Move rectangle
                self.canvas.coords(rect_id, x_start, y_start, x_end, y_end)
                
                # Move text
                self.canvas.coords(text_id, x_start + padding, y_start + block_height / 2)
                
                # Move delete button
                delete_btn_size = 20
                btn_x = x_end - delete_btn_size - padding
                btn_y = y_start + (block_height / 2)
                
                self.canvas.coords(delete_btn_id, 
                                  btn_x - delete_btn_size/2, btn_y - delete_btn_size/2,
                                  btn_x + delete_btn_size/2, btn_y + delete_btn_size/2)
                
                # Move X mark
                self.canvas.coords(x_mark_id, btn_x, btn_y)
        
        # Debug output to verify blocks were repositioned
        print(f"Repositioned {len(obj_ids)} blocks on timeline")

    # --- Event Handlers ---

    def _on_canvas_click(self, event):
        """Handle clicks on the timeline canvas to select objects or delete them."""
        if not self.canvas:
            return

        # Find items directly overlapping the click coordinates
        overlapping_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)

        clicked_obj_id = None
        is_delete_button = False
        
        if overlapping_items:
            # Iterate overlapping items
            for item_id in overlapping_items:
                tags = self.canvas.gettags(item_id)
                print(f"_on_canvas_click: Click near ({event.x}, {event.y}), found overlapping item {item_id} with tags: {tags}") # Debug
                
                # Check if this is a delete button
                for tag in tags:
                    if tag.startswith("delete_btn_"):
                        clicked_obj_id = tag[11:]  # Extract the ID after "delete_btn_"
                        is_delete_button = True
                        print(f"_on_canvas_click: Found delete button for obj_id: {clicked_obj_id}") # Debug
                        break
                
                if is_delete_button:
                    break  # Found delete button, no need to check other items
                
                # If not a delete button, check if it's another part of an object
                for tag in tags:
                    if tag.startswith("obj_"):
                        clicked_obj_id = tag[4:]  # Extract the ID after "obj_"
                        print(f"_on_canvas_click: Found obj_id: {clicked_obj_id} from item {item_id}") # Debug
                        break
        
        if clicked_obj_id and is_delete_button:
            # Delete the object if delete button was clicked
            print(f"Delete button clicked for object {clicked_obj_id}") # Debug
            self.delete_block(clicked_obj_id)
        elif clicked_obj_id:
            # Otherwise select the object
            print(f"Timeline item selected: obj_id={clicked_obj_id}") # Debug
            self.ui_manager.handle_timeline_selection(clicked_obj_id)
        else:
            # No item was under the cursor
            print(f"Timeline background clicked at ({event.x}, {event.y})") # Debug
            self.ui_manager.handle_timeline_selection(None)