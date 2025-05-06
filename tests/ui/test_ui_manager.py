# tests/ui/test_ui_manager.py
"""Tests for the UIManager class."""

import pytest
from unittest.mock import MagicMock, patch
import tkinter.messagebox # Import messagebox for mocking

# Imports needed for type hinting and instantiation
from easymanim.ui.ui_manager import UIManager
# Import the classes to be mocked
from easymanim.logic.scene_builder import SceneBuilder 
from easymanim.interface.manim_interface import ManimInterface
# Define a dummy MainApplication again (or import if it exists later)
class MockMainApplication:
    def schedule_task(self, callback, *args):
        # Simplest mock: call immediately for testing flow
        # More complex tests might check args or delay
        callback(*args)

# REMOVE Dummy Panel classes - Use MagicMock directly in fixture
# class MockTimelinePanel: ... 
# class MockPropertiesPanel: ...
# class MockPreviewPanel: ...
# class MockStatusBarPanel: ...

# --- Test Setup Fixture (Optional but helpful) ---
@pytest.fixture
def ui_manager_fixture():
    """Provides a UIManager instance with mocked dependencies."""
    mock_root_app = MockMainApplication()
    mock_scene_builder = MagicMock(spec=SceneBuilder)
    mock_manim_interface = MagicMock(spec=ManimInterface)
    
    ui_manager = UIManager(mock_root_app, mock_scene_builder, mock_manim_interface)
    
    # Create and register mock panels using MagicMock
    mock_timeline = MagicMock() # Removed spec=MockTimelinePanel
    mock_properties = MagicMock() # Removed spec=MockPropertiesPanel
    mock_preview = MagicMock() # Removed spec=MockPreviewPanel
    mock_statusbar = MagicMock() # Removed spec=MockStatusBarPanel
    
    ui_manager.register_panel("timeline", mock_timeline)
    ui_manager.register_panel("properties", mock_properties)
    ui_manager.register_panel("preview", mock_preview)
    ui_manager.register_panel("statusbar", mock_statusbar)
    
    # Return tuple: manager and mocks for assertion checks
    return ui_manager, mock_root_app, mock_scene_builder, mock_manim_interface, { 
        "timeline": mock_timeline, 
        "properties": mock_properties,
        "preview": mock_preview,
        "statusbar": mock_statusbar
    }

