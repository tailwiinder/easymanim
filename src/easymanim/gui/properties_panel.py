import tkinter as tk
import ttkbootstrap as ttk
from tkinter.colorchooser import askcolor
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import at runtime, only needed for type hinting
    from ..ui.ui_manager import UIManager

class PropertiesPanel(ttk.Frame):
    """A panel to display and edit properties of the selected object."""

    # Store default properties centrally if they become complex
    DEFAULT_PROPS = {
        'position': (0.0, 0.0, 0.0),
        'color': '#FFFFFF',
        'opacity': 1.0,
        # Object-specific defaults will be merged
    }
    OBJECT_DEFAULTS = {
        'Circle': {'radius': 0.5},
        'Square': {'side_length': 1.0},
        'Text': {'text': 'Hello', 'font_size': 48}
    }
    # Available animations (could be dynamically fetched later)
    ANIMATIONS = ["None", "FadeIn", "GrowFromCenter", "Write"] # Example

    def __init__(self, parent, ui_manager: 'UIManager'):
        """Initialize the PropertiesPanel.

        Args:
            parent: The parent widget.
            ui_manager: The UIManager instance.
        """
        super().__init__(parent, padding=10)
        self.ui_manager = ui_manager
        self.current_object_id: Optional[str] = None
        self.widgets = {} # Store property widgets for easy access/clearing
        self._placeholder_label = None

        # Create initial placeholder
        self.show_placeholder()

    def show_placeholder(self):
        """Clear existing widgets and display the placeholder message."""
        self._clear_widgets()
        self._placeholder_label = ttk.Label(
            self,
            text="Select an object to edit properties.",
            anchor=tk.CENTER
        )
        self._placeholder_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def _clear_widgets(self):
        """Destroy all current property widgets and the placeholder."""
        self.rowconfigure(0, weight=0)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0) # Reset column 1 used by display_properties

        # Destroy ALL direct children widgets
        for child in self.winfo_children():
            child.destroy()
            
        # Reset internal references
        self.widgets = {}
        # if self._placeholder_label:
        #     self._placeholder_label.destroy() # Already destroyed by loop above
        self._placeholder_label = None

    # --- Public Methods (Called by UIManager) ---

    def display_properties(self, obj_id: str, props: dict):
        """Display the properties for the given object."""
        self.current_object_id = obj_id
        self._clear_widgets() # Remove placeholder or previous properties

        # Define the order, ensuring keys match SceneBuilder's 'properties' dict
        # 'type' is usually not edited here. 'pos_x', 'pos_y', 'pos_z' are individual.
        prop_order = [
            'text_content', 'font_size', 'radius', 'side_length', 
            'pos_x', 'pos_y', 'pos_z', 
            'fill_color', 'opacity', # opacity is fill_opacity
            'stroke_color', 'stroke_width', 'stroke_opacity',
            'animation'
        ]

        row = 0
        # Create Label and Widget for each property
        # First, iterate defined order
        for key in prop_order:
            if key in props:
                value = props[key]
                self._create_property_widget(key, value, row)
                row += 1
        
        # Second, iterate any remaining props not in prop_order (optional, for robustness)
        # for key, value in props.items():
        # if key not in prop_order and key != 'type': # Avoid re-creating or showing 'type'
        # self._create_property_widget(key, value, row)
        # row += 1

        # Configure column weights if using grid
        self.columnconfigure(1, weight=1)

    def _create_property_widget(self, key: str, value: Any, row: int):
        """Helper to create and grid a label and appropriate widget for a property."""
        if key == 'type':
            return

        display_key_name = key.replace('_', ' ').capitalize()
        if key == 'fill_color':
            display_key_name = 'Fill Color'
        elif key == 'opacity':
            display_key_name = 'Fill Opacity'
        elif key == 'stroke_color':
            display_key_name = 'Stroke Color'
        elif key == 'stroke_width':
            display_key_name = 'Stroke Width'
        elif key == 'stroke_opacity':
            display_key_name = 'Stroke Opacity'
        
        label = ttk.Label(self, text=f"{display_key_name}:")
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)

        widget = None
        if key == 'fill_color' or key == 'stroke_color': 
            widget = self._create_color_picker(key, str(value))
            widget.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=2)
        elif key == 'animation':
            widget = self._create_animation_dropdown(key, str(value))
            widget.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=2)
        elif key == 'text_content':
             widget = self._create_entry(key, value, is_text=True)
             widget.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=2)
        # Default for numerical entries
        elif key in ['pos_x', 'pos_y', 'pos_z', 'radius', 'side_length', 'opacity', 'font_size', 'stroke_width', 'stroke_opacity']:
            # For shapes, stroke_width should be editable. For Text, it might not be present in props from SceneBuilder.
            # We should only create entry if key is actually in props (checked by caller display_properties)
            widget = self._create_entry(key, value)
            widget.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=2)
        else:
            # Fallback for any other properties, display as non-editable text for now
            widget = ttk.Label(self, text=str(value))
            widget.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=2)
            self.widgets[key] = widget # Store even if non-editable

    # --- Widget Creation Helpers (Called by display_properties) ---

    def _create_entry(self, key: str, value: Any, is_text: bool = False):
        """Helper to create a validated ttk.Entry widget."""
        entry = ttk.Entry(self)
        entry.insert(0, str(value))
        entry._property_key = key # Store property name for callbacks
        self.widgets[key] = entry

        if not is_text:
            # Register the validation command
            vcmd = (self.register(self._validate_float), '%P') # %P is value_if_allowed
            entry.config(validate='key', validatecommand=vcmd) # Validate on each key press
            # Bind FocusOut and Return to the general property change handler
            entry.bind("<FocusOut>", lambda e, k=key: self._on_property_changed(e, k))
            entry.bind("<Return>", lambda e, k=key: self._on_property_changed(e, k))
        else:
            # Bind text entry changes too
            entry.bind("<FocusOut>", lambda e, k=key: self._on_property_changed(e, k))
            entry.bind("<Return>", lambda e, k=key: self._on_property_changed(e, k))

        return entry

    def _create_color_picker(self, key: str, value: str):
        """Helper to create a color picker button and swatch."""
        color_frame = ttk.Frame(self)
        
        # Color Swatch (Label with background color)
        swatch = ttk.Label(color_frame, text="      ", background=value, relief="sunken", borderwidth=1)
        swatch.pack(side=tk.LEFT, padx=5)

        # Button to open color picker
        button = ttk.Button(color_frame, text="Choose Color...",
                           command=lambda k=key, s=swatch: self._on_pick_color(k, s))
        button.pack(side=tk.LEFT)
        
        button._property_key = key # Store property name
        self.widgets[key] = button # Or maybe store the frame?
        # Store swatch separately if needed for update
        self.widgets[f"{key}_swatch"] = swatch 

        return color_frame

    def _create_animation_dropdown(self, key: str, value: str):
        """Helper to create an animation selection Combobox."""
        combo = ttk.Combobox(self, values=self.ANIMATIONS, state="readonly")
        combo.set(value if value in self.ANIMATIONS else self.ANIMATIONS[0]) # Set current or default
        combo._property_key = key
        self.widgets[key] = combo

        # Binding for when a selection is made (for Phase 2: Editing)
        combo.bind("<<ComboboxSelected>>", lambda e, k=key: self._on_animation_selected(e, k))
        return combo

    # --- Validation and Event Handlers ---

    def _validate_float(self, value_if_allowed: str) -> bool:
        """Validation command for float entries."""
        if not value_if_allowed:
            return True # Allow empty entry
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False
        
    def _on_property_changed(self, event, key: str, is_pos: bool = False, axis: Optional[int] = None):
        """Handle Entry widget update (FocusOut, Return key)."""
        widget = event.widget
        # Check if widget still exists (it might have been destroyed by a quick subsequent selection)
        if not widget.winfo_exists():
            return
                
        new_value_str = widget.get()
        print(f"_on_property_changed: key={key}, axis={axis}, value='{new_value_str}'") # Debug

        if self.current_object_id is None:
            print("_on_property_changed: No object selected.") # Debug
            return

        try:
            if is_pos:
                # Position needs special handling for tuple update
                new_value = float(new_value_str)
                # Get current position tuple from UI manager or SceneBuilder?
                # For now, assume we pass axis and value separately
                self.ui_manager.handle_property_change(self.current_object_id, key, new_value, axis_index=axis)
            elif key in ['radius', 'side_length', 'opacity', 'font_size', 'pos_x', 'pos_y', 'pos_z', 'stroke_width', 'stroke_opacity']:
                new_value = float(new_value_str) # Convert to float
                self.ui_manager.handle_property_change(self.current_object_id, key, new_value)
            elif key == 'text_content' or key == 'animation': # Handle animation as string
                new_value = new_value_str # Text/Animation is already a string
                # For animation, _on_animation_selected handles UIManager call for Combobox
                # This branch for _on_property_changed would only be relevant if animation was an Entry
                if key == 'text_content':
                    self.ui_manager.handle_property_change(self.current_object_id, key, new_value)
            elif key == 'fill_color' or key == 'stroke_color': # For color picker, _on_pick_color handles the UIManager call
                pass # Handled by _on_pick_color
            else:
                # Fallback? Or should only known keys trigger this?
                print(f"_on_property_changed: Unknown key type '{key}'")
                return # Don't call UIManager for unknown keys

        except ValueError:
            print(f"_on_property_changed: Invalid value '{new_value_str}' for key '{key}'. Update aborted.")
            # Optionally revert the widget to the last known good value
            pass 

    def _on_pick_color(self, key: str, swatch_widget: ttk.Label):
        """Handle the color picker button click."""
        # key argument here should consistently be what SceneBuilder expects, e.g., 'fill_color'
        if self.current_object_id is None:
            print("_on_pick_color: No object selected.") # Debug
            return

        # Get current color to set as initialcolor in askcolor dialog
        current_color = "#FFFFFF" # Default
        # Assuming color is stored in props; SceneBuilder would be the source of truth.
        # For now, try to get it from the swatch if available
        try:
            current_color = swatch_widget.cget("background")
        except tk.TclError: # Widget might not exist or prop not set
            pass

        new_color_tuple = askcolor(initialcolor=current_color, title="Choose Color")
        if new_color_tuple and new_color_tuple[1]:  # Check if a color was chosen (result is tuple (rgb, hex))
            new_color_hex = new_color_tuple[1]
            print(f"_on_pick_color: New color selected: {new_color_hex} for key {key}") # Debug
            swatch_widget.config(background=new_color_hex)
            # Notify UIManager (for Phase 2: Editing)
            self.ui_manager.handle_property_change(self.current_object_id, key, new_color_hex)

    def _on_animation_selected(self, event, key: str):
        """Handle Combobox selection change for animation."""
        # key argument here should be 'animation'
        widget = event.widget
        new_value = widget.get()
        print(f"_on_animation_selected: key={key}, value='{new_value}'") # Debug

        if self.current_object_id is None:
            print("_on_animation_selected: No object selected.") # Debug
            return

        # Notify UIManager (for Phase 2: Editing)
        self.ui_manager.handle_animation_change(self.current_object_id, new_value)