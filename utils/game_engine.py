"""
Game Engine for Brick Breaker

This module provides the core game logic for the Brick Breaker game.
It's designed to work with both the Flask web app and potentially
other frontends.
"""

import math
import random
import json
import os
from .game_objects import Ball, Paddle, Brick, Powerup, Laser

class GameEngine:
    """Main game engine that manages the game state and logic"""
    
    def __init__(self, config=None):
        """Initialize the game engine with optional configuration"""
        # Default configuration
        self.config = config or {}
        self.screen_width = self.config.get('SCREEN_WIDTH', 800)
        self.screen_height = self.config.get('SCREEN_HEIGHT', 600)
        self.fps = self.config.get('FPS', 60)
        
        # Game state
        self.lives = 3
        self.score = 0
        self.level = 1
        self.high_score = 0
        self.game_over = False
        self.level_complete = False
        self.paused = False
        
        # Game objects
        self.paddle = None
        self.balls = []
        self.bricks = []
        self.powerups = []
        self.lasers = []
        self.particles = []
        
        # Flag to track if current level was created in the editor
        self.is_editor_level = False
        
        # Initialize game objects
        self.reset_level()
    
    def reset_level(self):
        """Reset the level, keeping score and lives"""
        self.paddle = Paddle(self.screen_width, self.screen_height)
        self.balls = [Ball(self.screen_width, self.screen_height)]
        self.bricks = []
        self.powerups = []
        self.lasers = []
        self.particles = []
        self.paused = False
        self.level_complete = False
        self.is_editor_level = False
        
        # Load level data
        self.load_level(self.level)
    
    def reset_game(self):
        """Reset the entire game"""
        self.lives = 3
        self.score = 0
        self.level = 1
        self.game_over = False
        self.is_editor_level = False
        self.reset_level()
    
    def load_level(self, level_num):
        """Load a level from a JSON file"""
        try:
            level_file = f"level-{level_num}.json"
            level_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'levels', level_file)
            
            if os.path.exists(level_path):
                with open(level_path, 'r') as f:
                    level_data = json.load(f)
                    print(f"Loading level {level_num} from {level_path}")
                
                # Check if this is an editor-created level
                self.is_editor_level = level_data.get('editor_version', False)
                
                if self.is_editor_level:
                    print(f"Loading editor-created level {level_num}")
                else:
                    print(f"Loading standard level {level_num}")
                
                # Process bricks data
                if 'bricks' in level_data:
                    print(f"Found {len(level_data['bricks'])} bricks in level data")
                    for brick_data in level_data['bricks']:
                        # Create the brick
                        brick = Brick(
                            brick_data['x'], 
                            brick_data['y'],
                            brick_data.get('strength', 1),
                            0.0 if self.is_editor_level else 0.3  # No random powerups in editor levels
                        )
                        
                        # Handle powerup settings
                        if self.is_editor_level or brick_data.get('editor_placed', False):
                            # For editor levels, explicitly set powerup properties from data
                            brick.has_powerup = brick_data.get('has_powerup', False)
                            if brick.has_powerup:
                                brick.powerup_type = brick_data.get('powerup_type', 0)
                                print(f"Editor brick at ({brick.x}, {brick.y}) has powerup type {brick.powerup_type}")
                        else:
                            # For non-editor bricks, use properties from the JSON
                            brick.has_powerup = brick_data.get('has_powerup', False)
                            if brick.has_powerup:
                                brick.powerup_type = brick_data.get('powerup_type', 0)
                                print(f"Brick at ({brick.x}, {brick.y}) has powerup type {brick.powerup_type}")
                        
                        self.bricks.append(brick)
            else:
                # If level file doesn't exist, generate level programmatically
                print(f"Level file {level_path} not found, generating level")
                self.generate_level(level_num)
        
        except Exception as e:
            print(f"Error loading level {level_num}: {e}")
            # Fall back to generated level
            self.generate_level(level_num)
    
    def generate_level(self, level):
        """Generate a level programmatically"""
        # Default brick properties
        brick_width = 75
        brick_height = 20
        brick_gap = 2
        brick_rows = 6
        brick_cols = 10
        
        if level == 1:
            self._generate_simple_rows_level(brick_width, brick_height, brick_gap, brick_rows, brick_cols)
        elif level == 2:
            self._generate_diamond_pattern_level(brick_width, brick_height, brick_gap, brick_rows, brick_cols)
        elif level == 3:
            self._generate_checkerboard_level(brick_width, brick_height, brick_gap, brick_rows, brick_cols)
        else:
            self._generate_random_level(brick_width, brick_height, brick_gap, brick_rows, brick_cols, level)
        
        # Generated levels are not editor levels
        self.is_editor_level = False
    
    def _generate_simple_rows_level(self, brick_width, brick_height, brick_gap, brick_rows, brick_cols):
        """Generate a simple rows layout (Level 1)"""
        # Calculate total width of all bricks plus gaps
        total_width = brick_cols * brick_width + (brick_cols - 1) * brick_gap
        # Calculate starting x position to center bricks horizontally
        start_x = (self.screen_width - total_width) // 2
        
        # Simple rows with proper alignment and centering
        for row in range(brick_rows):
            for col in range(brick_cols):
                # Calculate positions with proper centering
                x = start_x + col * (brick_width + brick_gap)
                y = row * (brick_height + brick_gap) + 50
                # First row has strength 1, then 2, then 3...
                strength = min(row + 1, 4) 
                self.bricks.append(Brick(x, y, strength))
    
    def _generate_diamond_pattern_level(self, brick_width, brick_height, brick_gap, brick_rows, brick_cols):
        """Generate a diamond pattern layout (Level 2)"""
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
                    self.bricks.append(Brick(x, y, strength))
    
    def _generate_checkerboard_level(self, brick_width, brick_height, brick_gap, brick_rows, brick_cols):
        """Generate a checkerboard pattern layout (Level 3)"""
        for row in range(brick_rows+2):
            for col in range(brick_cols+2):
                if (row + col) % 2 == 0:
                    x = col * (brick_width + brick_gap) + 25
                    y = row * (brick_height + brick_gap) + 40
                    strength = random.randint(1, 3)
                    self.bricks.append(Brick(x, y, strength))
    
    def _generate_random_level(self, brick_width, brick_height, brick_gap, brick_rows, brick_cols, level):
        """Generate a random layout (higher levels)"""
        for row in range(brick_rows + level//2):
            for col in range(brick_cols):
                if random.random() < 0.8:  # 80% chance of a brick
                    x = col * (brick_width + brick_gap) + 50
                    y = row * (brick_height + brick_gap) + 40
                    # Higher chance of strong bricks in later levels
                    strength = random.choices(
                        [1, 2, 3, 4], 
                        weights=[5-level//2, level, level//2, level//3],
                        k=1
                    )[0]
                    strength = max(1, min(strength, 4))  # Clamp between 1-4
                    self.bricks.append(Brick(x, y, strength))
    
    def save_level_to_json(self, level_num):
        """Save the current level layout to a JSON file"""
        level_data = {
            "id": f"level-{level_num}",
            "name": f"Level {level_num}",
            "editor_version": self.is_editor_level,
            "bricks": []
        }
        
        for brick in self.bricks:
            brick_data = {
                "x": brick.x,
                "y": brick.y,
                "strength": brick.strength,
                "has_powerup": brick.has_powerup,
                "powerup_type": brick.powerup_type if brick.has_powerup else 0
            }
            level_data["bricks"].append(brick_data)
        
        # Ensure the levels directory exists
        levels_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'levels')
        if not os.path.exists(levels_dir):
            os.makedirs(levels_dir)
        
        # Save the level data
        level_file = f"level-{level_num}.json"
        level_path = os.path.join(levels_dir, level_file)
        
        with open(level_path, 'w') as f:
            json.dump(level_data, f, indent=2)
    
    def update(self, dt, input_data=None):
        """Update game state for a single frame"""
        if self.paused:
            return
        
        # Process input if provided
        if input_data:
            self.process_input(input_data)
        
        # Update paddle
        self.paddle.update(dt, input_data)
        
        # Check if we should shoot lasers
        if self.paddle.laser_active:
            new_lasers = self.paddle.shoot_laser(dt)
            if new_lasers:
                self.lasers.extend(new_lasers)
        
        # Update all game objects
        self.update_lasers(dt)
        self.update_balls(dt)
        self.update_powerups(dt)
        self.update_particles(dt)
        
        # Check if level is complete (all bricks destroyed)
        if len(self.bricks) == 0 and not self.level_complete:
            self.level_complete = True
            # Add score bonus for completing the level
            self.score += 100 * self.level
            # Note: We don't automatically increment level or reset here anymore
            # That will be handled by the frontend when the player clicks "Next Level"
    
    def advance_to_next_level(self):
        """Advance to the next level (called from frontend)"""
        self.level += 1
        self.reset_level()
    
    def process_input(self, input_data):
        """Process user input"""
        # Toggle pause
        if input_data.get('pause_pressed'):
            self.paused = not self.paused
        
        # Launch ball
        if input_data.get('launch_pressed'):
            for ball in self.balls:
                ball.active = True
        
        # Toggle control mode
        if input_data.get('toggle_control_pressed'):
            self.paddle.use_mouse = not self.paddle.use_mouse
        
        # Update paddle position
        if self.paddle.use_mouse and 'mouse_x' in input_data:
            self.paddle.set_position_from_mouse(input_data['mouse_x'])
        else:
            self.paddle.set_direction(
                input_data.get('left_pressed', False),
                input_data.get('right_pressed', False)
            )
    
    def update_lasers(self, dt):
        """Update all lasers"""
        for laser in self.lasers[:]:
            laser.update(dt)
            
            # Check if laser is off screen
            if laser.y < 0:
                self.lasers.remove(laser)
                continue
                
            # Check laser-brick collisions
            self._check_laser_brick_collisions(laser)
    
    def _check_laser_brick_collisions(self, laser):
        """Handle collisions between lasers and bricks"""
        for brick in self.bricks[:]:
            if laser.rect.colliderect(brick.rect):
                # Brick hit by laser
                brick_broken = brick.hit()
                
                if brick_broken:
                    self._handle_brick_destruction(brick)
                
                # Remove the laser
                if laser in self.lasers:
                    self.lasers.remove(laser)
                break
    
    def update_balls(self, dt):
        """Update all balls"""
        for ball in self.balls[:]:
            # Skip if the ball is not active
            if not ball.active:
                ball.stick_to_paddle(self.paddle)
                continue
            
            # Update ball position
            ball.update(dt)
            
            # Check if ball is lost
            if ball.y >= self.screen_height:
                self._handle_ball_lost(ball)
                continue
            
            # Check for ball-wall collisions
            ball.handle_wall_collision(self.screen_width, self.screen_height)
            
            # Check for ball-paddle collisions
            if ball.rect.colliderect(self.paddle.rect) and ball.speed_y > 0:
                ball.handle_paddle_collision(self.paddle)
            
            # Check for ball-brick collisions
            self._check_ball_brick_collisions(ball)
    
    def _handle_ball_lost(self, ball):
        """Handle a ball falling off the bottom of the screen"""
        if len(self.balls) <= 1:
            # Last ball lost - lose a life
            self.lives -= 1
            
            if self.lives <= 0:
                # Game over
                self.high_score = max(self.high_score, self.score)
                self.game_over = True
            else:
                # Just reset ball
                self.balls = [Ball(self.screen_width, self.screen_height)]
        else:
            # Remove just this ball
            self.balls.remove(ball)
    
    def _check_ball_brick_collisions(self, ball):
        """Handle collisions between balls and bricks"""
        for brick in self.bricks[:]:
            if ball.rect.colliderect(brick.rect) and not brick.broken:
                # Skip collision check if ball has thru ability
                if not ball.thru:
                    ball.handle_brick_collision(brick)
                
                # Damage/Break the brick
                brick_broken = brick.hit(ball)
                
                if brick_broken:
                    self._handle_brick_destruction(brick)
                
                # If ball has thru ability, continue to next brick
                # Otherwise, break after the first collision
                if not ball.thru:
                    break
    
    def _handle_brick_destruction(self, brick):
        """Handle a brick being destroyed"""
        # Create particles
        self.create_particles(
            brick.x + brick.width // 2,
            brick.y + brick.height // 2
        )
        
        # Create powerup - RESPECT EDITOR SETTINGS
        if brick.has_powerup:
            # Editor bricks should always drop their powerup as specified
            self.powerups.append(Powerup(
                brick.x + brick.width // 2 - 15,
                brick.y + brick.height,
                brick.powerup_type
            ))
            
        # Add score
        self.score += 10 * brick.max_strength
        
        # Remove the brick
        self.bricks.remove(brick)
    
    def update_powerups(self, dt):
        """Update all powerups"""
        for powerup in self.powerups[:]:
            # Update and check if off screen
            powerup.update(dt)
            if powerup.y > self.screen_height:
                self.powerups.remove(powerup)
                continue
                
            # Check for paddle collision
            if powerup.rect.colliderect(self.paddle.rect) and not powerup.collected:
                powerup.collected = True
                self.apply_powerup(powerup)
                self.powerups.remove(powerup)
    
    def apply_powerup(self, powerup):
        """Apply a powerup effect"""
        # Powerup effects from the original code
        if powerup.type == 0:  # POWERUP_EXPAND
            # Expand paddle
            self.paddle.width = min(self.paddle.original_width * 2, self.screen_width // 2)
            self.paddle.rect.width = self.paddle.width
            # Re-center the paddle
            self.paddle.x = max(0, min(self.paddle.x, self.screen_width - self.paddle.width))
            
        elif powerup.type == 1:  # POWERUP_SHRINK
            # Shrink paddle (negative powerup)
            self.paddle.width = max(self.paddle.original_width // 2, 30)
            self.paddle.rect.width = self.paddle.width
            
        elif powerup.type == 2:  # POWERUP_MULTI
            # Add 2 extra balls
            for _ in range(2):
                # Create a new ball with random direction
                first_ball = self.balls[0]
                new_ball = Ball(self.screen_width, self.screen_height)
                new_ball.x = first_ball.x
                new_ball.y = first_ball.y
                new_ball.speed_x = first_ball.speed_x * random.uniform(0.8, 1.2)
                new_ball.speed_y = first_ball.speed_y * random.uniform(0.8, 1.2)
                new_ball.active = True
                self.balls.append(new_ball)
                
        elif powerup.type == 3:  # POWERUP_SLOW
            # Slow all balls down
            for ball in self.balls:
                speed = math.sqrt(ball.speed_x**2 + ball.speed_y**2)
                direction_x = ball.speed_x / speed
                direction_y = ball.speed_y / speed
                new_speed = max(2, speed * 0.7)  # Slow down but maintain min speed
                ball.speed_x = direction_x * new_speed
                ball.speed_y = direction_y * new_speed
                
        elif powerup.type == 4:  # POWERUP_FAST
            # Speed balls up (negative powerup)
            for ball in self.balls:
                speed = math.sqrt(ball.speed_x**2 + ball.speed_y**2)
                direction_x = ball.speed_x / speed
                direction_y = ball.speed_y / speed
                new_speed = min(10, speed * 1.5)  # Speed up but cap at max
                ball.speed_x = direction_x * new_speed
                ball.speed_y = direction_y * new_speed
                
        elif powerup.type == 5:  # POWERUP_LASER
            # Activate lasers
            self.paddle.laser_active = True
            self.paddle.laser_time = 10  # 10 seconds
            
        elif powerup.type == 6:  # POWERUP_LIFE
            # Extra life
            self.lives += 1
            
        elif powerup.type == 7:  # POWERUP_THRU
            # Ball goes through bricks
            for ball in self.balls:
                ball.thru = True
    
    def create_particles(self, x, y, count=10):
        """Create particles for visual effects"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            size = random.randint(2, 6)
            lifetime = random.uniform(0.5, 2.0) * self.fps
            color = (
                random.randint(150, 255),
                random.randint(150, 255),
                random.randint(150, 255)
            )
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'lifetime': lifetime
            })
    
    def update_particles(self, dt):
        """Update and remove expired particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['lifetime'] -= 1
            
            # Remove expired particles
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def get_game_state(self):
        """Return the current game state as a dictionary"""
        return {
            'lives': self.lives,
            'score': self.score,
            'level': self.level,
            'high_score': self.high_score,
            'game_over': self.game_over,
            'level_complete': self.level_complete,
            'paused': self.paused,
            'is_editor_level': self.is_editor_level,
            'paddle': {
                'x': self.paddle.x,
                'y': self.paddle.y,
                'width': self.paddle.width,
                'height': self.paddle.height,
                'laser_active': self.paddle.laser_active
            },
            'balls': [{
                'x': ball.x,
                'y': ball.y,
                'size': ball.size,
                'active': ball.active,
                'thru': ball.thru
            } for ball in self.balls],
            'bricks': [{
                'x': brick.x,
                'y': brick.y,
                'width': brick.width,
                'height': brick.height,
                'strength': brick.strength,
                'max_strength': brick.max_strength,
                'broken': brick.broken,
                'has_powerup': brick.has_powerup,
                'powerup_type': brick.powerup_type if brick.has_powerup else 0
            } for brick in self.bricks],
            'powerups': [{
                'x': powerup.x,
                'y': powerup.y,
                'type': powerup.type,
                'size': powerup.size,
                'collected': powerup.collected
            } for powerup in self.powerups],
            'lasers': [{
                'x': laser.x,
                'y': laser.y,
                'width': laser.width,
                'height': laser.height
            } for laser in self.lasers],
            'particles': self.particles  # Already in a suitable format
        }