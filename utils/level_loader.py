"""
Level loader utility for Brick Breaker

This module provides functions to load and save level data.
"""

import os
import json
import random

def load_level(level_num, levels_dir='levels'):
    """
    Load a level from a JSON file
    
    Args:
        level_num: The level number to load
        levels_dir: Directory containing level files
        
    Returns:
        Dictionary containing level data
    """
    level_file = f"level-{level_num}.json"
    level_path = os.path.join(levels_dir, level_file)
    
    if not os.path.exists(level_path):
        # If level file doesn't exist, generate a level
        return generate_level(level_num)
    
    try:
        with open(level_path, 'r') as f:
            level_data = json.load(f)
            
        # Check if this is an editor-created level
        if 'editor_version' in level_data and level_data['editor_version']:
            print(f"Loading editor-created level {level_num}")
            # For editor levels, ensure all brick properties are explicit
            if 'bricks' in level_data:
                for brick in level_data['bricks']:
                    # Ensure has_powerup is a boolean value
                    if 'has_powerup' not in brick:
                        brick['has_powerup'] = False
                        
                    # If a brick has a powerup, ensure powerup_type is set
                    if brick['has_powerup'] and 'powerup_type' not in brick:
                        brick['powerup_type'] = 0
                        
                    # Mark this brick as editor-placed
                    brick['editor_placed'] = True
        else:
            print(f"Loading standard level {level_num}")
            # For regular levels, do normal processing
            
        return level_data
    except Exception as e:
        print(f"Error loading level {level_num}: {e}")
        return generate_level(level_num)


def save_level(level_data, level_num, levels_dir='levels', editor_mode=False):
    """
    Save level data to a JSON file
    
    Args:
        level_data: Dictionary containing level data
        level_num: The level number to save
        levels_dir: Directory to save level files
        editor_mode: Whether this level is saved from the editor
    """
    # Ensure the directory exists
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
    
    # Normalize level ID to ensure consistent format
    level_data['id'] = f"level-{level_num}"
    
    # Add editor flag if in editor mode
    if editor_mode:
        level_data['editor_version'] = True
    elif 'editor_version' not in level_data:
        level_data['editor_version'] = False
        
    # Process bricks based on mode
    if 'bricks' in level_data:
        for brick in level_data['bricks']:
            # For editor mode, ensure all properties are explicitly set
            if editor_mode:
                brick['editor_placed'] = True
                
                # Ensure has_powerup is set
                if 'has_powerup' not in brick:
                    brick['has_powerup'] = False
                    
                # Ensure powerup_type is set if has_powerup is True
                if brick['has_powerup'] and 'powerup_type' not in brick:
                    brick['powerup_type'] = 0
            else:
                # For game-generated levels, set default values
                if 'has_powerup' not in brick:
                    brick['has_powerup'] = random.random() < 0.3
                    
                if brick['has_powerup'] and 'powerup_type' not in brick:
                    brick['powerup_type'] = random.randint(0, 7)
    
    level_file = f"level-{level_num}.json"
    level_path = os.path.join(levels_dir, level_file)
    
    with open(level_path, 'w') as f:
        json.dump(level_data, f, indent=2)


def save_editor_level(level_data, level_num, levels_dir='levels'):
    """
    Save level data from the editor with explicit settings
    
    Args:
        level_data: Dictionary containing level data
        level_num: The level number to save
        levels_dir: Directory to save level files
    """
    # Call the normal save function with editor_mode=True
    save_level(level_data, level_num, levels_dir, editor_mode=True)