# --- Test Class --- 
class TestUIManager:
    """Test suite for the UIManager."""

    def test_init_and_register(self, ui_manager_fixture):
        """Test basic initialization and panel registration."""
        ui_manager, root_app, scene_builder, manim_interface, panels = ui_manager_fixture
        assert ui_manager.root_app is root_app
        assert ui_manager.scene_builder is scene_builder
        assert ui_manager.manim_interface is manim_interface
        assert ui_manager.selected_object_id is None
        assert len(ui_manager.panels) == 4 # Check all panels were registered
        assert ui_manager.panels["timeline"] is panels["timeline"]

    def test_handle_add_object_calls_scenebuilder_and_timeline_panel(self, ui_manager_fixture):
        """Verify handle_add_object_request calls SceneBuilder and updates TimelinePanel.
        Red Step: Requires handle_add_object_request implementation.
        """
        ui_manager, _, mock_scene_builder, _, panels = ui_manager_fixture
        mock_timeline = panels['timeline']
        mock_statusbar = panels['statusbar'] # Get status bar mock too
        
        # Configure mock SceneBuilder to return a dummy ID
        dummy_id = "circle_test123"
        mock_scene_builder.add_object.return_value = dummy_id
        # Spy on the add_block method of the mock TimelinePanel
        mock_timeline.add_block = MagicMock()
        # Spy on status bar
        mock_statusbar.set_status = MagicMock()

        # Call the handler
        object_type = "Circle"
        ui_manager.handle_add_object_request(object_type)

        # Assert SceneBuilder was called
        mock_scene_builder.add_object.assert_called_once_with(object_type)

        # Assert TimelinePanel was updated 
        # For now, assume a simple label format (this might change)
        # The exact label generation isn't the focus here, just the call.
        mock_timeline.add_block.assert_called_once()
        # Check the first argument passed to add_block was the id
        assert mock_timeline.add_block.call_args[0][0] == dummy_id 
        # We can refine the label check later if needed
        assert isinstance(mock_timeline.add_block.call_args[0][1], str) 

        # Assert Status bar was updated (optional but good practice)
        mock_statusbar.set_status.assert_called()

    def test_handle_timeline_selection_updates_properties_panel(self, ui_manager_fixture):
        """Verify timeline selection updates internal state and PropertiesPanel.
        Red Step: Requires handle_timeline_selection implementation.
        """
        ui_manager, _, mock_scene_builder, _, panels = ui_manager_fixture
        mock_properties = panels['properties']
        mock_statusbar = panels['statusbar']
        
        # --- Mock setup --- 
        dummy_id_1 = "circle_sel123"
        dummy_props_1 = {'radius': 1.0, 'fill_color': '#FFFFFF'}
        dummy_id_2 = "square_sel456"
        dummy_props_2 = {'side_length': 2.0, 'fill_color': '#00FF00'}
        
        # Configure SceneBuilder mock
        def get_props_side_effect(obj_id):
            if obj_id == dummy_id_1: return dummy_props_1
            if obj_id == dummy_id_2: return dummy_props_2
            return None
        mock_scene_builder.get_object_properties.side_effect = get_props_side_effect
        
        # Spy on PropertiesPanel methods
        mock_properties.display_properties = MagicMock()
        mock_properties.show_placeholder = MagicMock()
        mock_statusbar.set_status = MagicMock() # Reset mock for this test

        # --- Test Selection 1 --- 
        ui_manager.handle_timeline_selection(dummy_id_1)
        
        assert ui_manager.selected_object_id == dummy_id_1
        mock_scene_builder.get_object_properties.assert_called_with(dummy_id_1)
        mock_properties.display_properties.assert_called_once_with(dummy_id_1, dummy_props_1)
        mock_properties.show_placeholder.assert_not_called()
        mock_statusbar.set_status.assert_called() # Check status updated
        status_call_args = mock_statusbar.set_status.call_args[0]
        assert dummy_id_1 in status_call_args[0] # Status includes ID
        
        # Reset mocks for next check
        mock_properties.display_properties.reset_mock()
        mock_statusbar.set_status.reset_mock()
        mock_scene_builder.get_object_properties.reset_mock()

        # --- Test Selection 2 --- 
        ui_manager.handle_timeline_selection(dummy_id_2)
        
        assert ui_manager.selected_object_id == dummy_id_2
        mock_scene_builder.get_object_properties.assert_called_with(dummy_id_2)
        mock_properties.display_properties.assert_called_once_with(dummy_id_2, dummy_props_2)
        mock_properties.show_placeholder.assert_not_called()
        mock_statusbar.set_status.assert_called()
        status_call_args = mock_statusbar.set_status.call_args[0]
        assert dummy_id_2 in status_call_args[0]
        
        # Reset mocks
        mock_properties.display_properties.reset_mock()
        mock_statusbar.set_status.reset_mock()
        mock_scene_builder.get_object_properties.reset_mock()

        # --- Test Deselection --- 
        ui_manager.handle_timeline_selection(None)
        
        assert ui_manager.selected_object_id is None
        mock_scene_builder.get_object_properties.assert_not_called() # Shouldn't fetch props
        mock_properties.display_properties.assert_not_called()
        mock_properties.show_placeholder.assert_called_once()
        mock_statusbar.set_status.assert_called()
        status_call_args = mock_statusbar.set_status.call_args[0]
        assert "Deselected" in status_call_args[0] or "Ready" in status_call_args[0] # Status cleared

    def test_handle_property_change_updates_scenebuilder(self, ui_manager_fixture):
        """Verify property/animation changes call SceneBuilder update methods.
        Red Step: Requires handle_property_change and handle_animation_change.
        """
        ui_manager, _, mock_scene_builder, _, panels = ui_manager_fixture
        mock_statusbar = panels['statusbar']
        mock_statusbar.set_status = MagicMock() # Spy on status bar
        
        # --- Test Property Change --- 
        dummy_id = "circle_prop123"
        prop_key = "pos_x"
        new_value = -3.14
        
        # Assume object is selected (though not strictly needed for this call)
        ui_manager.selected_object_id = dummy_id 
        
        # Call the handler for a regular property
        ui_manager.handle_property_change(dummy_id, prop_key, new_value)
        
        # Assert SceneBuilder was called correctly
        mock_scene_builder.update_object_property.assert_called_once_with(
            dummy_id, prop_key, new_value
        )
        mock_scene_builder.set_object_animation.assert_not_called() # Ensure wrong method wasn't called
        mock_statusbar.set_status.assert_called() # Check status updated
        
        # Reset mocks
        mock_scene_builder.reset_mock()
        mock_statusbar.reset_mock()

        # --- Test Animation Change --- 
        anim_prop_key = "animation" # Although we have a dedicated handler
        new_anim = "FadeIn"

        # Call the dedicated handler for animation
        ui_manager.handle_animation_change(dummy_id, new_anim)
        
        # Assert SceneBuilder was called correctly
        mock_scene_builder.set_object_animation.assert_called_once_with(dummy_id, new_anim)
        mock_scene_builder.update_object_property.assert_not_called()
        mock_statusbar.set_status.assert_called() # Check status updated

    def test_handle_refresh_preview_calls_scenebuilder_and_maniminterface(self, ui_manager_fixture):
        """Verify refresh preview request coordinates script generation and render call.
        Red Step: Requires handle_refresh_preview_request implementation.
        """
        ui_manager, _, mock_scene_builder, mock_manim_interface, panels = ui_manager_fixture
        mock_preview = panels['preview']
        mock_statusbar = panels['statusbar']
        
        # --- Mock setup --- 
        dummy_script = "# Preview Script"
        dummy_scene = "PreviewScene"
        mock_scene_builder.generate_script.return_value = (dummy_script, dummy_scene)
        
        # Spy on methods
        mock_preview.show_rendering_state = MagicMock()
        mock_manim_interface.render_async = MagicMock()
        mock_statusbar.set_status = MagicMock()
        
        # --- Call handler --- 
        ui_manager.handle_refresh_preview_request()
        
        # --- Assertions --- 
        # 1. SceneBuilder called correctly
        mock_scene_builder.generate_script.assert_called_once_with('preview')
        
        # 2. PreviewPanel state updated
        mock_preview.show_rendering_state.assert_called_once()
        mock_statusbar.set_status.assert_called() # Check status updated

        # 3. ManimInterface called correctly
        mock_manim_interface.render_async.assert_called_once()
        call_args, call_kwargs = mock_manim_interface.render_async.call_args
        
        assert call_kwargs.get('script_content') == dummy_script
        assert call_kwargs.get('scene_name') == dummy_scene
        # Check for preview flags (as defined in architecture/checklist)
        assert call_kwargs.get('quality_flags') == ['-s', '-ql'] 
        assert call_kwargs.get('output_format') == 'png'
        # Check that the callback passed is the UIManager's internal method
        assert call_kwargs.get('callback') == ui_manager._preview_callback

    def test_preview_callback_success_updates_panel(self, ui_manager_fixture):
        """Verify _preview_callback updates panel correctly on success.
        Red Step: Requires implementation of _preview_callback success path.
        """
        ui_manager, _, _, _, panels = ui_manager_fixture
        mock_preview = panels['preview']
        mock_statusbar = panels['statusbar']
        
        # Spy on panel methods
        mock_preview.display_image = MagicMock()
        mock_preview.show_idle_state = MagicMock()
        mock_statusbar.set_status = MagicMock()
        
        dummy_image_bytes = b'imagedata'
        
        # Call the callback directly, simulating success
        ui_manager._preview_callback(True, dummy_image_bytes)
        
        # Assert PreviewPanel methods called
        mock_preview.display_image.assert_called_once_with(dummy_image_bytes)
        mock_preview.show_idle_state.assert_called_once()
        
        # Assert Statusbar updated
        mock_statusbar.set_status.assert_called_once()
        status_message = mock_statusbar.set_status.call_args[0][0]
        assert "Preview updated" in status_message or "success" in status_message.lower()

    @patch('tkinter.messagebox.showerror') # Mock the showerror function
    def test_preview_callback_failure_shows_error(self, mock_showerror, ui_manager_fixture):
        """Verify _preview_callback handles failure correctly.
        Red Step: Requires implementation of _preview_callback failure path.
        """
        ui_manager, _, _, _, panels = ui_manager_fixture
        mock_preview = panels['preview']
        mock_statusbar = panels['statusbar']
        
        # Spy on panel methods
        mock_preview.show_idle_state = MagicMock()
        mock_statusbar.set_status = MagicMock()
        
        dummy_error_message = "Manim failed spectacularly!"
        
        # Call the callback directly, simulating failure
        ui_manager._preview_callback(False, dummy_error_message)
        
        # Assert messagebox.showerror was called
        mock_showerror.assert_called_once()
        # Check title and message passed to showerror
        assert "Preview Failed" in mock_showerror.call_args[0][0] # Title check
        assert dummy_error_message in mock_showerror.call_args[0][1] # Message check
        
        # Assert PreviewPanel state reset
        mock_preview.show_idle_state.assert_called_once()
        
        # Assert Statusbar updated
        mock_statusbar.set_status.assert_called_once()
        status_message = mock_statusbar.set_status.call_args[0][0]
        assert "Preview failed" in status_message or "error" in status_message.lower()

    # --- Render Request and Callback Tests --- 

    def test_handle_render_video_request(self, ui_manager_fixture):
        """Verify render request coordinates script generation and render call.
        Red Step: Requires handle_render_video_request implementation.
        """
        ui_manager, _, mock_scene_builder, mock_manim_interface, panels = ui_manager_fixture
        mock_preview = panels['preview'] # May need to disable refresh btn
        mock_statusbar = panels['statusbar']
        
        dummy_script = "# Render Script"
        dummy_scene = "EasyManimScene"
        mock_scene_builder.generate_script.return_value = (dummy_script, dummy_scene)
        
        # Spy on methods
        # Assume Render button would be disabled elsewhere, potentially statusbar update is enough
        mock_manim_interface.render_async = MagicMock()
        mock_statusbar.set_status = MagicMock()
        
        ui_manager.handle_render_video_request()
        
        mock_scene_builder.generate_script.assert_called_once_with('render')
        mock_statusbar.set_status.assert_called() # Check status updated (e.g., "Rendering video...")
        status_message = mock_statusbar.set_status.call_args[0][0]
        assert "Rendering video" in status_message
        
        mock_manim_interface.render_async.assert_called_once()
        call_args, call_kwargs = mock_manim_interface.render_async.call_args
        assert call_kwargs.get('script_content') == dummy_script
        assert call_kwargs.get('scene_name') == dummy_scene
        assert call_kwargs.get('quality_flags') == ['-ql'] # Render flags 
        assert call_kwargs.get('output_format') == 'mp4'
        assert call_kwargs.get('callback') == ui_manager._render_callback

    @patch('tkinter.messagebox.showinfo')
    def test_render_callback_success(self, mock_showinfo, ui_manager_fixture):
        """Verify _render_callback handles success (shows info message).
        Red Step: Requires _render_callback success path implementation.
        """
        ui_manager, _, _, _, panels = ui_manager_fixture
        mock_statusbar = panels['statusbar']
        mock_statusbar.set_status = MagicMock()
        # Assume some UI elements might need state reset (e.g., buttons enabled)
        mock_preview_panel = panels['preview'] # Example: preview panel button
        mock_preview_panel.show_idle_state = MagicMock()

        dummy_video_path = "media/videos/render/480p/EasyManimScene.mp4"
        
        ui_manager._render_callback(True, dummy_video_path)
        
        mock_showinfo.assert_called_once()
        assert "Render Complete" in mock_showinfo.call_args[0][0] # Title
        assert dummy_video_path in mock_showinfo.call_args[0][1] # Message includes path
        
        mock_statusbar.set_status.assert_called_once()
        assert "Video render complete" in mock_statusbar.set_status.call_args[0][0]
        assert dummy_video_path in mock_statusbar.set_status.call_args[0][0]
        
        mock_preview_panel.show_idle_state.assert_called_once() # Example state reset

    @patch('tkinter.messagebox.showerror')
    def test_render_callback_failure(self, mock_showerror, ui_manager_fixture):
        """Verify _render_callback handles failure (shows error message).
        Red Step: Requires _render_callback failure path implementation.
        """
        ui_manager, _, _, _, panels = ui_manager_fixture
        mock_statusbar = panels['statusbar']
        mock_statusbar.set_status = MagicMock()
        mock_preview_panel = panels['preview']
        mock_preview_panel.show_idle_state = MagicMock()

        dummy_error_msg = "Render exploded!"
        
        ui_manager._render_callback(False, dummy_error_msg)
        
        mock_showerror.assert_called_once()
        assert "Render Failed" in mock_showerror.call_args[0][0] # Title
        assert dummy_error_msg in mock_showerror.call_args[0][1] # Message
        
        mock_statusbar.set_status.assert_called_once()
        assert "Video render failed" in mock_statusbar.set_status.call_args[0][0]

        mock_preview_panel.show_idle_state.assert_called_once() # Example state reset