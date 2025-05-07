import uuid
import textwrap
from typing import Any, Dict, List, Optional, Literal

# Default properties based on PRD and Manim standards
DEFAULT_CIRCLE_PROPS = {
    'pos_x': 0.0,
    'pos_y': 0.0,
    'pos_z': 0.0, # Add pos_z for consistency
    'radius': 1.0,
    'fill_color': '#58C4DD', # Manim default blue
    'opacity': 1.0, # Add opacity
    'stroke_color': '#FFFFFF', # Default white stroke
    'stroke_width': 2.0,      # Default stroke width
    'stroke_opacity': 1.0,
    'animation': 'None' # Add animation
}

DEFAULT_SQUARE_PROPS = {
    'pos_x': 0.0,
    'pos_y': 0.0,
    'pos_z': 0.0, # Add pos_z
    'side_length': 2.0, # Manim default
    'fill_color': '#58C4DD', # Manim default blue (can change later)
    'opacity': 1.0, # Add opacity
    'stroke_color': '#FFFFFF', # Default white stroke
    'stroke_width': 2.0,      # Default stroke width
    'stroke_opacity': 1.0,
    'animation': 'None' # Add animation
}

DEFAULT_TEXT_PROPS = {
    'pos_x': 0.0,
    'pos_y': 0.0,
    'pos_z': 0.0, # Add pos_z
    'text_content': 'Text',
    'fill_color': '#FFFFFF', # Manim default white
    'font_size': 48, # Add font_size
    'opacity': 1.0, # Add opacity
    'stroke_color': '#000000', # Default black stroke for text (often not visible without width)
    'stroke_opacity': 1.0,     # Manim's Text might not use stroke_width directly for font outline
                                # but stroke_color and stroke_opacity are valid params.
    'animation': 'None' # Add animation
}

DEFAULT_PROPS_MAP = {
    'Circle': DEFAULT_CIRCLE_PROPS,
    'Square': DEFAULT_SQUARE_PROPS,
    'Text': DEFAULT_TEXT_PROPS, # PRD uses TextMobject, just use Text for type key
}

