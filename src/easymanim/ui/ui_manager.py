# src/easymanim/ui/ui_manager.py
"""Coordinates interactions between UI panels and backend logic."""

from typing import TYPE_CHECKING, Optional, Any, Dict, Union
import tkinter as tk # Tkinter types might be needed if panels are typed
import tkinter.messagebox # Import messagebox

# Avoid circular imports
if TYPE_CHECKING:
    from easymanim.logic.scene_builder import SceneBuilder
    from easymanim.interface.manim_interface import ManimInterface
    from easymanim.main_app import MainApplication
    # Add imports for Panel types if needed later, e.g.:
    # from easymanim.gui.preview_panel import PreviewPanel 
    # from easymanim.gui.timeline_panel import TimelinePanel
    # from easymanim.gui.properties_panel import PropertiesPanel

class UIManager:
    """Mediates communication between UI panels, SceneBuilder, and ManimInterface."""
    
    def __init__(self, 
                 root_app: 'MainApplication', 
                 scene_builder: 'SceneBuilder', 
                 manim_interface: 'ManimInterface'):
        """Initializes the UIManager.
        
        Args:
            root_app: The main application instance (for scheduling tasks).
            scene_builder: The instance managing scene state.
            manim_interface: The instance handling Manim execution.
        """
        self.root_app = root_app
        self.scene_builder = scene_builder
        self.manim_interface = manim_interface
        self.panels: Dict[str, Any] = {} # Store references to UI panels (mocked in tests)
        self.selected_object_id: Optional[str] = None

    def register_panel(self, name: str, panel_instance: Any):
        """Allows the MainApplication to register UI panel instances."""
        print(f"Registering panel: {name}") # Debug print
        self.panels[name] = panel_instance

    # --- Event Handling Methods (to be implemented via TDD) --- 
    
    def handle_add_object_request(self, obj_type: str):
        """Handles request to add a new object (e.g., from Toolbar button)."""
        print(f"Handling add object request: {obj_type}")
        try:
            new_id = self.scene_builder.add_object(obj_type)
            print(f"  SceneBuilder returned new ID: {new_id}")
            
            # Update Timeline Panel
            timeline_panel = self.panels.get("timeline")
            if timeline_panel:
                # Generate a label (can be refined later)
                # For now, use type and last 6 chars of ID for uniqueness
                print(f"  Updating timeline panel with: obj_id={new_id}, obj_type={obj_type}")
                # Assume add_block exists on the panel instance
                timeline_panel.add_block(new_id, obj_type) # Pass obj_type directly
            else:
                print("  Timeline panel not found!")

            # Update Status Bar
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                status_message = f"{obj_type} added (ID: {new_id})"
                print(f"  Updating status bar: {status_message}")
                # Assume set_status exists
                statusbar_panel.set_status(status_message)
            else:
                print("  Statusbar panel not found!")

            # TODO: Enable Render button if needed?

        except ValueError as e:
            # Handle case where SceneBuilder rejects object type
            print(f"[UIManager Error] Failed to add object: {e}")
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                statusbar_panel.set_status(f"Error: {e}")
            # Optionally show a messagebox error too
            # messagebox.showerror("Error", f"Failed to add object: {e}")
        except Exception as e:
            # Catch unexpected errors during the process
            print(f"[UIManager Error] Unexpected error adding object: {e}")
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                statusbar_panel.set_status(f"Error adding {obj_type}")
            # Consider logging traceback here

    def handle_timeline_selection(self, obj_id: Optional[str]):
        """Handles an object being selected or deselected in the timeline.

        Updates the properties panel accordingly.
        """
        print(f"Handling timeline selection: {obj_id}")
        self.selected_object_id = obj_id
        
        properties_panel = self.panels.get("properties")
        statusbar_panel = self.panels.get("statusbar")

        if properties_panel is None:
            print("  Properties panel not found!")
            # Optionally update status bar about missing panel
            return

        if obj_id is not None:
            # Object selected
            props = self.scene_builder.get_object_properties(obj_id)
            if props is not None:
                print(f"  Displaying properties for {obj_id}")
                properties_panel.display_properties(obj_id, props)
                if statusbar_panel:
                    statusbar_panel.set_status(f"Selected: {obj_id}")
            else:
                # ID was provided but not found in SceneBuilder (e.g., stale ID)
                print(f"  Selected object ID {obj_id} not found in SceneBuilder!")
                properties_panel.show_placeholder()
                if statusbar_panel:
                    statusbar_panel.set_status(f"Error: Object {obj_id} not found")
        else:
            # Deselection
            print("  Deselecting object, showing placeholder.")
            properties_panel.show_placeholder()
            if statusbar_panel:
                 # Using "Ready" is common for deselection/idle state
                statusbar_panel.set_status("Ready") 
        
    def handle_property_change(self, obj_id: str, prop_key: str, value: Any, axis_index: Optional[int] = None):
        """Handles a property value being changed in the Properties Panel."""
        print(f"Handling property change for {obj_id}: {prop_key} = {value}, axis_index = {axis_index}")
        try:
            self.scene_builder.update_object_property(obj_id, prop_key, value, axis_index=axis_index)
            # Update status bar
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                # Capitalize prop_key for display
                display_prop = prop_key.replace('_', ' ').capitalize()
                status_message = f"{display_prop} updated for {obj_id}"
                statusbar_panel.set_status(status_message)
        except Exception as e:
            print(f"[UIManager Error] Failed to update property {prop_key} for {obj_id}: {e}")
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                statusbar_panel.set_status(f"Error updating {prop_key}")

    def handle_animation_change(self, obj_id: str, anim_name: str):
        """Handles the animation type being changed in the Properties Panel."""
        print(f"Handling animation change for {obj_id}: {anim_name}")
        try:
            self.scene_builder.set_object_animation(obj_id, anim_name)
            # Update status bar
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                status_message = f"Animation set to '{anim_name}' for {obj_id}"
                statusbar_panel.set_status(status_message)
        except Exception as e:
            print(f"[UIManager Error] Failed to set animation for {obj_id}: {e}")
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                statusbar_panel.set_status(f"Error setting animation")

    def handle_refresh_preview_request(self):
        """Handles request to refresh the static preview image."""
        print("Handling refresh preview request")
        try:
            script_content, scene_name = self.scene_builder.generate_script('preview')
            print(f"  Generated preview script for scene: {scene_name}")
            
            preview_panel = self.panels.get("preview")
            statusbar_panel = self.panels.get("statusbar")
            
            # Update UI to show rendering state
            if preview_panel:
                preview_panel.show_rendering_state()
            if statusbar_panel:
                statusbar_panel.set_status("Rendering preview...")
            
            # Define preview quality flags
            quality_flags = ['-s', '-ql'] # Static image, low quality
            
            # Call ManimInterface to render asynchronously
            self.manim_interface.render_async(
                script_content=script_content,
                scene_name=scene_name,
                quality_flags=quality_flags,
                output_format='png',
                callback=self._preview_callback # Pass internal method as callback
            )
            print("  render_async called on ManimInterface")
        
        except Exception as e:
            print(f"[UIManager Error] Failed during refresh preview setup: {e}")
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                statusbar_panel.set_status("Error generating preview script")
            # Potentially show error to user or update preview panel state
            preview_panel = self.panels.get("preview")
            if preview_panel:
                 preview_panel.show_idle_state() # Re-enable button etc.

    def handle_render_video_request(self):
        """Handles request to render the final video.
        
        Similar to preview request, but uses 'render' script type and 'mp4' output.
        """
        print("Handling render video request")
        try:
            script_content, scene_name = self.scene_builder.generate_script('render')
            print(f"  Generated render script for scene: {scene_name}")
            
            # Get panels needed for state updates
            preview_panel = self.panels.get("preview") # May need to disable btn
            statusbar_panel = self.panels.get("statusbar")
            
            # Update UI to show rendering state (disable relevant buttons)
            # TODO: Determine which buttons *exactly* need disabling
            if preview_panel:
                # Potentially reuse show_rendering_state or have a specific one
                preview_panel.show_rendering_state() 
            if statusbar_panel:
                statusbar_panel.set_status("Rendering video...")
            
            # Define render quality flags (low quality for V1)
            quality_flags = ['-ql'] 
            
            # Call ManimInterface to render asynchronously
            self.manim_interface.render_async(
                script_content=script_content,
                scene_name=scene_name,
                quality_flags=quality_flags,
                output_format='mp4',
                callback=self._render_callback # Use the render callback
            )
            print("  render_async called on ManimInterface for MP4")
        
        except Exception as e:
            print(f"[UIManager Error] Failed during render video setup: {e}")
            statusbar_panel = self.panels.get("statusbar")
            if statusbar_panel:
                statusbar_panel.set_status("Error generating render script")
            # Reset UI state if setup fails
            preview_panel = self.panels.get("preview")
            if preview_panel:
                 preview_panel.show_idle_state() 
                 
    # --- Callback Methods (to be implemented via TDD) ---
    
    def _preview_callback(self, success: bool, result: Union[bytes, str]):
        """Callback function for ManimInterface after preview render attempt."""
        print(f"_preview_callback received: success={success}, result type={type(result)}")
        
        preview_panel = self.panels.get("preview")
        statusbar_panel = self.panels.get("statusbar")

        if success:
            if isinstance(result, bytes):
                # Success path: Display the image
                if preview_panel:
                    preview_panel.display_image(result)
                    preview_panel.show_idle_state()
                if statusbar_panel:
                    statusbar_panel.set_status("Preview updated.")
            else:
                # Should not happen for successful PNG, but handle defensively
                print(f"[UIManager Error] Preview success=True, but result was not bytes: {type(result)}")
                if preview_panel:
                    preview_panel.show_idle_state() # Still reset state
                if statusbar_panel:
                    statusbar_panel.set_status("Preview error: Invalid result type.")
        else:
            # Failure path
            error_message = str(result) # Ensure result is a string
            print(f"Preview failed: {error_message}") 
            
            # Show error dialog to the user
            tkinter.messagebox.showerror("Preview Failed", error_message)
            
            # Reset UI state
            if preview_panel:
                preview_panel.show_idle_state()
            if statusbar_panel:
                statusbar_panel.set_status("Preview failed.")
        
    def _render_callback(self, success: bool, result: Union[str, str]):
        """Callback function for ManimInterface after video render attempt."""
        print(f"_render_callback received: success={success}, result type={type(result)}")
        
        preview_panel = self.panels.get("preview") # Needed to reset state
        statusbar_panel = self.panels.get("statusbar")

        if success:
            if isinstance(result, str):
                # Success path: Show confirmation message with path
                video_path = result
                print(f"Render successful: {video_path}")
                tkinter.messagebox.showinfo("Render Complete", f"Video saved as:\n{video_path}")
                if statusbar_panel:
                    statusbar_panel.set_status(f"Video render complete: {video_path}")
            else:
                # Should not happen for successful MP4, but handle defensively
                print(f"[UIManager Error] Render success=True, but result was not str: {type(result)}")
                if statusbar_panel:
                    statusbar_panel.set_status("Render error: Invalid result type.")
        else:
            # Failure path
            error_message = str(result)
            print(f"Render failed: {error_message}") 
            tkinter.messagebox.showerror("Render Failed", error_message)
            if statusbar_panel:
                statusbar_panel.set_status("Video render failed.")
                
        # Reset UI state (e.g., re-enable buttons) regardless of success/failure
        if preview_panel:
            preview_panel.show_idle_state()
        
