import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import io
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import at runtime
    from ..ui.ui_manager import UIManager

class PreviewPanel(ttk.Frame):
    """Panel to display the Manim preview image and refresh button."""

    def __init__(self, parent, ui_manager: 'UIManager'):
        """Initialize the PreviewPanel.

        Args:
            parent: The parent widget.
            ui_manager: The UIManager instance.
        """
        super().__init__(parent, padding=5)
        self.ui_manager = ui_manager
        self.canvas: Optional[tk.Canvas] = None
        self.refresh_button: Optional[ttk.Button] = None
        self._photo_image = None # Keep reference to avoid GC
        self._image_on_canvas = None
        self._placeholder_id = None

        self._create_widgets()
        self._bind_events()
        self.show_idle_state() # Start in idle state

    def _create_widgets(self):
        """Create canvas and button widgets."""
        # Configure grid
        self.rowconfigure(0, weight=1) # Canvas row expands
        self.columnconfigure(0, weight=1) # Canvas col expands
        
        self.canvas = tk.Canvas(self, bg="gray85", bd=1, relief="sunken")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.refresh_button = ttk.Button(
            self,
            text="Refresh Preview",
            # command=self.ui_manager.handle_refresh_preview_request # Bind in _bind_events
            bootstyle="success"
        )
        self.refresh_button.grid(row=1, column=0, pady=(5, 0), sticky="ew")

    def _bind_events(self):
        """Bind events."""
        if self.refresh_button:
            self.refresh_button.config(command=self.ui_manager.handle_refresh_preview_request)
        # Bind configure to redraw placeholder like in Timeline
        if self.canvas:
             self.canvas.bind("<Configure>", self._draw_placeholder)
             
    def _draw_placeholder(self, event=None):
        """Draw placeholder text if no image is present."""
        if not self.canvas:
            return
            
        # If an image exists, don't draw placeholder
        if self._image_on_canvas:
            if self._placeholder_id:
                 self.canvas.delete(self._placeholder_id)
                 self._placeholder_id = None
            return
        
        # Delete previous placeholder if switching back
        if self._placeholder_id:
             self.canvas.delete(self._placeholder_id)
             self._placeholder_id = None
             
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Fallback to configured size if needed
        if canvas_width <= 1: canvas_width = self.canvas.cget("width")
        if canvas_height <= 1: canvas_height = self.canvas.cget("height")
        try:
            canvas_width = int(canvas_width)
            canvas_height = int(canvas_height)
        except ValueError:
             return # Cannot draw
             
        if canvas_width > 1 and canvas_height > 1:
            placeholder_text = "Click 'Refresh Preview' to see output"
            self._placeholder_id = self.canvas.create_text(
                canvas_width / 2, canvas_height / 2,
                text=placeholder_text,
                fill="grey50",
                tags=("placeholder",) # Tag for finding in tests
            )

    # --- Public Methods (Called by UIManager) ---

    def display_image(self, image_bytes: bytes):
        """Display the rendered preview image on the canvas."""
        if not self.canvas:
            return
            
        # Clear previous items (placeholder, rendering text, or old image)
        self.canvas.delete("placeholder")
        self.canvas.delete("rendering_text")
        if self._image_on_canvas:
             self.canvas.delete(self._image_on_canvas)
             self._image_on_canvas = None
        if self._placeholder_id:
             self._placeholder_id = None # Placeholder already deleted by tag

        try:
            # Load image data
            image = Image.open(io.BytesIO(image_bytes))
            self._photo_image = ImageTk.PhotoImage(image) # Keep reference!

            # Get canvas center coordinates
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            # Fallback to configured size if needed
            if canvas_width <= 1: canvas_width = self.canvas.cget("width")
            if canvas_height <= 1: canvas_height = self.canvas.cget("height")
            try:
                 canvas_width = int(canvas_width)
                 canvas_height = int(canvas_height)
            except ValueError:
                 canvas_width, canvas_height = 300, 200 # Default if conversion fails
                 
            center_x = canvas_width / 2
            center_y = canvas_height / 2
            
            # Create image on canvas
            self._image_on_canvas = self.canvas.create_image(
                center_x,
                center_y,
                image=self._photo_image,
                tags=("preview_image",)
            )
            print(f"display_image: Displayed image with ID {self._image_on_canvas}") # Debug

        except Exception as e:
            print(f"[PreviewPanel Error] Failed to display image: {e}")
            # Optionally show an error message on the canvas
            self._draw_placeholder() # Revert to placeholder on error

    def show_rendering_state(self):
        """Update UI to show preview is rendering (disable button, update text)."""
        if self.refresh_button:
            self.refresh_button.config(state=tk.DISABLED)
        if self.canvas:
            # Clear previous image/placeholder
            if self._image_on_canvas:
                self.canvas.delete(self._image_on_canvas)
                self._image_on_canvas = None
            if self._placeholder_id:
                self.canvas.delete(self._placeholder_id)
                self._placeholder_id = None
            
            # Draw "Rendering..." text
            # TODO: Add a dedicated ID for rendering text if needed
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            # Use fallback size similar to _draw_placeholder
            if canvas_width <= 1: canvas_width = self.canvas.cget("width")
            if canvas_height <= 1: canvas_height = self.canvas.cget("height")
            try:
                canvas_width = int(canvas_width)
                canvas_height = int(canvas_height)
                if canvas_width > 1 and canvas_height > 1:
                    # Ensure no duplicate rendering text exists
                    self.canvas.delete("rendering_text") 
                    self.canvas.create_text(
                        canvas_width / 2, canvas_height / 2,
                        text="Rendering Preview...",
                        fill="black",
                        tags=("rendering_text",) # Tag for finding/deleting
                    )
            except ValueError:
                 pass # Cannot draw

    def show_idle_state(self):
        """Update UI to show idle state (enable button, show placeholder/image)."""
        if self.refresh_button:
             self.refresh_button.config(state=tk.NORMAL)
        
        # Remove rendering text if it exists
        if self.canvas:
             self.canvas.delete("rendering_text")
             
        # Decide whether to draw placeholder or keep existing image
        if self._image_on_canvas:
             pass # Keep image
        else:
             self._draw_placeholder() 