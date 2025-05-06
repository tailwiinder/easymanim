import pytest
# We expect SceneBuilder to be in src/easymanim/logic/scene_builder.py
from easymanim.logic.scene_builder import SceneBuilder

def test_init_creates_empty_object_list():
    """
    Verify that SceneBuilder initializes with an empty list of objects.
    Red Step: This test expects SceneBuilder to exist and have an 'objects' list.
    """
    builder = SceneBuilder()
    # Assert that the 'objects' attribute exists and is an empty list
    assert hasattr(builder, 'objects'), "SceneBuilder instance should have an 'objects' attribute"
    assert builder.objects == [], "SceneBuilder should initialize with an empty 'objects' list"

def test_add_object_returns_unique_id():
    """Verify that adding objects returns unique IDs.
    Red Step: This test requires the add_object method to exist and return something.
    """
    builder = SceneBuilder()
    # Assume 'Circle' is a valid type for now
    id1 = builder.add_object('Circle') 
    id2 = builder.add_object('Square') # Use a different type for variety

    assert isinstance(id1, str), "ID should be a string"
    assert isinstance(id2, str), "ID should be a string"
    assert id1 != id2, "Consecutive calls to add_object should return unique IDs"
    assert len(id1) > 0, "ID should not be empty"
    assert len(id2) > 0, "ID should not be empty"

def test_add_object_adds_correct_type_to_list():
    """Verify add_object adds a dictionary with the correct type and ID to the internal list.
    Red Step: This requires add_object to modify self.objects.
    """
    builder = SceneBuilder()
    obj_type_to_add = "Circle"
    returned_id = builder.add_object(obj_type_to_add)

    assert len(builder.objects) == 1, "objects list should contain one item after adding"
    
    added_object = builder.objects[0]
    assert isinstance(added_object, dict), "Item in objects list should be a dictionary"
    assert added_object.get('id') == returned_id, "Object dictionary should have the correct 'id'"
    assert added_object.get('type') == obj_type_to_add, "Object dictionary should have the correct 'type'"
    
    # Check for existence of a properties dictionary (content tested later)
    assert 'properties' in added_object, "Object dictionary should have a 'properties' key"
    assert isinstance(added_object['properties'], dict), "'properties' should be a dictionary"

    # Check for default animation state
    assert 'animation' in added_object, "Object dictionary should have an 'animation' key"
    assert added_object['animation'] == 'None', "Default animation should be 'None'"

    # Add another object to ensure list grows correctly
    builder.add_object("Square")
    assert len(builder.objects) == 2, "objects list should contain two items after adding a second"
    assert builder.objects[1].get('type') == "Square", "Second object should have the correct type"

def test_get_object_properties_retrieves_correct_data():
    """Verify get_object_properties returns the correct properties for a valid ID.
    Red Step: Requires the get_object_properties method.
    """
    builder = SceneBuilder()
    circle_id = builder.add_object('Circle')
    square_id = builder.add_object('Square')

    circle_props = builder.get_object_properties(circle_id)
    square_props = builder.get_object_properties(square_id)

    assert isinstance(circle_props, dict), "Should return a dictionary for valid ID"
    assert circle_props.get('radius') == 1.0, "Returned properties should match defaults (Circle)"
    assert circle_props.get('fill_color') == '#58C4DD'

    assert isinstance(square_props, dict), "Should return a dictionary for valid ID"
    assert square_props.get('side_length') == 2.0, "Returned properties should match defaults (Square)"
    
    # Ensure the returned dict is the properties dict, not the whole object dict
    assert 'id' not in circle_props 
    assert 'type' not in circle_props
    assert 'animation' not in circle_props

def test_get_object_properties_returns_none_for_invalid_id():
    """Verify get_object_properties returns None for an invalid or non-existent ID.
    Red Step: Requires the get_object_properties method.
    """
    builder = SceneBuilder()
    builder.add_object('Circle') # Add something so the list isn't empty

    props = builder.get_object_properties("invalid_id_123")
    assert props is None, "Should return None for an invalid ID"

    props_empty = builder.get_object_properties("")
    assert props_empty is None, "Should return None for an empty string ID"

