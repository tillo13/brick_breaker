import pygame
import sys
import random
import math
import time

# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
BALL_SIZE = 15
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_GAP = 2
POWERUP_SIZE = 30
POWERUP_SPEED = 3
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 150, 0)
PURPLE = (200, 0, 255)
CYAN = (0, 255, 255)
PINK = (255, 150, 150)
COLORS = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]

# macOS optimization
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Brick Breaker Deluxe")
clock = pygame.time.Clock()

# Try to load sounds - with error handling in case files don't exist
try:
    bounce_sound = pygame.mixer.Sound("bounce.wav")
    brick_sound = pygame.mixer.Sound("brick.wav")
    powerup_sound = pygame.mixer.Sound("powerup.wav")
    life_lost_sound = pygame.mixer.Sound("life_lost.wav")
    level_complete_sound = pygame.mixer.Sound("level_complete.wav")
except:
    # If sounds can't be loaded, create dummy sound objects
    bounce_sound = pygame.mixer.Sound(buffer=bytes(100))
    brick_sound = pygame.mixer.Sound(buffer=bytes(100))
    powerup_sound = pygame.mixer.Sound(buffer=bytes(100))
    life_lost_sound = pygame.mixer.Sound(buffer=bytes(100))
    level_complete_sound = pygame.mixer.Sound(buffer=bytes(100))
    print("Sound files not found - game will run without sound")

# Try to load fonts
try:
    font_sm = pygame.font.Font(None, 24)
    font_md = pygame.font.Font(None, 36)
    font_lg = pygame.font.Font(None, 72)
except:
    # Fall back to default system font if needed
    font_sm = pygame.font.SysFont(None, 24)
    font_md = pygame.font.SysFont(None, 36) 
    font_lg = pygame.font.SysFont(None, 72)

# Powerup types
POWERUP_EXPAND = 0      # Expand paddle
POWERUP_SHRINK = 1      # Shrink paddle (negative powerup)
POWERUP_MULTI = 2       # Add extra balls
POWERUP_SLOW = 3        # Slow ball down
POWERUP_FAST = 4        # Speed ball up (negative powerup)
POWERUP_LASER = 5       # Shoot lasers
POWERUP_LIFE = 6        # Extra life
POWERUP_THRU = 7        # Ball goes through bricks

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.use_mouse = True
        self.laser_active = False
        self.laser_time = 0
        self.laser_cooldown = 0.5  # Seconds between laser shots
        self.last_laser_time = 0
        
    def draw(self):
        # Draw paddle
        pygame.draw.rect(screen, WHITE, self.rect)
        
        # Draw laser cannons if active
        if self.laser_active:
            pygame.draw.rect(screen, RED, (self.x + 10, self.y - 5, 5, 10))
            pygame.draw.rect(screen, RED, (self.x + self.width - 15, self.y - 5, 5, 10))
        
    def update(self):
        if self.use_mouse:
            # Mouse control
            mouse_x, _ = pygame.mouse.get_pos()
            self.x = mouse_x - self.width // 2
        else:
            # Keyboard control
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.x += self.speed
        
        # Keep paddle within screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        
        # Update rectangle position
        self.rect.x = self.x
        
        # Countdown laser time
        if self.laser_active:
            self.laser_time -= 1/FPS
            if self.laser_time <= 0:
                self.laser_active = False
    
    def shoot_laser(self):
        current_time = time.time()
        if self.laser_active and current_time - self.last_laser_time >= self.laser_cooldown:
            self.last_laser_time = current_time
            return [
                Laser(self.x + 12, self.y - 10),
                Laser(self.x + self.width - 12, self.y - 10)
            ]
        return []

class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.width = 3
        self.height = 15
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
        
    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

