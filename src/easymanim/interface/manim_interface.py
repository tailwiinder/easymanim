# src/easymanim/interface/manim_interface.py
"""Handles executing Manim rendering commands asynchronously."""

import threading
import subprocess
import os
import tempfile
import pathlib
from typing import TYPE_CHECKING, Callable, Union, List, Literal

# Avoid circular import for type hinting
if TYPE_CHECKING:
    from easymanim.main_app import MainApplication # Assuming MainApplication is defined here

class ManimInterface:
    """Manages the execution of Manim CLI commands in background threads."""
    
    def __init__(self, root_app: 'MainApplication'):
        """Initializes the ManimInterface.

        Args:
            root_app: Reference to the main application instance, needed for scheduling 
                      UI updates from background threads.
        """
        self.root_app: 'MainApplication' = root_app
        
        # Create a dedicated temporary directory for scripts
        # This directory will be managed by the OS's temp system
        temp_dir_path_str = tempfile.mkdtemp(prefix="easymanim_scripts_")
        self.temp_script_dir: pathlib.Path = pathlib.Path(temp_dir_path_str)
        
        # Optional: Add cleanup for this dir? Maybe later if needed.
        # For now, rely on OS temp cleanup or manual deletion if issues arise.

    def render_async(self, 
                     script_content: str, 
                     scene_name: str, 
                     quality_flags: List[str], 
                     output_format: Literal['png', 'mp4'], 
                     callback: Callable[[bool, Union[bytes, str]], None]):
        """Renders a Manim script asynchronously in a background thread.

        Creates a temporary script file, starts a thread to run the Manim 
        command, and schedules a callback on the main thread upon completion.

        Args:
            script_content: The Manim script content as a string.
            scene_name: The name of the Scene class to render.
            quality_flags: List of Manim CLI flags for quality/preview 
                           (e.g., ['-', '-ql'], ['ql']).
            output_format: The desired output ('png' for preview, 'mp4' for video).
            callback: A function to call upon completion. Takes two arguments:
                      - success (bool): True if rendering succeeded, False otherwise.
                      - result (Union[bytes, str]): PNG image bytes if success and 
                        output_format='png', output video *path* (str) if success 
                        and output_format='mp4', or an error message (str) if failure.
        """
        temp_script_path_str = None # Define variable outside try block
        try:
            # Create a temporary file to store the script
            # delete=False is important because we need the file path to exist 
            # after the 'with' block to pass to the subprocess.
            # The thread running the subprocess will be responsible for deleting it.
            with tempfile.NamedTemporaryFile(mode='w', 
                                          suffix='.py', 
                                          delete=False, 
                                          dir=str(self.temp_script_dir),
                                          encoding='utf-8') as temp_script:
                temp_script.write(script_content)
                temp_script_path_str = temp_script.name
                # temp_script is automatically closed upon exiting the 'with' block

            # --- Start the background thread --- 
            thread = threading.Thread(
                target=self._run_manim_thread,
                args=(
                    temp_script_path_str, 
                    scene_name, 
                    quality_flags, 
                    output_format, 
                    callback
                )
            )
            thread.start()
            
            # Note: Cleanup of temp_script_path_str is now the responsibility 
            # of _run_manim_thread after the subprocess finishes.

        except Exception as e:
            # Handle exceptions during file writing or thread setup
            # Ensure callback is still called with failure
            error_message = f"Error setting up render: {e}"
            print(f"[ManimInterface Error] {error_message}") # Log error
            # Ensure cleanup happens even if thread start fails
            if temp_script_path_str and os.path.exists(temp_script_path_str):
                 try:
                     os.remove(temp_script_path_str)
                     print(f"Cleaned up failed script: {temp_script_path_str}")
                 except OSError as remove_error:
                     print(f"Error cleaning up failed script {temp_script_path_str}: {remove_error}")
            # Schedule the callback in the main thread
            self.root_app.schedule_task(callback, False, error_message)

    def _get_quality_directory(self, flags: List[str]) -> str:
        """Determines the Manim media quality directory based on flags."""
        # Manim maps flags to directory names, e.g. -ql -> 480p, -qm -> 720p, -qh -> 1080p
        # For V1, we primarily care about -ql
        if "-ql" in flags:
            return "480p"
        # Add other mappings if needed for future quality options
        # elif "-qm" in flags:
        #     return "720p"
        # elif "-qh" in flags:
        #     return "1080p"
        else:
            # Default or fallback if flags don't specify quality explicitly
            # Manim's default might vary, but 480p is a safe guess for -ql absence?
            # Or perhaps raise an error or use a default like "default_quality"
            print("[Manim Thread Warning] Could not determine quality directory from flags. Defaulting to 480p.")
            return "480p" 

    def _run_manim_thread(self, 
                          script_path: str, 
                          scene_name: str, 
                          flags: List[str], 
                          output_format: Literal['png', 'mp4'], 
                          callback: Callable[[bool, Union[bytes, str]], None]):
        """The function executed in the background thread to run Manim.
        
        Handles subprocess execution, result checking, and cleanup.
        """
        command = [
            'python', '-m', 'manim', 
            script_path, 
            scene_name
        ] + flags

        print(f"Running Manim command: {' '.join(command)}")
        success = False
        result_data: Union[bytes, str] = "Unknown error during execution."
        script_path_obj = pathlib.Path(script_path)

        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=False # We check returncode manually below
            )
            
            if result.returncode == 0:
                print(f"Manim execution successful (code 0) for {script_path}")
                # --- Handle successful PNG output --- 
                if output_format == 'png':
                    script_stem = script_path_obj.stem
                    # Manim convention: media/images/<script_stem>/<scene_name>*.png
                    # Glob for the potentially timestamped file name
                    # Assuming execution from project root where 'media' would be
                    glob_pattern = f"media/images/{script_stem}/{scene_name}*.png"
                    try:
                        output_files = list(pathlib.Path('.').glob(glob_pattern))
                        if not output_files:
                            result_data = f"Render success (code 0), but output PNG not found using glob: {glob_pattern}"
                            print(f"[Manim Thread Warning] {result_data}")
                        elif len(output_files) > 1:
                            # Warn but proceed with the first file found
                            result_data = f"Render success (code 0), but multiple PNGs found ({len(output_files)}) using glob: {glob_pattern}. Using first one." 
                            print(f"[Manim Thread Warning] {result_data}")
                            output_file = output_files[0]
                            result_data = output_file.read_bytes()
                            success = True
                        else: # Exactly one file found
                            output_file = output_files[0]
                            print(f"Found output PNG: {output_file}")
                            result_data = output_file.read_bytes()
                            success = True 
                    except Exception as e:
                        result_data = f"Render success (code 0), but failed to find/read output PNG: {e}"
                        print(f"[Manim Thread Error] {result_data}")
                        
                # --- Handle successful MP4 output --- 
                elif output_format == 'mp4':
                    script_stem = script_path_obj.stem
                    scene_name_no_ext = scene_name # Scene name usually doesn't have extension
                    # quality_dir = self._get_quality_directory(flags) # Old way
                    
                    # Manim convention: media/videos/<script_stem>/<quality_dir_with_fps>/<scene_name>.mp4
                    # Instead of predicting exact quality_dir, glob for the MP4 file.
                    media_videos_script_dir = pathlib.Path('.') / "media" / "videos" / script_stem
                    
                    print(f"Searching for MP4 output for scene '{scene_name_no_ext}' in subdirectories of: {media_videos_script_dir}")
                    
                    # Glob pattern: */SceneName.mp4 (any subdir under media_videos_script_dir)
                    found_files = list(media_videos_script_dir.glob(f"*/{scene_name_no_ext}.mp4"))
                    
                    if found_files:
                        if len(found_files) > 1:
                            # This case should be rare if Manim is run for a single quality setting at a time.
                            print(f"[Manim Thread Warning] Multiple MP4s found for '{scene_name_no_ext}' in {media_videos_script_dir}. Using first: {found_files[0]}")
                        
                        output_file_path = str(found_files[0].resolve()) # Use absolute path
                        print(f"Found output MP4: {output_file_path}")
                        success = True
                        result_data = output_file_path
                    else:
                        # File not found using glob
                        result_data = f"Render success (code 0), but output MP4 for '{scene_name_no_ext}' not found in any subdirectory of {media_videos_script_dir}"
                        print(f"[Manim Thread Warning] {result_data}")
                        # success remains False
                    
            else: # Manim returned non-zero exit code
                error_intro = f"Manim failed (code {result.returncode}) for {script_path}:"
                # Combine stdout/stderr for more context, prioritizing stderr
                error_details = f"\n--- STDERR ---\n{result.stderr or '[No Stderr]'}\n--- STDOUT ---\n{result.stdout or '[No Stdout]'}"
                result_data = f"{error_intro}{error_details}"
                print(f"[Manim Thread Error] {error_intro}")
                # success remains False (set initially)

        except Exception as e:
            # --- Exception handling during subprocess run --- 
            result_data = f"Exception during Manim subprocess run for {script_path}: {e}"
            print(f"[Manim Thread Error] {result_data}")
            success = False # Ensure success is false if exception occurs
            
        finally:
            # --- Schedule Callback --- 
            try:
                self.root_app.schedule_task(callback, success, result_data)
                print(f"Callback scheduled for {script_path_obj.name} (Success: {success})")
            except Exception as cb_e:
                print(f"[Manim Thread Error] Failed to schedule callback for {script_path_obj.name}: {cb_e}")

            # --- Cleanup --- 
            print(f"Cleaning up script: {script_path}") 
            try:
                # Use os.path.exists with the string path
                if os.path.exists(script_path):
                     os.remove(script_path)
                     print(f"Successfully removed script: {script_path_obj.name}")
                else:
                     print(f"Script file not found for cleanup: {script_path}")
            except OSError as e:
                print(f"[Manim Thread Error] Failed to remove script {script_path}: {e}")

    # Note: Removed the extra pass from the end of the class definition 