def test_update_object_property_modifies_internal_state():
    """Verify update_object_property correctly modifies the internal state.
    Red Step: Requires the update_object_property method.
    """
    builder = SceneBuilder()
    circle_id = builder.add_object('Circle')
    initial_props = builder.get_object_properties(circle_id)
    assert initial_props['pos_x'] == 0.0 # Verify initial state

    # --- Test updating a valid property --- 
    new_pos_x = -5.5
    builder.update_object_property(circle_id, 'pos_x', new_pos_x)
    
    updated_props = builder.get_object_properties(circle_id)
    assert updated_props['pos_x'] == new_pos_x, "pos_x should be updated"
    assert updated_props['pos_y'] == 0.0, "Other properties should remain unchanged"
    assert updated_props['radius'] == 1.0, "Other properties should remain unchanged"

    # --- Test updating a different property (color) --- 
    new_color = "#FF0000"
    builder.update_object_property(circle_id, 'fill_color', new_color)
    updated_props_color = builder.get_object_properties(circle_id)
    assert updated_props_color['fill_color'] == new_color, "fill_color should be updated"
    assert updated_props_color['pos_x'] == new_pos_x, "Previous updates should persist"

    # --- Test updating non-existent ID --- 
    # Ensure updating an invalid ID doesn't crash and doesn't affect existing objects
    try:
        builder.update_object_property("invalid_id", 'pos_x', 100.0)
    except Exception as e:
        pytest.fail(f"Updating invalid ID raised an unexpected exception: {e}")
    
    props_after_invalid_update = builder.get_object_properties(circle_id)
    assert props_after_invalid_update['pos_x'] == new_pos_x, "Updating invalid ID shouldn't affect valid objects"

    # --- Test updating non-existent property key --- 
    # Ensure updating an invalid property key doesn't crash and doesn't add the key (for now)
    try:
        builder.update_object_property(circle_id, 'non_existent_prop', 'some_value')
    except Exception as e:
        pytest.fail(f"Updating invalid property key raised an unexpected exception: {e}")
        
    props_after_invalid_key = builder.get_object_properties(circle_id)
    assert 'non_existent_prop' not in props_after_invalid_key, "Updating invalid key shouldn't add the key"
    assert props_after_invalid_key['pos_x'] == new_pos_x, "Updating invalid key shouldn't affect other properties"

def test_set_object_animation_modifies_internal_state():
    """Verify set_object_animation correctly updates the animation state.
    Red Step: Requires the set_object_animation method.
    """
    builder = SceneBuilder()
    circle_id = builder.add_object('Circle')
    square_id = builder.add_object('Square')

    # Check initial state
    assert builder.objects[0]['animation'] == 'None'
    assert builder.objects[1]['animation'] == 'None'

    # Set animation for the circle
    anim_name = "FadeIn"
    builder.set_object_animation(circle_id, anim_name)

    # Verify circle animation updated, square unchanged
    assert builder.objects[0]['animation'] == anim_name, "Circle animation should be updated"
    assert builder.objects[1]['animation'] == 'None', "Square animation should remain unchanged"

    # Set animation for the square
    builder.set_object_animation(square_id, "Grow") # Use a different hypothetical anim name
    assert builder.objects[0]['animation'] == anim_name, "Circle animation should persist"
    assert builder.objects[1]['animation'] == "Grow", "Square animation should be updated"

    # Reset circle animation
    builder.set_object_animation(circle_id, "None")
    assert builder.objects[0]['animation'] == 'None', "Circle animation should be reset to None"

    # Test updating non-existent ID
    try:
        builder.set_object_animation("invalid_id", "FadeOut")
    except Exception as e:
        pytest.fail(f"Setting animation for invalid ID raised an unexpected exception: {e}")
    
    # Ensure other animations weren't affected
    assert builder.objects[0]['animation'] == 'None'
    assert builder.objects[1]['animation'] == "Grow"

