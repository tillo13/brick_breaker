"""
Game Renderer for Brick Breaker

This module provides utility functions for rendering game objects.
It's primarily used for generating preview images of levels or creating
server-side screenshots of the game state.
"""

import io
import base64
from PIL import Image, ImageDraw, ImageFont

def generate_level_preview(level_data, width=800, height=400):
    """
    Generate a preview image of a level
    
    Args:
        level_data: Dictionary containing level data
        width: Image width
        height: Image height
        
    Returns:
        Base64 encoded PNG image
    """
    # Create a new image with black background
    image = Image.new('RGB', (width, height), (0, 0, 30))
    draw = ImageDraw.Draw(image)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        title_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw level title
    level_name = level_data.get('name', f"Level {level_data.get('id', '1')}")
    draw.text((width // 2, 20), level_name, fill=(255, 220, 0), font=title_font, anchor="mt")
    
    # Draw bricks
    brick_colors = [
        (255, 50, 50),   # Red (strength 1)
        (255, 220, 0),   # Yellow (strength 2)
        (50, 255, 50),   # Green (strength 3)
        (50, 50, 255)    # Blue (strength 4+)
    ]
    
    bricks = level_data.get('bricks', [])
    for brick in bricks:
        x = brick.get('x', 0)
        y = brick.get('y', 0)
        strength = brick.get('strength', 1)
        color = brick_colors[min(strength, 4) - 1]
        
        # Draw brick rectangle
        draw.rectangle([x, y, x + 75, y + 20], fill=color, outline=(255, 255, 255))
        
        # If strength > 1, add number
        if strength > 1:
            draw.text((x + 37, y + 10), str(strength), fill=(255, 255, 255), font=font, anchor="mm")
    
    # Convert image to base64 encoded PNG
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_str}"

def generate_game_screenshot(game_state, width=800, height=600):
    """
    Generate a screenshot of the current game state
    
    Args:
        game_state: Dictionary containing game state
        width: Image width
        height: Image height
        
    Returns:
        Base64 encoded PNG image
    """
    # Create a new image with black background
    image = Image.new('RGB', (width, height), (0, 0, 30))
    draw = ImageDraw.Draw(image)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Draw UI elements
    # Lives
    draw.text((30, 20), f"Lives: {game_state.get('lives', 0)}", fill=(255, 255, 255), font=font)
    
    # Score
    draw.text((width - 150, 20), f"Score: {game_state.get('score', 0)}", fill=(255, 255, 255), font=font)
    
    # Level
    draw.text((width // 2, 20), f"Level: {game_state.get('level', 1)}", fill=(255, 255, 255), font=font, anchor="mt")
    
    # Draw paddle
    paddle = game_state.get('paddle', {})
    draw.rectangle([
        paddle.get('x', 0),
        paddle.get('y', height - 50),
        paddle.get('x', 0) + paddle.get('width', 100),
        paddle.get('y', height - 50) + paddle.get('height', 20)
    ], fill=(255, 255, 255))
    
    # Draw balls
    balls = game_state.get('balls', [])
    for ball in balls:
        x = ball.get('x', 0)
        y = ball.get('y', 0)
        size = ball.get('size', 15)
        
        # Draw ball
        draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255))
    
    # Draw bricks
    brick_colors = [
        (255, 50, 50),   # Red (strength 1)
        (255, 220, 0),   # Yellow (strength 2)
        (50, 255, 50),   # Green (strength 3)
        (50, 50, 255)    # Blue (strength 4+)
    ]
    
    bricks = game_state.get('bricks', [])
    for brick in bricks:
        if brick.get('broken', False):
            continue
            
        x = brick.get('x', 0)
        y = brick.get('y', 0)
        width = brick.get('width', 75)
        height = brick.get('height', 20)
        strength = brick.get('strength', 1)
        color = brick_colors[min(strength, 4) - 1]
        
        # Draw brick rectangle
        draw.rectangle([x, y, x + width, y + height], fill=color, outline=(255, 255, 255))
        
        # If strength > 1, add number
        if strength > 1:
            draw.text((x + width // 2, y + height // 2), str(strength), fill=(255, 255, 255), font=font, anchor="mm")
    
    # Draw powerups
    powerup_colors = [
        (50, 255, 50),    # Expand (green)
        (255, 50, 50),    # Shrink (red)
        (0, 255, 255),    # Multi (cyan)
        (50, 50, 255),    # Slow (blue)
        (255, 150, 0),    # Fast (orange)
        (255, 255, 0),    # Laser (yellow)
        (200, 0, 255),    # Life (purple)
        (255, 255, 0)     # Thru (yellow)
    ]
    
    powerup_symbols = ['+', '-', 'M', 'S', 'F', 'L', '♥', 'T']
    
    powerups = game_state.get('powerups', [])
    for powerup in powerups:
        if powerup.get('collected', False):
            continue
            
        x = powerup.get('x', 0)
        y = powerup.get('y', 0)
        size = powerup.get('size', 30)
        type_id = powerup.get('type', 0)
        
        color = powerup_colors[type_id]
        symbol = powerup_symbols[type_id]
        
        # Draw powerup rectangle
        draw.rectangle([x, y, x + size, y + size], fill=color, outline=(255, 255, 255))
        
        # Draw symbol
        draw.text((x + size // 2, y + size // 2), symbol, fill=(255, 255, 255), font=font, anchor="mm")
    
    # Draw lasers
    lasers = game_state.get('lasers', [])
    for laser in lasers:
        x = laser.get('x', 0)
        y = laser.get('y', 0)
        width = laser.get('width', 3)
        height = laser.get('height', 15)
        
        # Draw laser rectangle
        draw.rectangle([x, y, x + width, y + height], fill=(255, 0, 0))
    
    # Convert image to base64 encoded PNG
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_str}"