def generate_level(level_num, screen_width=800, screen_height=600):
    """
    Generate a level programmatically
    
    Args:
        level_num: The level number to generate
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        
    Returns:
        Dictionary containing generated level data
    """
    brick_width = 75
    brick_height = 20
    brick_gap = 2
    brick_rows = 6
    brick_cols = 10
    
    bricks = []
    
    if level_num == 1:
        # Calculate total width of all bricks plus gaps
        total_width = brick_cols * brick_width + (brick_cols - 1) * brick_gap
        # Calculate starting x position to center bricks horizontally
        start_x = (screen_width - total_width) // 2
        
        # Simple rows with proper alignment and centering
        for row in range(brick_rows):
            for col in range(brick_cols):
                # Calculate positions with proper centering
                x = start_x + col * (brick_width + brick_gap)
                y = row * (brick_height + brick_gap) + 50
                # First row has strength 1, then 2, then 3...
                strength = min(row + 1, 4) 
                
                # Randomly decide if this brick has a powerup
                has_powerup = random.random() < 0.3
                powerup_type = random.randint(0, 7) if has_powerup else 0
                
                bricks.append({
                    "x": x,
                    "y": y,
                    "strength": strength,
                    "has_powerup": has_powerup,
                    "powerup_type": powerup_type
                })
    
    elif level_num == 2:
        # Diamond pattern
        center_col = brick_cols // 2
        center_row = brick_rows // 2
        for row in range(brick_rows+2):
            for col in range(brick_cols+2):
                # Calculate distance from center
                dist = abs(col - center_col) + abs(row - center_row)
                if dist <= brick_rows:
                    x = col * (brick_width + brick_gap) + 25
                    y = row * (brick_height + brick_gap) + 40
                    # Outer bricks have higher strength
                    strength = max(1, 4 - dist // 2)
                    
                    # Randomly decide if this brick has a powerup
                    has_powerup = random.random() < 0.3
                    powerup_type = random.randint(0, 7) if has_powerup else 0
                    
                    bricks.append({
                        "x": x,
                        "y": y,
                        "strength": strength,
                        "has_powerup": has_powerup,
                        "powerup_type": powerup_type
                    })
    
    elif level_num == 3:
        # Checkerboard pattern
        for row in range(brick_rows+2):
            for col in range(brick_cols+2):
                if (row + col) % 2 == 0:
                    x = col * (brick_width + brick_gap) + 25
                    y = row * (brick_height + brick_gap) + 40
                    strength = random.randint(1, 3)
                    
                    # Randomly decide if this brick has a powerup
                    has_powerup = random.random() < 0.3
                    powerup_type = random.randint(0, 7) if has_powerup else 0
                    
                    bricks.append({
                        "x": x,
                        "y": y,
                        "strength": strength,
                        "has_powerup": has_powerup,
                        "powerup_type": powerup_type
                    })
    
    else:
        # Random level - higher number means more difficult
        for row in range(brick_rows+level_num//2):
            for col in range(brick_cols):
                if random.random() < 0.8:  # 80% chance of a brick
                    x = col * (brick_width + brick_gap) + 50
                    y = row * (brick_height + brick_gap) + 40
                    # Higher chance of strong bricks in later levels
                    strength = random.choices([1, 2, 3, 4], 
                                            weights=[5-level_num//2, level_num, level_num//2, level_num//3],
                                            k=1)[0]
                    strength = max(1, min(strength, 4))  # Clamp between 1-4
                    
                    # Randomly decide if this brick has a powerup
                    has_powerup = random.random() < 0.3
                    powerup_type = random.randint(0, 7) if has_powerup else 0
                    
                    bricks.append({
                        "x": x,
                        "y": y,
                        "strength": strength,
                        "has_powerup": has_powerup,
                        "powerup_type": powerup_type
                    })
    
    # Mark this as a generated level, not an editor level
    return {
        "id": f"level-{level_num}",
        "name": f"Level {level_num}",
        "editor_version": False,
        "bricks": bricks
    }

def create_sample_levels(levels_dir='levels', num_levels=3):
    """
    Create sample level files
    
    Args:
        levels_dir: Directory to save level files
        num_levels: Number of sample levels to create
    """
    # Ensure the directory exists
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
    
    # Generate and save sample levels
    for level in range(1, num_levels + 1):
        level_data = generate_level(level)
        save_level(level_data, level, levels_dir)