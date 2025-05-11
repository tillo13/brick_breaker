"""
Game Objects for Brick Breaker

This module defines the game objects used in the Brick Breaker game.
"""

import random
import math
import time

class Rect:
    """Simple rectangle for collision detection"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def colliderect(self, other):
        """Check if this rectangle collides with another"""
        return (
            self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y
        )

class Paddle:
    """Player-controlled paddle that bounces the ball"""
    
    def __init__(self, screen_width, screen_height):
        self.original_width = 100  # Default paddle width
        self.width = self.original_width
        self.height = 20
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 50
        self.speed = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.use_mouse = True
        self.laser_active = False
        self.laser_time = 0
        self.laser_cooldown = 0.5  # Seconds between laser shots
        self.last_laser_time = 0
        self.screen_width = screen_width
        self.move_left = False
        self.move_right = False
    
    def set_direction(self, left, right):
        """Set movement direction based on keyboard input"""
        self.move_left = left
        self.move_right = right
    
    def set_position_from_mouse(self, mouse_x):
        """Set paddle position based on mouse input"""
        self.x = mouse_x - self.width // 2
        # Keep paddle within screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x > self.screen_width - self.width:
            self.x = self.screen_width - self.width
        self.rect.x = self.x
    
    def update(self, dt, input_data=None):
        """Update paddle position"""
        if self.use_mouse and input_data and 'mouse_x' in input_data:
            # Mouse control (handled in set_position_from_mouse)
            pass
        else:
            # Keyboard control
            if self.move_left:
                self.x -= self.speed
            if self.move_right:
                self.x += self.speed
            
            # Keep paddle within screen bounds
            if self.x < 0:
                self.x = 0
            elif self.x > self.screen_width - self.width:
                self.x = self.screen_width - self.width
        
        # Update rectangle position
        self.rect.x = self.x
        
        # Countdown laser time
        if self.laser_active:
            self.laser_time -= dt
            if self.laser_time <= 0:
                self.laser_active = False
    
    def shoot_laser(self, dt):
        """Create laser objects if cooldown allows"""
        current_time = time.time()
        if self.laser_active and current_time - self.last_laser_time >= self.laser_cooldown:
            self.last_laser_time = current_time
            return [
                Laser(self.x + 12, self.y - 10),
                Laser(self.x + self.width - 12, self.y - 10)
            ]
        return []

class Laser:
    """Laser projectile fired from the paddle"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.width = 3
        self.height = 15
        self.rect = Rect(self.x, self.y, self.width, self.height)
    
    def update(self, dt):
        """Update laser position"""
        self.y -= self.speed
        self.rect.y = self.y

class Ball:
    """Ball that bounces around and breaks bricks"""
    
    def __init__(self, screen_width, screen_height, x=None, y=None, speed_x=None, speed_y=None):
        self.size = 15  # Ball diameter
        self.x = x if x is not None else screen_width // 2
        self.y = y if y is not None else screen_height // 2
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # If speed is not provided, give a random direction
        if speed_x is None or speed_y is None:
            angle = random.uniform(math.pi/4, 3*math.pi/4)  # Angle between 45 and 135 degrees
            speed = random.uniform(4, 5)
            self.speed_x = speed * math.cos(angle)
            self.speed_y = -speed * math.sin(angle)  # Negative for upward movement
        else:
            self.speed_x = speed_x
            self.speed_y = speed_y
            
        self.rect = Rect(self.x, self.y, self.size, self.size)
        self.active = False
        self.thru = False
    
    def update(self, dt):
        """Update ball position"""
        if self.active:
            # Move the ball
            self.x += self.speed_x
            self.y += self.speed_y
            
            # Update rectangle position
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
    
    def stick_to_paddle(self, paddle):
        """Position the ball on top of the paddle when not active"""
        self.x = paddle.x + paddle.width // 2 - self.size // 2
        self.y = paddle.y - self.size
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def handle_wall_collision(self, screen_width, screen_height):
        """Handle collisions with screen boundaries"""
        if self.x <= 0 or self.x >= screen_width - self.size:
            self.speed_x = -self.speed_x
        if self.y <= 0:
            self.speed_y = -self.speed_y
    
    def handle_paddle_collision(self, paddle):
        """Handle collision with the paddle"""
        # Calculate where on the paddle the ball hit
        hit_pos = (self.x + self.size // 2) - paddle.x
        hit_ratio = hit_pos / paddle.width
        
        # Angle the ball based on where it hit (between -60 and 60 degrees)
        angle = (hit_ratio - 0.5) * (2*math.pi/3)
        
        # Speed increases slightly with each paddle hit
        speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        speed = min(speed * 1.05, 12)  # Cap max speed
        
        # Set new velocity
        self.speed_x = speed * math.sin(angle)
        self.speed_y = -speed * math.cos(angle)
    
    def handle_brick_collision(self, brick):
        """Handle collision with a brick"""
        # Calculate which side of the brick was hit
        dx_entry = (self.rect.x + self.rect.width - brick.rect.x) if self.speed_x > 0 else (brick.rect.x + brick.rect.width - self.rect.x)
        dy_entry = (self.rect.y + self.rect.height - brick.rect.y) if self.speed_y > 0 else (brick.rect.y + brick.rect.height - self.rect.y)
        
        if dx_entry < dy_entry:
            # Horizontal collision
            self.speed_x = -self.speed_x
        else:
            # Vertical collision
            self.speed_y = -self.speed_y

class Brick:
    """Breakable brick that can contain a powerup"""
    
    def __init__(self, x, y, strength=1, powerup_chance=0.3):
        self.width = 75
        self.height = 20
        self.x = x
        self.y = y
        self.strength = strength  # Number of hits to break
        self.max_strength = strength  # Remember initial strength
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.broken = False
        
        # Initialize powerup properties but don't randomize
        # These will be set explicitly in level loading if needed
        self.has_powerup = False
        self.powerup_type = None
        self.editor_placed = False  # Flag for editor-placed bricks
        
        # Only randomly assign powerups for non-editor bricks if not explicitly set
        if not self.editor_placed and random.random() < powerup_chance:
            self.has_powerup = True
            self.powerup_type = random.randint(0, 7)
    
    def hit(self, ball=None):
        """Reduce brick strength when hit"""
        # If ball has thru ability, break brick immediately
        if ball and ball.thru:
            self.strength = 0
        else:
            self.strength -= 1
        
        if self.strength <= 0:
            self.broken = True
            return True  # Brick is broken
        return False  # Brick is damaged but not broken

class Powerup:
    """Collectable powerup that provides special abilities"""
    
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.size = 30
        self.speed = 3
        self.rect = Rect(self.x, self.y, self.size, self.size)
        self.collected = False
        self.angle = 0  # For rotation effect in visual rendering
    
    def update(self, dt):
        """Update powerup position"""
        if not self.collected:
            self.y += self.speed
            self.rect.y = self.y
            self.angle = (self.angle + 2) % 360  # For visual rotation