class SceneBuilder:
    """Manages the state of the Manim scene being constructed.

    Handles adding objects, updating their properties, managing animations,
    and generating Manim scripts.
    """
    def __init__(self):
        """Initializes the SceneBuilder with an empty list of scene objects."""
        self.objects: List[Dict[str, Any]] = []

    def _generate_unique_id(self, obj_type: str) -> str:
        """Generates a unique ID for a scene object."""
        # Format: objecttype_first6charsofUUIDhex
        return f"{obj_type.lower()}_{uuid.uuid4().hex[:6]}"

    def add_object(self, obj_type: str) -> str:
        """Adds a new object of the specified type to the scene.
        
        Creates an object dictionary with default properties based on the type,
        assigns a unique ID, and appends it to the internal list.

        Args:
            obj_type: The type of Manim object to add (e.g., 'Circle', 'Square', 'Text').

        Returns:
            A unique ID assigned to the new object.
            
        Raises:
            ValueError: If obj_type is not recognized.
        """
        if obj_type not in DEFAULT_PROPS_MAP:
            # Consider more robust error handling or logging later
            raise ValueError(f"Unsupported object type: {obj_type}")
            
        new_id = self._generate_unique_id(obj_type)
        default_props = DEFAULT_PROPS_MAP[obj_type]
        
        new_object_data = {
            'id': new_id,
            'type': obj_type,
            'properties': default_props.copy(), # animation is now part of default_props
            # 'animation': 'None' # No longer a top-level item here
        }
        
        self.objects.append(new_object_data)
        
        return new_id

    def get_object_properties(self, obj_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the 'properties' sub-dictionary for a given object ID.
        This dictionary contains all displayable and editable attributes.
        """
        for obj in self.objects:
            if obj.get('id') == obj_id:
                # Return the 'properties' sub-dictionary directly
                return obj.get('properties')
        return None

    def update_object_property(self, obj_id: str, prop_key: str, value: Any, axis_index: Optional[int] = None):
        """Updates a specific property of a specific object within its 'properties' dict."""
        obj_to_update = None
        for obj_data in self.objects: # Renamed obj to obj_data to avoid conflict
            if obj_data['id'] == obj_id:
                obj_to_update = obj_data
                break

        if obj_to_update:
            properties = obj_to_update['properties'] # Get the sub-dictionary

            if prop_key == 'position' and axis_index is not None:
                # Determine the actual key for pos_x, pos_y, pos_z based on axis_index
                pos_keys = ['pos_x', 'pos_y', 'pos_z']
                if 0 <= axis_index < len(pos_keys):
                    actual_prop_key = pos_keys[axis_index]
                    try:
                        properties[actual_prop_key] = float(value)
                        print(f"Updated {actual_prop_key} for {obj_id} to {value}. Properties: {properties}")
                    except ValueError:
                        print(f"Error: Invalid value '{value}' for {actual_prop_key}.")
                else:
                    print(f"Error: Invalid axis_index {axis_index} for position component update.")
            elif prop_key == 'animation': # Handle animation directly now
                 properties[prop_key] = str(value) # Ensure it's a string
                 print(f"Updated property for {obj_id}: {prop_key} to {value}. Properties: {properties}")
            else:
                # Default behavior for other properties
                # Type conversion might be needed here based on prop_key
                if prop_key in ['radius', 'side_length', 'font_size', 'opacity', 'stroke_width', 'stroke_opacity']:
                    try:
                        properties[prop_key] = float(value)
                    except ValueError:
                        print(f"Error: Invalid float value '{value}' for {prop_key}.")
                        return # Or handle error appropriately
                elif prop_key == 'text_content':
                    properties[prop_key] = str(value)
                elif prop_key == 'fill_color': # Assuming color is a hex string
                    properties[prop_key] = str(value)
                else:
                    properties[prop_key] = value # Fallback for other types or new properties
                print(f"Updated property for {obj_id}: {prop_key} to {value}. Properties: {properties}")
        else:
            print(f"Error: Object with ID {obj_id} not found for update.")

    def set_object_animation(self, obj_id: str, anim_name: str):
        """Sets the animation type for a specific object within its 'properties' dict."""
        target_object_data = None
        for obj_data in self.objects:
            if obj_data.get('id') == obj_id:
                target_object_data = obj_data
                break

        if target_object_data is None:
            print(f"Error: Object with ID {obj_id} not found for setting animation.")
            return

        if 'properties' in target_object_data:
            target_object_data['properties']['animation'] = anim_name
            print(f"Set animation for {obj_id} to {anim_name}. Properties: {target_object_data['properties']}")
        else:
            print(f"Error: 'properties' dictionary not found for object {obj_id}.")

    def get_all_objects(self) -> List[Dict[str, Any]]:
        """Returns a shallow copy of the list of all object dictionaries.

        Returns:
            A list containing dictionaries, where each dictionary represents
            an object in the scene.
        """
        # Return a shallow copy to prevent external modification of internal list
        return self.objects.copy() 

    def _format_manim_prop(self, value: Any) -> str:
        """Formats a Python value into a Manim-compatible string representation."""
        if isinstance(value, str):
            # Need quotes for strings
            # Escape potential quotes within the string itself
            escaped_value = value.replace("\'", "\\\'").replace('"', '\\"')
            return f"'{escaped_value}'"
        # Add more formatting rules if needed (e.g., for lists, specific objects)
        return str(value) # Default to standard string conversion

    def generate_script(self, script_type: Literal['preview', 'render']) -> tuple[str, str]:
        """Generates a Manim Python script based on the current scene state.

        Args:
            script_type: Determines the type of script ('preview' or 'render').
                         'preview' generates a static scene.
                         'render' includes animations.

        Returns:
            A tuple containing:
            - The generated Python script content as a string.
            - The name of the Manim Scene class defined in the script.
        """
        object_creation_lines = []
        add_lines = []
        play_lines = [] # For render script later

        # Common imports
        imports = [
            "# Generated by EasyManim",
            "from manim import *",
            "import numpy as np # Often needed for positioning"
        ]
        
        # Sort objects by z-position for creation order
        objects_by_type = {
            'Text': [],
            'Other': []
        }
        
        # Separate text objects from other objects
        for obj in self.objects:
            if obj['type'] == 'Text':
                objects_by_type['Text'].append(obj)
            else:
                objects_by_type['Other'].append(obj)
        
        # All objects need to be created in the regular way
        for obj in self.objects:
            obj_id = obj['id']
            obj_type = obj['type']
            properties = obj['properties']
            animation = properties.get('animation', 'None') 
            
            var_name = f"{obj_type.lower()}_{obj_id[-6:]}"
            
            # --- Object Instantiation (common for all) ---
            prop_args_for_script = [] 
            pos_x = properties.get('pos_x', 0.0)
            pos_y = properties.get('pos_y', 0.0)
            pos_z = properties.get('pos_z', 0.0)
            
            # Use move_to for x,y positioning only
            move_to_str = f".move_to(np.array([{pos_x}, {pos_y}, 0]))"
            
            # Convert z position to z_index in a safe way - only for non-text objects
            # Higher z values = higher z_index = appears on top
            z_index_value = max(0, int(pos_z * 10))
            
            # For non-text objects, handle z_index as a parameter
            if obj_type != 'Text' and z_index_value > 0:
                prop_args_for_script.append(f"z_index={z_index_value}")
                
            instantiation_base = f"{var_name} = {obj_type}("
            if obj_type == 'Text':
                text_content_formatted = self._format_manim_prop(properties.get('text_content', ''))
                instantiation_base += text_content_formatted
                font_size_val = properties.get('font_size')
                if font_size_val is not None:
                    prop_args_for_script.append(f"font_size={self._format_manim_prop(font_size_val)}")
                prop_args_for_script.append(f"color={self._format_manim_prop(properties.get('fill_color', '#FFFFFF'))}")
                prop_args_for_script.append(f"fill_opacity={self._format_manim_prop(properties.get('opacity', 1.0))}")
                prop_args_for_script.append(f"stroke_color={self._format_manim_prop(properties.get('stroke_color', '#000000'))}")
                prop_args_for_script.append(f"stroke_opacity={self._format_manim_prop(properties.get('stroke_opacity', 1.0))}")
            elif obj_type == 'Circle':
                prop_args_for_script.append(f"radius={self._format_manim_prop(properties.get('radius', 1.0))}")
                prop_args_for_script.append(f"fill_color={self._format_manim_prop(properties.get('fill_color', '#FFFFFF'))}")
                prop_args_for_script.append(f"fill_opacity={self._format_manim_prop(properties.get('opacity', 1.0))}")
                prop_args_for_script.append(f"stroke_color={self._format_manim_prop(properties.get('stroke_color', '#FFFFFF'))}")
                prop_args_for_script.append(f"stroke_width={self._format_manim_prop(properties.get('stroke_width', 2.0))}")
                prop_args_for_script.append(f"stroke_opacity={self._format_manim_prop(properties.get('stroke_opacity', 1.0))}")
            elif obj_type == 'Square':
                prop_args_for_script.append(f"side_length={self._format_manim_prop(properties.get('side_length', 2.0))}")
                prop_args_for_script.append(f"fill_color={self._format_manim_prop(properties.get('fill_color', '#FFFFFF'))}")
                prop_args_for_script.append(f"fill_opacity={self._format_manim_prop(properties.get('opacity', 1.0))}")
                prop_args_for_script.append(f"stroke_color={self._format_manim_prop(properties.get('stroke_color', '#FFFFFF'))}")
                prop_args_for_script.append(f"stroke_width={self._format_manim_prop(properties.get('stroke_width', 2.0))}")
                prop_args_for_script.append(f"stroke_opacity={self._format_manim_prop(properties.get('stroke_opacity', 1.0))}")

            if prop_args_for_script:
                if obj_type == 'Text' and instantiation_base.endswith(text_content_formatted):
                    instantiation_base += ", "
                instantiation_base += ", ".join(prop_args_for_script)
            
            # Base instantiation
            final_instantiation = f"{instantiation_base}){move_to_str}"
            object_creation_lines.append(final_instantiation)
            
            # --- Animation and Scene Addition Logic ---
            added_by_intro_animation = False
            if script_type == 'render' and animation != 'None':
                animation_command_str = None
                is_intro_anim = False

                if animation == 'FadeIn':
                    animation_command_str = f"FadeIn({var_name})"
                    is_intro_anim = True
                elif animation == 'GrowFromCenter':
                    animation_command_str = f"GrowFromCenter({var_name})"
                    is_intro_anim = True
                elif animation == 'Write' and obj_type == 'Text':
                    animation_command_str = f"Write({var_name})"
                    is_intro_anim = True
                
                if animation_command_str:
                    play_lines.append(f"self.play({animation_command_str})")
                    if is_intro_anim:
                        added_by_intro_animation = True
                elif animation == 'Write' and obj_type != 'Text': 
                    add_lines.append(f"self.add({var_name}) # 'Write' animation not applicable to {obj_type}")
                else:
                    add_lines.append(f"self.add({var_name}) # Default add for animation: {animation}")
            
            # Skip adding objects here - we'll handle them based on z-position
            if not added_by_intro_animation and animation != 'None':
                add_lines.append(f"self.add({var_name}) # For animation: {animation}")

        # Collect objects for z-ordering
        shape_objects = []  # Non-text objects
        text_objects = []   # Text objects only
        
        for obj in self.objects:
            obj_id = obj['id']
            obj_type = obj['type']
            animation = obj['properties'].get('animation', 'None')
            var_name = f"{obj_type.lower()}_{obj_id[-6:]}"
            pos_z = obj['properties'].get('pos_z', 0)
            
            # Skip objects already handled by animations
            if script_type == 'render':
                if animation == 'FadeIn' or animation == 'GrowFromCenter':
                    continue
                if animation == 'Write' and obj_type == 'Text':
                    continue
            
            # Separate text and non-text objects
            if obj_type == 'Text':
                text_objects.append((var_name, pos_z))
            else:
                shape_objects.append((var_name, pos_z, obj_type))
        
        # First add all non-text objects in z-order
        if shape_objects:
            # Sort by z-position (low to high)
            shape_objects.sort(key=lambda x: x[1])
            
            add_lines.append("\n# Non-text objects added in z-order")
            for var_name, z_pos, obj_type in shape_objects:
                add_lines.append(f"self.add({var_name})  # {obj_type} with z={z_pos}")
        
        # Then add all text objects in z-order
        if text_objects:
            # Sort by z-position (low to high)
            text_objects.sort(key=lambda x: x[1])
            
            add_lines.append("\n# Text objects added last to ensure proper z-ordering")
            for var_name, z_pos in text_objects:
                add_lines.append(f"self.add({var_name})  # Text with z={z_pos}")
            
            # Then bring ALL text objects to front explicitly
            if text_objects:
                add_lines.append("\n# Ensure ALL text objects appear on top")
                for var_name, z_pos in text_objects:
                    add_lines.append(f"self.bring_to_front({var_name})  # Force text on top")
                
            # Extra handling for text with positive z-values
            texts_with_positive_z = [(name, z) for name, z in text_objects if z > 0]
            if texts_with_positive_z:
                # Sort by descending z-position (highest z first) for proper layering
                texts_with_positive_z.sort(key=lambda x: -x[1])  # Note the negative sign for descending sort
                
                add_lines.append("\n# Extra handling for text with positive z-values")
                for var_name, z_pos in texts_with_positive_z:
                    # Apply multiple bring_to_front calls for higher z-values
                    # This is a hack, but it helps ensure text with higher z appears on top
                    repeats = max(1, int(z_pos))
                    for _ in range(repeats):
                        add_lines.append(f"self.bring_to_front({var_name})  # Extra priority for z={z_pos}")
        
        # Determine Scene Name and Class Definition
        scene_name = "PreviewScene" if script_type == 'preview' else "EasyManimScene"
        class_def = f"class {scene_name}(Scene):"
        construct_def = "    def construct(self):"

        # Assemble the final script
        construct_body_lines = []
        
        # If z-position is used, add a comment explaining z-index 
        if any(abs(obj['properties'].get('pos_z', 0.0)) > 0.001 for obj in self.objects):
            construct_body_lines.append("# Z-positioning is being used via z_index")
            construct_body_lines.append("# Higher z_index values appear on top (closer to viewer)")
        
        # Add all object creation code
        construct_body_lines.extend(object_creation_lines)

        # For render scripts, play lines (animations) come first, then residual add lines.
        # For preview scripts, only add lines are used after object creation.
        if script_type == 'render':
            construct_body_lines.extend(play_lines) 
            construct_body_lines.extend(add_lines) # These are objects not introduced by an animation
        else: # preview
            construct_body_lines.extend(add_lines)
            
        if not (object_creation_lines or add_lines or play_lines): # Check if any content for body
            indented_body = "        pass # No objects or animations"
        else:
            indented_body = textwrap.indent("\n".join(construct_body_lines), "        ")

        script_lines = imports + ["", class_def, construct_def, indented_body]
        script_content = "\n".join(script_lines)

        return script_content, scene_name 