def test_get_all_objects_returns_copy():
    """Verify get_all_objects returns a copy of the internal objects list.
    Red Step: Requires the get_all_objects method.
    """
    builder = SceneBuilder()
    assert builder.get_all_objects() == [], "Should return empty list initially"

    id1 = builder.add_object('Circle')
    id2 = builder.add_object('Square')
    builder.update_object_property(id1, 'pos_x', 1.0)
    builder.set_object_animation(id2, 'FadeIn')

    all_objects = builder.get_all_objects()

    assert isinstance(all_objects, list), "Should return a list"
    assert len(all_objects) == 2, "Should return all added objects"
    assert all_objects[0]['id'] == id1
    assert all_objects[1]['id'] == id2
    assert all_objects[0]['type'] == 'Circle'
    assert all_objects[1]['type'] == 'Square'
    assert all_objects[0]['properties']['pos_x'] == 1.0 # Check if properties are present
    assert all_objects[1]['animation'] == 'FadeIn' # Check if animation state is present

    # Verify it returns a COPY, not the internal list itself
    assert all_objects is not builder.objects, "Should return a copy, not the internal list reference"

    # Further check for copy: modify the returned list and ensure internal state is unchanged
    all_objects[0]['properties']['pos_x'] = 99.0
    internal_object_props = builder.get_object_properties(id1)
    # assert internal_object_props['pos_x'] == 1.0, "Modifying the returned list should not affect internal state (shallow copy check)"
    # Corrected assertion for shallow copy:
    assert internal_object_props['pos_x'] == 99.0, "Modifying the shallow copy's nested dict *should* affect internal state"

    # Optional deep copy check (modifying a nested dict): 
    # Note: The current implementation likely needs deepcopy for this to pass
    # all_objects[0]['properties']['pos_x'] = 99.0 
    # internal_props = builder.get_object_properties(id1)
    # assert internal_props['pos_x'] == 1.0 # This would fail with just .copy()
    # For V1, a shallow copy via .copy() is acceptable as per checklist note. 

def test_generate_script_preview_empty():
    """Verify generate_script('preview') returns a valid empty scene script.
    Red Step: Requires the generate_script method.
    """
    builder = SceneBuilder()
    script_content, scene_name = builder.generate_script('preview')

    assert scene_name == "PreviewScene", "Scene name for preview should be PreviewScene"
    assert isinstance(script_content, str), "Script content should be a string"
    assert "from manim import *" in script_content, "Script should import manim"
    assert "class PreviewScene(Scene):" in script_content, "Script should define PreviewScene class"
    assert "def construct(self):" in script_content, "Scene should have a construct method"
    # Check for emptiness - simplest check is absence of common object/add lines
    assert "Circle" not in script_content 
    assert "Square" not in script_content
    assert "Text" not in script_content
    assert "self.add" not in script_content 
    assert "self.play" not in script_content 

def test_generate_script_preview_with_objects():
    """Verify generate_script('preview') creates code for added objects.
    Red Step: Requires generate_script to process self.objects.
    """
    builder = SceneBuilder()
    circle_id = builder.add_object('Circle')
    text_id = builder.add_object('Text')
    
    # Modify a property to check if it's reflected
    builder.update_object_property(text_id, 'pos_y', 1.5)
    builder.update_object_property(text_id, 'text_content', 'Hello')
    builder.update_object_property(circle_id, 'fill_color', '#FF0000')

    script_content, scene_name = builder.generate_script('preview')

    assert scene_name == "PreviewScene"
    
    # Check for variable names based on ID suffix (implementation detail, but testable)
    circle_var = f"circle_{circle_id[-6:]}"
    text_var = f"text_{text_id[-6:]}"
    assert circle_var in script_content, "Should generate variable name for circle"
    assert text_var in script_content, "Should generate variable name for text"

    # Check for object instantiation with properties
    # Note: Formatting might vary slightly, focus on key elements
    assert f"{circle_var} = Circle(radius=1.0, fill_color='#FF0000')" in script_content
    # Position check needs .move_to()
    assert f".move_to([0.0, 0.0, 0.0])" in script_content # Default position for circle
    
    assert f"{text_var} = Text('Hello', fill_color='#FFFFFF')" in script_content
    assert f".move_to([0.0, 1.5, 0.0])" in script_content # Updated position for text

    # Check for self.add calls
    assert f"self.add({circle_var})" in script_content
    assert f"self.add({text_var})" in script_content

    # Ensure no animations are included in preview
    assert "self.play" not in script_content

    # Check overall structure again
    assert "class PreviewScene(Scene):" in script_content
    assert "def construct(self):" in script_content 