class Ball:
    def __init__(self, x=None, y=None, speed_x=None, speed_y=None):
        self.size = BALL_SIZE
        self.x = x if x is not None else SCREEN_WIDTH // 2
        self.y = y if y is not None else SCREEN_HEIGHT // 2
        
        # If speed is not provided, give a random direction
        if speed_x is None or speed_y is None:
            angle = random.uniform(math.pi/4, 3*math.pi/4)  # Angle between 45 and 135 degrees
            speed = random.uniform(4, 5)
            self.speed_x = speed * math.cos(angle)
            self.speed_y = -speed * math.sin(angle)  # Negative for upward movement
        else:
            self.speed_x = speed_x
            self.speed_y = speed_y
            
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.active = False
        self.thru = False
        
    def draw(self):
        if self.thru:
            # Draw a glowing effect for thru-ball
            for i in range(3, 0, -1):
                alpha = 100 - i * 30
                s = pygame.Surface((self.size + i*4, self.size + i*4), pygame.SRCALPHA)
                s.fill((255, 200, 0, alpha))
                screen.blit(s, (self.x + self.size//2 - (self.size + i*4)//2, 
                               self.y + self.size//2 - (self.size + i*4)//2))
            
            # Draw the ball
            pygame.draw.circle(screen, YELLOW, 
                              (int(self.x + self.size // 2), int(self.y + self.size // 2)), 
                              self.size // 2)
        else:
            # Regular ball
            pygame.draw.circle(screen, WHITE, 
                              (int(self.x + self.size // 2), int(self.y + self.size // 2)), 
                              self.size // 2)
        
    def update(self, paddle, bricks, powerups, lasers=None):
        if not self.active:
            # If ball is not active, stick to paddle
            self.x = paddle.x + paddle.width // 2 - self.size // 2
            self.y = paddle.y - self.size
        else:
            # Move the ball
            self.x += self.speed_x
            self.y += self.speed_y
            
            # Wall collision
            if self.x <= 0 or self.x >= SCREEN_WIDTH - self.size:
                self.speed_x = -self.speed_x
                bounce_sound.play()
            if self.y <= 0:
                self.speed_y = -self.speed_y
                bounce_sound.play()
            
            # Paddle collision
            if self.rect.colliderect(paddle.rect) and self.speed_y > 0:
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
                
                bounce_sound.play()
        
        # Update rectangle position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        return self.y >= SCREEN_HEIGHT  # Return True if ball is lost

class Brick:
    def __init__(self, x, y, strength=1, powerup_chance=0.3):
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.x = x
        self.y = y
        self.strength = strength  # Number of hits to break
        self.max_strength = strength  # Remember initial strength
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.broken = False
        
        # Random chance for a powerup in this brick
        self.has_powerup = random.random() < powerup_chance
        self.powerup_type = random.randint(0, 7) if self.has_powerup else None
        
    def draw(self):
        if not self.broken:
            # Color based on strength
            if self.strength == 1:
                color = COLORS[0]  # Red
            elif self.strength == 2:
                color = COLORS[2]  # Yellow
            elif self.strength == 3:
                color = COLORS[3]  # Green
            else:
                color = COLORS[5]  # Blue for 4+ strength
            
            # Draw the brick
            pygame.draw.rect(screen, color, self.rect)
            
            # Add shine effect
            pygame.draw.line(screen, (255, 255, 255, 128), 
                            (self.x, self.y), 
                            (self.x + self.width, self.y), 1)
            
            # If strength > 1, add number indicator
            if self.strength > 1:
                text = font_sm.render(str(self.strength), True, WHITE)
                text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
                screen.blit(text, text_rect)
    
    def hit(self, ball=None):
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
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.size = POWERUP_SIZE
        self.speed = POWERUP_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.collected = False
        self.angle = 0  # For rotation effect
        
    def draw(self):
        if not self.collected:
            # Determine color based on powerup type
            colors = [GREEN, RED, CYAN, BLUE, ORANGE, YELLOW, PURPLE, YELLOW]
            color = colors[self.type]
            
            # Draw a rotating square with powerup symbol
            self.angle = (self.angle + 2) % 360
            center_x, center_y = self.x + self.size // 2, self.y + self.size // 2
            
            # Create a surface for the powerup
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, self.size, self.size))
            
            # Add a symbol based on powerup type
            symbols = ["+", "-", "M", "S", "F", "L", "♥", "T"]
            symbol_text = font_md.render(symbols[self.type], True, WHITE)
            symbol_rect = symbol_text.get_rect(center=(self.size//2, self.size//2))
            surf.blit(symbol_text, symbol_rect)
            
            # Rotate the surface
            rotated_surf = pygame.transform.rotate(surf, self.angle)
            rotated_rect = rotated_surf.get_rect(center=(center_x, center_y))
            
            # Draw to screen
            screen.blit(rotated_surf, rotated_rect.topleft)
    
    def update(self):
        if not self.collected:
            self.y += self.speed
            self.rect.y = self.y
            
            # Check if powerup is off screen
            if self.y > SCREEN_HEIGHT:
                return True  # Remove this powerup
        return False  # Keep this powerup

def create_bricks(level):
    bricks = []
    
    # Different brick layouts for different levels
    if level == 1:
        # Calculate total width of all bricks plus gaps
        total_width = BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP
        # Calculate starting x position to center bricks horizontally
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Simple rows with proper alignment and centering
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                # Calculate positions with proper centering
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
                # First row has strength 1, then 2, then 3...
                strength = min(row + 1, 4) 
                bricks.append(Brick(x, y, strength))
    
    elif level == 2:
        # Diamond pattern
        center_col = BRICK_COLS // 2
        center_row = BRICK_ROWS // 2
        for row in range(BRICK_ROWS+2):
            for col in range(BRICK_COLS+2):
                # Calculate distance from center
                dist = abs(col - center_col) + abs(row - center_row)
                if dist <= BRICK_ROWS:
                    x = col * (BRICK_WIDTH + BRICK_GAP) + 25
                    y = row * (BRICK_HEIGHT + BRICK_GAP) + 40
                    # Outer bricks have higher strength
                    strength = max(1, 4 - dist // 2)
                    bricks.append(Brick(x, y, strength))
    
    elif level == 3:
        # Checkerboard pattern
        for row in range(BRICK_ROWS+2):
            for col in range(BRICK_COLS+2):
                if (row + col) % 2 == 0:
                    x = col * (BRICK_WIDTH + BRICK_GAP) + 25
                    y = row * (BRICK_HEIGHT + BRICK_GAP) + 40
                    strength = random.randint(1, 3)
                    bricks.append(Brick(x, y, strength))
    
    else:
        # Random level - higher number means more difficult
        for row in range(BRICK_ROWS+level//2):
            for col in range(BRICK_COLS):
                if random.random() < 0.8:  # 80% chance of a brick
                    x = col * (BRICK_WIDTH + BRICK_GAP) + 50
                    y = row * (BRICK_HEIGHT + BRICK_GAP) + 40
                    # Higher chance of strong bricks in later levels
                    strength = random.choices([1, 2, 3, 4], 
                                            weights=[5-level//2, level, level//2, level//3],
                                            k=1)[0]
                    strength = max(1, min(strength, 4))  # Clamp between 1-4
                    bricks.append(Brick(x, y, strength))
    
    return bricks

def apply_powerup(powerup, paddle, balls, lives):
    powerup_sound.play()
    duration = 15 * FPS  # 15 seconds duration for timed powerups
    
    if powerup.type == POWERUP_EXPAND:
        # Expand paddle
        paddle.width = min(PADDLE_WIDTH * 2, SCREEN_WIDTH // 2)
        paddle.rect.width = paddle.width
        # Re-center the paddle
        paddle.x = max(0, min(paddle.x, SCREEN_WIDTH - paddle.width))
        
    elif powerup.type == POWERUP_SHRINK:
        # Shrink paddle (negative powerup)
        paddle.width = max(PADDLE_WIDTH // 2, 30)
        paddle.rect.width = paddle.width
        
    elif powerup.type == POWERUP_MULTI:
        # Add 2 extra balls
        for _ in range(2):
            # Create a new ball with random direction
            new_ball = Ball(
                x=balls[0].x,
                y=balls[0].y,
                speed_x=balls[0].speed_x * random.uniform(0.8, 1.2),
                speed_y=balls[0].speed_y * random.uniform(0.8, 1.2)
            )
            new_ball.active = True
            balls.append(new_ball)
            
    elif powerup.type == POWERUP_SLOW:
        # Slow all balls down
        for ball in balls:
            speed = math.sqrt(ball.speed_x**2 + ball.speed_y**2)
            direction_x = ball.speed_x / speed
            direction_y = ball.speed_y / speed
            new_speed = max(2, speed * 0.7)  # Slow down but maintain min speed
            ball.speed_x = direction_x * new_speed
            ball.speed_y = direction_y * new_speed
            
    elif powerup.type == POWERUP_FAST:
        # Speed balls up (negative powerup)
        for ball in balls:
            speed = math.sqrt(ball.speed_x**2 + ball.speed_y**2)
            direction_x = ball.speed_x / speed
            direction_y = ball.speed_y / speed
            new_speed = min(10, speed * 1.5)  # Speed up but cap at max
            ball.speed_x = direction_x * new_speed
            ball.speed_y = direction_y * new_speed
            
    elif powerup.type == POWERUP_LASER:
        # Activate lasers
        paddle.laser_active = True
        paddle.laser_time = 10  # 10 seconds of laser
        
    elif powerup.type == POWERUP_LIFE:
        # Extra life
        return lives + 1
        
    elif powerup.type == POWERUP_THRU:
        # Ball goes through bricks
        for ball in balls:
            ball.thru = True
    
    return lives

def draw_text(text, size, x, y, color=WHITE):
    """Helper function to draw text on the screen"""
    if size == "small":
        font = font_sm
    elif size == "medium":
        font = font_md
    else:
        font = font_lg
        
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def show_game_over(score, high_score):
    """Display game over screen"""
    screen.fill(BLACK)
    
    # Game Over text
    draw_text("GAME OVER", "large", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, RED)
    
    # Score
    draw_text(f"Score: {score}", "medium", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    # High Score
    if score > high_score:
        draw_text("NEW HIGH SCORE!", "medium", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, YELLOW)
        high_score = score
    else:
        draw_text(f"High Score: {high_score}", "medium", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
    
    # Instructions
    draw_text("Press SPACE to play again or ESC to quit", "small", 
              SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
    
    pygame.display.flip()
    
    # Wait for player input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    
    return high_score

def show_level_start(level):
    """Display level start screen"""
    screen.fill(BLACK)
    
    # Level text
    draw_text(f"LEVEL {level}", "large", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, GREEN)
    
    # Instructions
    if level == 1:
        draw_text("Break all the bricks to advance!", "medium", 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text("Don't let the ball fall!", "medium", 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        draw_text("Collect powerups for special abilities", "medium", 
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
    
    draw_text("Press SPACE to start", "small", SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
    
    pygame.display.flip()
    
    # Wait for player input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def create_particle_effect(x, y, color, count=10):
    """Create particles for visual effects"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        size = random.randint(2, 6)
        lifetime = random.uniform(0.5, 2.0) * FPS
        particles.append({
            'x': x,
            'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': size,
            'color': color,
            'lifetime': lifetime
        })
    return particles
def update_particles(particles):
    """Update and remove expired particles"""
    for particle in particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['lifetime'] -= 1
        
        # Remove expired particles
        if particle['lifetime'] <= 0:  # Changed from a0 to 0
            particles.remove(particle)

def draw_particles(particles):
    """Draw all particles"""
    for particle in particles:
        # Fade out as lifetime decreases
        alpha = int(255 * (particle['lifetime'] / (FPS * 2)))
        color = list(particle['color'])
        if len(color) < 4:
            color.append(alpha)
        else:
            color[3] = alpha
            
        # Draw the particle
        pygame.draw.circle(
            screen, 
            color, 
            (int(particle['x']), int(particle['y'])), 
            particle['size']
        )

def main():
    # Initialize game variables
    lives = 3
    score = 0
    level = 1
    high_score = 0
    
    # Show opening level screen
    show_level_start(level)
    
    # Create game objects
    paddle = Paddle()
    balls = [Ball()]
    bricks = create_bricks(level)
    powerups = []
    lasers = []
    particles = []
    
    # Game state variables
    game_over = False
    level_complete = False
    paused = False
    
    # Main game loop
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Launch all inactive balls
                    for ball in balls:
                        ball.active = True
                        
                elif event.key == pygame.K_p:
                    # Toggle pause
                    paused = not paused
                    
                elif event.key == pygame.K_m:
                    # Toggle between mouse and keyboard control
                    paddle.use_mouse = not paddle.use_mouse
                    
                elif event.key == pygame.K_r:
                    # Reset balls if all are lost
                    if len(balls) == 0:
                        balls = [Ball()]
                
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
            # Switch to keyboard control if arrow keys are pressed
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                paddle.use_mouse = False
                
            # Switch to mouse control if mouse is moved
            if event.type == pygame.MOUSEMOTION:
                paddle.use_mouse = True
        
        # Skip updates if paused
        if paused:
            # Just draw "PAUSED" text and continue
            screen.fill(BLACK)
            draw_text("PAUSED", "large", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text("Press P to resume", "small", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
            pygame.display.flip()
            clock.tick(FPS)
            continue
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Update paddle
        paddle.update()
        
        # Check if we should shoot lasers
        if paddle.laser_active:
            new_lasers = paddle.shoot_laser()
            if new_lasers:
                lasers.extend(new_lasers)
        
        # Update lasers
        for laser in lasers[:]:
            laser.update()
            
            # Check if laser is off screen
            if laser.y < 0:
                lasers.remove(laser)
                continue
                
            # Check laser-brick collisions
            for brick in bricks[:]:
                if laser.rect.colliderect(brick.rect):
                    # Brick hit by laser
                    brick_broken = brick.hit()
                    
                    if brick_broken:
                        # Create particles
                        particles.extend(create_particle_effect(
                            brick.x + brick.width // 2,
                            brick.y + brick.height // 2,
                            COLORS[random.randint(0, len(COLORS)-1)]
                        ))
                        
                        # Create powerup if brick has one
                        if brick.has_powerup:
                            powerups.append(Powerup(
                                brick.x + brick.width // 2 - POWERUP_SIZE // 2,
                                brick.y + brick.height,
                                brick.powerup_type
                            ))
                            
                        # Add score
                        score += 10 * brick.max_strength
                        
                        # Remove the brick
                        bricks.remove(brick)
                    
                    # Remove the laser
                    if laser in lasers:
                        lasers.remove(laser)
                    
                    # Play sound
                    brick_sound.play()
                    break
        
        # Update balls
        # Make a copy of the list because we might add/remove items
        for ball in balls[:]:
            # Update ball and check if lost
            ball_lost = ball.update(paddle, bricks, powerups, lasers)
            
            if ball_lost:
                if len(balls) <= 1:
                    # Last ball lost - lose a life
                    lives -= 1
                    life_lost_sound.play()
                    
                    if lives <= 0:
                        # Game over
                        high_score = max(high_score, score)
                        high_score = show_game_over(score, high_score)
                        
                        # Reset for new game
                        lives = 3
                        score = 0
                        level = 1
                        paddle = Paddle()
                        balls = [Ball()]
                        bricks = create_bricks(level)
                        powerups = []
                        lasers = []
                        particles = []
                        show_level_start(level)
                    else:
                        # Just reset ball
                        balls = [Ball()]
                else:
                    # Remove just this ball
                    balls.remove(ball)
            
            # Check for ball-brick collisions
            for brick in bricks[:]:
                if ball.rect.colliderect(brick.rect) and not brick.broken:
                    # Calculate which side of the brick was hit
                    dx_entry = (ball.rect.right - brick.rect.left) if ball.speed_x > 0 else (brick.rect.right - ball.rect.left)
                    dy_entry = (ball.rect.bottom - brick.rect.top) if ball.speed_y > 0 else (brick.rect.bottom - ball.rect.top)
                    
                    # Check if the ball has thru ability
                    if not ball.thru:
                        if dx_entry < dy_entry:
                            # Horizontal collision
                            ball.speed_x = -ball.speed_x
                        else:
                            # Vertical collision
                            ball.speed_y = -ball.speed_y
                    
                    # Damage/Break the brick
                    brick_broken = brick.hit(ball)
                    
                    if brick_broken:
                        # Create particles
                        particles.extend(create_particle_effect(
                            brick.x + brick.width // 2,
                            brick.y + brick.height // 2,
                            COLORS[random.randint(0, len(COLORS)-1)]
                        ))
                        
                        # Create powerup if brick has one
                        if brick.has_powerup:
                            powerups.append(Powerup(
                                brick.x + brick.width // 2 - POWERUP_SIZE // 2,
                                brick.y + brick.height,
                                brick.powerup_type
                            ))
                            
                        # Add score
                        score += 10 * brick.max_strength
                        
                        # Remove the brick
                        bricks.remove(brick)
                    
                    # Play sound
                    brick_sound.play()
                    
                    # If ball has thru ability, continue to next brick
                    # Otherwise, break after the first collision
                    if not ball.thru:
                        break
        
        # Update powerups
        for powerup in powerups[:]:
            # Update and check if off screen
            if powerup.update():
                powerups.remove(powerup)
                continue
                
            # Check for paddle collision
            if powerup.rect.colliderect(paddle.rect) and not powerup.collected:
                powerup.collected = True
                lives = apply_powerup(powerup, paddle, balls, lives)
                powerups.remove(powerup)
        
        # Update particles
        update_particles(particles)
        
        # Check if level is complete
        if len(bricks) == 0:
            level_complete = True
            level_complete_sound.play()
            
            # Next level
            level += 1
            
            # Reset for next level, but keep score and lives
            paddle = Paddle()
            balls = [Ball()]
            bricks = create_bricks(level)
            powerups = []
            lasers = []
            
            # Add bonus points for completing level
            score += 100 * level
            
            # Show next level screen
            show_level_start(level)
            level_complete = False
        
        # Draw everything
        # Draw bricks
        for brick in bricks:
            brick.draw()
            
        # Draw powerups
        for powerup in powerups:
            powerup.draw()
            
        # Draw lasers
        for laser in lasers:
            laser.draw()
            
        # Draw balls
        for ball in balls:
            ball.draw()
            
        # Draw paddle
        paddle.draw()
        
        # Draw particles
        draw_particles(particles)
        
        # Draw UI
        # Lives
        for i in range(lives):
            pygame.draw.circle(screen, RED, (30 + i * 30, 30), 10)
            
        # Score
        score_text = font_md.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
        
        # Level
        level_text = font_md.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 20))
        
        # Controls info
        if any(not ball.active for ball in balls):
            draw_text("Press SPACE to launch", "small", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
            
        # Control method
        control_text = "Controls: Mouse" if paddle.use_mouse else "Controls: Arrow Keys"
        draw_text(control_text, "small", 120, SCREEN_HEIGHT - 30)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    main()
