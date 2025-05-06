"""Main entry point for the EasyManim application."""

# Ensure Pillow knows where Tcl/Tk is if not automatically found
# import os
# if os.environ.get('TK_LIBRARY') is None or os.environ.get('TCL_LIBRARY') is None:
#     # Add paths specific to your Python/Tk installation if needed
#     # Example for some Homebrew installations on macOS:
#     # tk_lib_path = "/opt/homebrew/opt/tcl-tk/lib"
#     # if os.path.exists(tk_lib_path):
#     #     os.environ['TK_LIBRARY'] = os.path.join(tk_lib_path, 'tk8.6')
#     #     os.environ['TCL_LIBRARY'] = os.path.join(tk_lib_path, 'tcl8.6')
#     print(f"TK_LIBRARY: {os.environ.get('TK_LIBRARY')}")
#     print(f"TCL_LIBRARY: {os.environ.get('TCL_LIBRARY')}")

# Import the main application class using relative import
from .main_app import MainApplication

def main():
    """Creates and runs the main application instance."""
    print("EasyManim starting...")
    app = MainApplication()
    app.run()
    print("EasyManim finished.")

if __name__ == "__main__":
    main() 