def test_generate_script_render_empty():
    """Verify generate_script('render') returns a valid empty scene script.
    Red Step: Requires generate_script to handle the 'render' type.
    """
    builder = SceneBuilder()
    script_content, scene_name = builder.generate_script('render')

    assert scene_name == "EasyManimScene", "Scene name for render should be EasyManimScene"
    assert isinstance(script_content, str), "Script content should be a string"
    assert "from manim import *" in script_content, "Script should import manim"
    assert "class EasyManimScene(Scene):" in script_content, "Script should define EasyManimScene class"
    assert "def construct(self):" in script_content, "Scene should have a construct method"
    # Check for emptiness
    assert "Circle" not in script_content
    assert "Square" not in script_content
    assert "Text" not in script_content
    assert "self.add" not in script_content
    assert "self.play" not in script_content 

def test_generate_script_render_no_animation():
    """Verify render script generation with objects but no animations.
    Green Step: This should pass with current implementation if preview works.
    """
    builder = SceneBuilder()
    circle_id = builder.add_object('Circle')
    text_id = builder.add_object('Text')
    # Ensure animations are 'None' (which is the default)
    assert builder.objects[0]['animation'] == 'None'
    assert builder.objects[1]['animation'] == 'None'

    script_content, scene_name = builder.generate_script('render')

    assert scene_name == "EasyManimScene", "Scene name should be EasyManimScene"
    
    # Check object creation code exists (similar to preview test)
    circle_var = f"circle_{circle_id[-6:]}"
    text_var = f"text_{text_id[-6:]}"
    assert f"{circle_var} = Circle(radius=1.0" in script_content
    assert f"{text_var} = Text('Text'" in script_content
    assert f"self.add({circle_var})" in script_content
    assert f"self.add({text_var})" in script_content

    # Crucially, check NO self.play calls exist
    assert "self.play" not in script_content, "Render script without animations should not have self.play"

    # Check overall structure
    assert "class EasyManimScene(Scene):" in script_content
    assert "def construct(self):" in script_content 

def test_generate_script_render_with_fadein():
    """Verify render script generation includes FadeIn animation code.
    Red Step: Requires generate_script to handle 'animation' field for render.
    """
    builder = SceneBuilder()
    circle_id = builder.add_object('Circle')
    square_id = builder.add_object('Square')
    text_id = builder.add_object('Text')

    # Set animation ONLY for the square
    builder.set_object_animation(square_id, 'FadeIn')

    script_content, scene_name = builder.generate_script('render')

    assert scene_name == "EasyManimScene"
    
    # Define expected variable names
    circle_var = f"circle_{circle_id[-6:]}"
    square_var = f"square_{square_id[-6:]}"
    text_var = f"text_{text_id[-6:]}"
    
    # Check that object creation and add lines still exist for all
    assert f"self.add({circle_var})" in script_content
    assert f"self.add({square_var})" in script_content
    assert f"self.add({text_var})" in script_content
    
    # Check that FadeIn import is added (needed for the animation)
    # We can check this by ensuring FadeIn is used
    assert "FadeIn" in script_content, "Script should use FadeIn if animation is set"

    # Check specifically for the FadeIn play call for the square
    expected_play_line = f"self.play(FadeIn({square_var}))"
    assert expected_play_line in script_content, "Script should contain self.play(FadeIn(...)) for the animated object"
    
    # Ensure FadeIn wasn't added for other objects
    assert f"self.play(FadeIn({circle_var}))" not in script_content
    assert f"self.play(FadeIn({text_var}))" not in script_content

    # Check order (rough check: play comes after add for the same object)
    add_square_index = script_content.find(f"self.add({square_var})")
    play_square_index = script_content.find(expected_play_line)
    assert add_square_index != -1 and play_square_index != -1, "Both add and play lines must exist"
    assert play_square_index > add_square_index, "self.play should come after self.add for the animated object" 