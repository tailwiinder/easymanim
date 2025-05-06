# tests/interface/test_manim_interface.py
"""Tests for the ManimInterface class."""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import pathlib
import tempfile # Import tempfile
import threading # Import threading
import subprocess # Import subprocess
import os # Import os for cleanup test later

# We expect ManimInterface to be in src/easymanim/interface/manim_interface.py
from easymanim.interface.manim_interface import ManimInterface

# Define a dummy class to mock MainApplication for type hints and basic function
class MockMainApplication:
    def schedule_task(self, callback, *args):
        # In tests, we might just call the callback immediately 
        # or use a mock to check if it was called
        pass 

class TestManimInterface:
    """Test suite for the ManimInterface."""

    def test_init_stores_root_app_and_defines_temp_dir(self):
        """Verify __init__ stores root_app and sets up temp_script_dir.
        Red Step: Requires __init__ method implementation.
        """
        mock_app = MockMainApplication()
        interface = ManimInterface(root_app=mock_app)

        assert interface.root_app is mock_app, "Should store the root_app reference"
        
        assert hasattr(interface, 'temp_script_dir'), "Should have a temp_script_dir attribute"
        assert isinstance(interface.temp_script_dir, pathlib.Path), "temp_script_dir should be a Path object"
        # We might test directory *creation* later or assume it happens here
        # For now, just check the attribute exists and is the right type

    @patch('tempfile.NamedTemporaryFile')
    def test_render_async_writes_script_to_temp_file(self, mock_named_temp_file, mocker):
        """Verify render_async creates and writes to a temporary script file.
        Red Step: Requires render_async method implementation.
        Uses mocker to patch tempfile.NamedTemporaryFile.
        """
        # Setup mock for the file handle returned by NamedTemporaryFile
        mock_file_handle = MagicMock()
        # Configure the context manager behavior
        mock_named_temp_file.return_value.__enter__.return_value = mock_file_handle
        # Store the dummy path in the mock file handle
        dummy_script_path = "/tmp/dummy_script_xyz.py"
        mock_file_handle.name = dummy_script_path

        mock_app = MockMainApplication()
        interface = ManimInterface(root_app=mock_app)
        
        dummy_script_content = "from manim import *\nclass TestScene(Scene): pass"
        dummy_scene_name = "TestScene"
        dummy_flags = ["-ql"]
        dummy_format = "png"
        mock_callback = MagicMock()

        # Call the method under test
        interface.render_async(
            script_content=dummy_script_content,
            scene_name=dummy_scene_name,
            quality_flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        # Assert NamedTemporaryFile was called correctly
        mock_named_temp_file.assert_called_once_with(
            mode='w', 
            suffix='.py', 
            delete=False, # Important for passing path to subprocess
            dir=str(interface.temp_script_dir), # Ensure it's a string if needed by mock
            encoding='utf-8' # Good practice to specify encoding
        )

        # Assert write was called with the script content on the mock file handle
        mock_file_handle.write.assert_called_once_with(dummy_script_content)
        # Assert the context manager was used (implies close)
        assert mock_named_temp_file.return_value.__exit__.called

    @patch('threading.Thread') # Patch the Thread class
    @patch('tempfile.NamedTemporaryFile') # Still need to patch file writing
    def test_render_async_starts_thread(self, mock_named_temp_file, mock_thread, mocker):
        """Verify render_async starts a thread targeting _run_manim_thread.
        Red Step: Requires render_async to instantiate and start threading.Thread.
        """
        # Setup mock for file writing
        mock_file_handle = MagicMock()
        mock_named_temp_file.return_value.__enter__.return_value = mock_file_handle
        dummy_script_path = "/tmp/dummy_script_thread.py"
        mock_file_handle.name = dummy_script_path

        mock_app = MockMainApplication()
        interface = ManimInterface(root_app=mock_app)
        # Add a dummy _run_manim_thread for the target check to work during test
        interface._run_manim_thread = MagicMock()
        
        # Dummy args for render_async
        dummy_script_content = "Script Content"
        dummy_scene_name = "SceneName"
        dummy_flags = ["-flag"]
        dummy_format = "mp4"
        mock_callback = MagicMock()

        # Call the method
        interface.render_async(
            script_content=dummy_script_content,
            scene_name=dummy_scene_name,
            quality_flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        # Assert threading.Thread was called
        mock_thread.assert_called_once()
        
        # Get the arguments passed to the Thread constructor
        call_args, call_kwargs = mock_thread.call_args
        
        # Check the target
        assert call_kwargs.get('target') == interface._run_manim_thread
        
        # Check the arguments passed to the target
        expected_args = (
            dummy_script_path, # Path from mock file handle
            dummy_scene_name,
            dummy_flags,
            dummy_format,
            mock_callback
        )
        assert call_kwargs.get('args') == expected_args

        # Assert the start method was called on the thread instance
        mock_thread.return_value.start.assert_called_once()

    @patch('subprocess.run')
    def test_run_manim_thread_calls_subprocess_correctly_preview(self, mock_subprocess_run, mocker):
        """Verify _run_manim_thread calls subprocess.run with correct preview args.
        Red Step: Requires _run_manim_thread to construct and run the command.
        """
        # Mock the return value of subprocess.run to avoid errors in this test
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        mock_app = MockMainApplication()
        # Mock the schedule_task to check callbacks later if needed
        mock_app.schedule_task = MagicMock()
        interface = ManimInterface(root_app=mock_app)
        
        # Arguments for the thread function
        dummy_script_path = "/tmp/dummy_preview.py"
        dummy_scene_name = "PreviewScene"
        # Preview flags according to checklist/architecture
        dummy_flags = ["-s", "-ql"]
        dummy_format = "png"
        mock_callback = MagicMock()

        # Call the method directly (it runs synchronously in the test)
        interface._run_manim_thread(
            script_path=dummy_script_path,
            scene_name=dummy_scene_name,
            flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        # Construct the expected command list
        expected_command = [
            'python', '-m', 'manim', 
            dummy_script_path, 
            dummy_scene_name
        ] + dummy_flags

        # Assert subprocess.run was called correctly
        mock_subprocess_run.assert_called_once_with(
            expected_command, 
            capture_output=True, 
            text=True, 
            check=False # Important: we check returncode manually
        )

    @patch('subprocess.run')
    def test_run_manim_thread_calls_subprocess_correctly_render(self, mock_subprocess_run, mocker):
        """Verify _run_manim_thread calls subprocess.run with correct render args.
        Green Step: Should pass with current implementation.
        """
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_app = MockMainApplication()
        mock_app.schedule_task = MagicMock()
        interface = ManimInterface(root_app=mock_app)
        
        dummy_script_path = "/tmp/dummy_render.py"
        dummy_scene_name = "EasyManimScene"
        # Render flags according to checklist/architecture
        dummy_flags = ["-ql"]
        dummy_format = "mp4"
        mock_callback = MagicMock()

        interface._run_manim_thread(
            script_path=dummy_script_path,
            scene_name=dummy_scene_name,
            flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        expected_command = [
            'python', '-m', 'manim', 
            dummy_script_path, 
            dummy_scene_name
        ] + dummy_flags

        mock_subprocess_run.assert_called_once_with(
            expected_command, 
            capture_output=True, 
            text=True, 
            check=False
        )

    @patch('os.remove') # Mock cleanup
    @patch('pathlib.Path') # Mock Path for glob and read_bytes
    @patch('subprocess.run') # Mock subprocess
    def test_run_manim_thread_schedules_success_callback_png(self, mock_subprocess_run, MockPath, mock_os_remove, mocker):
        """Verify _run_manim_thread schedules callback with PNG bytes on success.
        Red Step: Requires result checking, file finding, reading, and callback scheduling.
        """
        # --- Mock subprocess success --- 
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="Success!", stderr="")

        # --- Mock pathlib.Path --- 
        # Instance needed for the glob call
        mock_path_instance = MagicMock()
        # Configure the glob method to return a list with one mock file path
        mock_output_file_path = MagicMock()
        mock_path_instance.glob.return_value = [mock_output_file_path]
        # Configure the read_bytes method on the mock file path
        mock_png_bytes = b'\x89PNG\r\n\x1a\n' # Minimal PNG header
        mock_output_file_path.read_bytes.return_value = mock_png_bytes
        # Make Path('.') return our mock instance that has glob
        MockPath.return_value = mock_path_instance 
        
        # --- Mock App and Interface --- 
        mock_app = MockMainApplication()
        mock_app.schedule_task = MagicMock()
        interface = ManimInterface(root_app=mock_app)
        
        # --- Args for thread function --- 
        dummy_script_path = "/tmp/dummy_success.py"
        dummy_scene_name = "SuccessScene"
        dummy_flags = ["-s", "-ql"]
        dummy_format = "png"
        mock_callback = MagicMock()

        # --- Call the method --- 
        interface._run_manim_thread(
            script_path=dummy_script_path,
            scene_name=dummy_scene_name,
            flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        # --- Assertions --- 
        # 1. Check that glob was called correctly to find the output file
        expected_glob_pattern = f"media/images/{pathlib.Path(dummy_script_path).stem}/{dummy_scene_name}*.png"
        mock_path_instance.glob.assert_called_once_with(expected_glob_pattern)
        
        # 2. Check that read_bytes was called on the found file
        mock_output_file_path.read_bytes.assert_called_once()
        
        # 3. Check that schedule_task was called with success and image bytes
        mock_app.schedule_task.assert_called_once_with(mock_callback, True, mock_png_bytes)
        
        # 4. Check cleanup (will be tested more thoroughly later)
        # mock_os_remove.assert_called_once_with(dummy_script_path) 

    @patch('os.remove') # Mock cleanup
    @patch('subprocess.run') 
    # Patch os.path.exists now
    @patch('os.path.exists') 
    def test_run_manim_thread_schedules_success_callback_mp4(self, mock_os_path_exists, mock_subprocess_run, mock_os_remove, mocker):
        """Verify _run_manim_thread schedules callback with MP4 path on success.
        Uses os.path.exists mock.
        """
        # --- Mock subprocess --- 
        mock_result = MagicMock(returncode=0, stdout="Video Success!", stderr="")
        mock_subprocess_run.return_value = mock_result # Assign directly

        # --- Mock App and Interface --- 
        mock_app = MockMainApplication()
        mock_app.schedule_task = MagicMock()
        interface = ManimInterface(root_app=mock_app)
        
        # --- Args for thread function --- 
        dummy_script_path_str = "/tmp/dummy_mp4_success_ospath.py"
        dummy_scene_name = "SuccessScene"
        dummy_flags = ["-ql"]
        dummy_format = "mp4"
        mock_callback = MagicMock()
        
        # --- Determine Expected Path String --- 
        # Still need stem, use real pathlib locally for this
        script_stem = pathlib.Path(dummy_script_path_str).stem 
        quality_dir = interface._get_quality_directory(dummy_flags) 
        # Use os.path.join to match implementation
        expected_path_str = os.path.join('.', "media", "videos", script_stem, quality_dir, f"{dummy_scene_name}.mp4")

        # --- Configure the side effect for the mocked os.path.exists --- 
        def os_path_exists_side_effect(path_arg):
            # path_arg is the string passed to os.path.exists
            print(f"*** os.path.exists called with: {path_arg} ***")
            if path_arg == expected_path_str:
                print(f"    Matched MP4 Path -> TRUE")
                return True
            elif path_arg == dummy_script_path_str:
                print(f"    Matched Script Path -> TRUE")
                return True # For cleanup check in finally block
            else:
                print(f"    OTHER Path -> FALSE")
                return False
        mock_os_path_exists.side_effect = os_path_exists_side_effect
        
        # --- Call the method --- 
        interface._run_manim_thread(
            script_path=dummy_script_path_str,
            scene_name=dummy_scene_name,
            flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        # --- Assertions --- 
        # 1. Check that os.path.exists was called with expected paths
        mock_os_path_exists.assert_any_call(expected_path_str)
        mock_os_path_exists.assert_any_call(dummy_script_path_str)
        
        # 2. Check that schedule_task was called with success and the path string
        mock_app.schedule_task.assert_called_once_with(mock_callback, True, expected_path_str)
        
        # 3. Check cleanup 
        mock_os_remove.assert_called_once_with(dummy_script_path_str)

    @patch('os.remove') 
    @patch('os.path.exists') 
    @patch('subprocess.run')
    def test_run_manim_thread_schedules_failure_callback(self, mock_subprocess_run, mock_os_path_exists, mock_os_remove):
        """Verify _run_manim_thread schedules callback with error message on failure.
        Red Step: Requires handling of non-zero return code.
        """
        # --- Mock subprocess failure --- 
        error_output = "Traceback:\nSomething went wrong!"
        mock_subprocess_run.return_value = MagicMock(returncode=1, stdout="", stderr=error_output)

        # --- Mock os.path.exists for cleanup check --- 
        dummy_script_path_str = "/tmp/dummy_fail.py"
        def exists_side_effect(path_arg):
            if path_arg == dummy_script_path_str:
                return True # Assume script exists for cleanup
            return False
        mock_os_path_exists.side_effect = exists_side_effect
        
        # --- Mock App and Interface --- 
        mock_app = MockMainApplication()
        mock_app.schedule_task = MagicMock()
        interface = ManimInterface(root_app=mock_app)
        
        # --- Args for thread function --- 
        dummy_scene_name = "FailScene"
        dummy_flags = ["-ql"]
        dummy_format = "mp4" # Format doesn't matter much for failure
        mock_callback = MagicMock()

        # --- Call the method --- 
        interface._run_manim_thread(
            script_path=dummy_script_path_str,
            scene_name=dummy_scene_name,
            flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        # --- Assertions --- 
        # 1. Check schedule_task called with failure and error message
        # schedule_task(callback, success, result_data)
        mock_app.schedule_task.assert_called_once()
        call_args = mock_app.schedule_task.call_args[0]
        assert call_args[0] == mock_callback, "Callback function mismatch"
        assert call_args[1] is False, "Success flag should be False"
        assert isinstance(call_args[2], str), "Result data should be an error string"
        assert "Manim failed (code 1)" in call_args[2], "Error message should contain failure code"
        assert error_output in call_args[2], "Error message should contain stderr"
        
        # 2. Check cleanup 
        mock_os_remove.assert_called_once_with(dummy_script_path_str)

    @patch('os.remove') 
    @patch('os.path.exists') 
    @patch('subprocess.run')
    def test_run_manim_thread_cleans_up_temp_file(self, mock_subprocess_run, mock_os_path_exists, mock_os_remove):
        """Verify _run_manim_thread removes the temp script file in finally block.
        Red Step: Requires cleanup implementation in the finally block.
        """
        # --- Mock subprocess (result doesn't matter for cleanup) --- 
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        # --- Mock os.path.exists --- 
        dummy_script_path_str = "/tmp/dummy_cleanup.py"
        # Simulate file existing initially, then not existing after remove is called
        # (Though we only check remove was called once)
        exist_results = {dummy_script_path_str: True}
        def exists_side_effect(path_arg):
            return exist_results.get(path_arg, False)
        mock_os_path_exists.side_effect = exists_side_effect
        
        # --- Mock App and Interface --- 
        mock_app = MockMainApplication()
        mock_app.schedule_task = MagicMock() # Need mock schedule_task
        interface = ManimInterface(root_app=mock_app)
        
        # --- Args for thread function --- 
        dummy_scene_name = "CleanupScene"
        dummy_flags = ["-ql"]
        dummy_format = "mp4"
        mock_callback = MagicMock()

        # --- Call the method --- 
        interface._run_manim_thread(
            script_path=dummy_script_path_str,
            scene_name=dummy_scene_name,
            flags=dummy_flags,
            output_format=dummy_format,
            callback=mock_callback
        )

        # --- Assertions --- 
        # 1. Check os.path.exists was called for the script path
        mock_os_path_exists.assert_any_call(dummy_script_path_str)
        
        # 2. Check os.remove was called exactly once with the script path
        mock_os_remove.assert_called_once_with(dummy_script_path_str)

    # Tests for failure callback, cleanup will go here 