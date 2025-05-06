# EasyManim: Visual Manim Scene Creator

EasyManim is a user-friendly desktop application designed to simplify the creation of mathematical animations with the powerful [Manim Community](https://www.manim.community/) engine. It provides a graphical user interface (GUI) allowing users to visually construct scenes, add objects, edit properties, and render videos without directly writing Manim Python scripts for every detail.

Inspired by the usability of modern visual editors, EasyManim aims to make Manim's capabilities more accessible to educators, content creators, and anyone interested in producing high-quality mathematical visualizations.

**(Consider adding a screenshot or GIF of the EasyManim UI in action here)**

## Key Features (V0.1)

*   **Visual Scene Construction:** Add and manage Manim objects in a graphical environment.
*   **Supported Objects:** Create Circles, Squares, and Text objects.
*   **Property Editing:** Visually edit object properties such as:
    *   Position (X, Y, Z coordinates)
    *   Size (radius for circles, side length for squares)
    *   Text Content & Font Size
    *   Fill Color & Fill Opacity
    *   Stroke (Border) Color, Stroke Width (for shapes), & Stroke Opacity
*   **Animation Assignment:** Assign basic introductory animations (e.g., FadeIn, Write, GrowFromCenter) to objects.
*   **Static Preview:** Quickly render a static preview image of the current scene.
*   **Video Rendering:** Render the full animation to an MP4 video file.
*   **User-Friendly Interface:** Built with Python and `ttkbootstrap` for a clean, modern look and feel.

## Tech Stack

*   **Python 3.x**
*   **Manim Community Edition** (tested with v0.18.0 and later)
*   **Tkinter** (via `ttkbootstrap` for modern styling)
*   **Pillow** (for image handling in previews)

## Prerequisites

*   Python 3.7+ installed and added to your PATH.
*   A working Manim Community Edition installation. Please follow the [official Manim installation guide](https://docs.manim.community/en/stable/installation/index.html). This includes dependencies like FFmpeg, LaTeX, etc.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/EasyManim.git # Replace with your repo URL
    cd EasyManim
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    If you plan to contribute or run tests, also install development dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```
4. **Install the project in editable mode:**
   This step is important for resolving imports correctly, especially if you have a `src` layout.
   ```bash
   pip install -e .
   ```

## How to Run

After completing the installation steps, run the application using:

```bash
python -m easymanim.main
```
(Adjust the path if your entry point `main.py` is located differently, e.g., `python src/easymanim/main.py` or directly `python main.py` if it's in the root and configured in `pyproject.toml` as a script).

## How to Use (Basic Workflow)

1.  **Launch EasyManim.**
2.  **Add Objects:** Use the "Add Circle", "Add Square", or "Add Text" buttons in the toolbar. Objects will appear on the timeline.
3.  **Select an Object:** Click on an object's block in the timeline. Its properties will appear in the Properties Panel.
4.  **Edit Properties:** Modify position, size, color (fill/stroke), text content, opacity, etc., in the Properties Panel. Select an animation from the dropdown.
5.  **Preview Changes:** Click the "Refresh Preview" button to see a static image of your scene.
6.  **Render Video:** When ready, click the "Render Video" button to generate an MP4 animation.

## Current Status

EasyManim is currently at **V0.1**, a functional prototype demonstrating core viability. It supports basic object creation, property editing, a simple animation system, and video rendering.

## Future Direction (V2 and Beyond)

The next major version (V2) aims to introduce advanced animation and timeline controls, such as:

*   Custom animation durations (`run_time`).
*   Staggered object introduction and animation start times.
*   Defined object visibility durations on the timeline.
*   (Potentially) A more interactive timeline for visual adjustment of these timings.

We welcome contributions and suggestions to help EasyManim grow!

## Contributing

We encourage contributions to EasyManim! Please see the `CONTRIBUTING.md` file for guidelines on how to report bugs, suggest features, and submit pull requests.

## License

EasyManim is released under the **MIT License**. See the `LICENSE` file for more details. 