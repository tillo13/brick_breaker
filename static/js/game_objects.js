/**
 * Game Objects for Brick Breaker
 * This file defines the objects used in the game.
 */

// ======================
// Paddle Class
// ======================

// ======================
// Paddle Class
// ======================
class Paddle {
    constructor(canvasWidth, canvasHeight) {
        // Size
        this.width = 100;
        this.height = 20;
        
        // Position
        this.x = canvasWidth / 2 - this.width / 2;
        this.y = canvasHeight - 50;
        
        // Movement
        this.speed = 600; // pixels per second
        this.useMouseControl = true;
        
        // Canvas bounds
        this.canvasWidth = canvasWidth;
        
        // Laser powerup
        this.laserActive = false;
        this.laserTime = 0;
        this.laserCooldown = 0.3; // seconds between shots
        this.lastLaserTime = 0;
    }
    
    // Update paddle position based on input
    update(deltaTime, input) {
        if (!input) return;
        
        // Toggle control method if requested (M key)
        if (input.toggleControlPressed) {
            this.useMouseControl = !this.useMouseControl;
            console.log("Controls switched to:", this.useMouseControl ? "Mouse" : "Keyboard");
        }
        
        // Always respect forced keyboard mode (K key)
        if (input.forceKeyboardMode) {
            this.useMouseControl = false;
        }
        
        // Move paddle based on active control method
        if (this.useMouseControl && input.mouseX !== null) {
            // Mouse control
            this.x = input.mouseX - this.width / 2;
        } else {
            // Keyboard control
            if (input.leftPressed) {
                this.x -= this.speed * deltaTime;
            }
            if (input.rightPressed) {
                this.x += this.speed * deltaTime;
            }
        }
        
        // Keep paddle within canvas bounds
        this.x = Math.max(0, Math.min(this.canvasWidth - this.width, this.x));
        
        // Update laser timer
        if (this.laserActive) {
            this.laserTime -= deltaTime;
            if (this.laserTime <= 0) {
                this.laserActive = false;
            }
        }
    }
    
    // Activate laser powerup
    activateLaser(duration) {
        this.laserActive = true;
        this.laserTime = duration;
        this.lastLaserTime = 0; // reset cooldown
    }
    
    // Check if enough time has passed to fire laser
    canFireLaser() {
        const now = performance.now() / 1000;
        return now - this.lastLaserTime >= this.laserCooldown;
    }
    
    // Create laser objects
    fireLaser() {
        if (!this.laserActive || !this.canFireLaser()) {
            return [];
        }
        
        // Update last fire time
        this.lastLaserTime = performance.now() / 1000;
        
        // Create two lasers (one from each side of paddle)
        return [
            new Laser(this.x + 15, this.y - 10),
            new Laser(this.x + this.width - 15, this.y - 10)
        ];
    }
}

// ======================
// Ball Class
// ======================
class Ball {
    constructor(canvasWidth, canvasHeight, x, y) {
        // Size (for both display and collision)
        this.width = 15;
        this.height = 15;
        this.size = 15;
        
        // Position
        this.x = x !== undefined ? x : canvasWidth / 2 - this.size / 2;
        this.y = y !== undefined ? y : canvasHeight / 2;
        
        // Canvas bounds
        this.canvasWidth = canvasWidth;
        this.canvasHeight = canvasHeight;
        
        // Movement
        this.speedX = 0;
        this.speedY = 0;
        this.setInitialDirection();
        
        // State
        this.active = false;   // Is ball launched from paddle?
        this.thru = false;     // Can ball go through bricks?
    }
    
    // Set random initial direction
    setInitialDirection() {
        const angle = Math.random() * Math.PI / 4 + Math.PI / 4; // 45-90 degrees
        const speed = 450; // pixels per second
        
        this.speedX = speed * Math.cos(angle);
        this.speedY = -speed * Math.sin(angle); // Negative = up
    }
    
    // Update ball position
    update(deltaTime) {
        if (!this.active) return;
        
        // Move the ball
        this.x += this.speedX * deltaTime;
        this.y += this.speedY * deltaTime;
    }
    
    // Handle collision with walls
    handleWallCollision(canvasWidth, canvasHeight) {
        // Left and right walls
        if (this.x <= 0 || this.x + this.size >= canvasWidth) {
            this.speedX = -this.speedX;
            
            // Adjust position to prevent sticking
            if (this.x <= 0) {
                this.x = 0;
            } else {
                this.x = canvasWidth - this.size;
            }
        }
        
        // Top wall
        if (this.y <= 0) {
            this.speedY = -this.speedY;
            this.y = 0;
        }
    }
    
    // Position ball on paddle when not launched
    stickToPaddle(paddle) {
        this.x = paddle.x + paddle.width / 2 - this.size / 2;
        this.y = paddle.y - this.size;
    }
    
    // Handle collision with paddle
    handlePaddleCollision(paddle) {
        // Calculate where ball hit the paddle (0 to 1)
        const hitPosition = (this.x + this.size / 2 - paddle.x) / paddle.width;
        
        // Angle based on hit position (-60 to 60 degrees)
        const angle = (hitPosition - 0.5) * Math.PI / 3;
        
        // Get current speed
        const speed = Math.sqrt(this.speedX * this.speedX + this.speedY * this.speedY);
        
        // Set new direction with slight speed increase
        const newSpeed = Math.min(speed * 1.05, 800);
        this.speedX = newSpeed * Math.sin(angle);
        this.speedY = -Math.abs(newSpeed * Math.cos(angle)); // Force upward
        
        // Prevent ball from getting stuck in paddle
        this.y = paddle.y - this.size;
    }
    
    // Handle collision with brick
    handleBrickCollision(brick) {
        // Calculate collision depths
        const fromLeft = (this.x + this.size) - brick.x;
        const fromRight = (brick.x + brick.width) - this.x;
        const fromTop = (this.y + this.size) - brick.y;
        const fromBottom = (brick.y + brick.height) - this.y;
        
        // Find shallowest collision (smallest depth)
        const depths = [fromLeft, fromRight, fromTop, fromBottom];
        const minDepth = Math.min(...depths);
        
        // Bounce based on which side was hit
        if (minDepth === fromTop || minDepth === fromBottom) {
            // Hit top or bottom - reverse Y velocity
            this.speedY = -this.speedY;
            
            // Adjust position to prevent multiple hits
            if (minDepth === fromTop) {
                this.y = brick.y - this.size;
            } else {
                this.y = brick.y + brick.height;
            }
        } else {
            // Hit left or right - reverse X velocity
            this.speedX = -this.speedX;
            
            // Adjust position to prevent multiple hits
            if (minDepth === fromLeft) {
                this.x = brick.x - this.size;
            } else {
                this.x = brick.x + brick.width;
            }
        }
    }
}

// ======================
// Brick Class
// ======================
class Brick {
    constructor(x, y, strength = 1, powerupChance = 0.3) {
        // Size
        this.width = 75;
        this.height = 20;
        
        // Position
        this.x = x;
        this.y = y;
        
        // Strength (hits needed to break)
        this.strength = strength;
        this.maxStrength = strength;
        
        // Powerup properties will be set explicitly for editor bricks
        this.hasPowerup = false;
        this.powerupType = null;
        this.editorPlaced = false;
        
        // Only randomly assign powerups if not editor placed and not explicitly set
        if (!this.editorPlaced && Math.random() < powerupChance) {
            this.hasPowerup = true;
            this.powerupType = Math.floor(Math.random() * 8);
        }
    }
    
    // Handle being hit by ball or laser
    hit(ball = null) {
        // If hit by thru ball, break immediately
        if (ball && ball.thru) {
            this.strength = 0;
        } else {
            this.strength--;
        }
        
        // Return true if brick is broken
        return this.strength <= 0;
    }
    
    // Get color based on strength
    getColor() {
        const colors = [
            '#ff3232', // Red (strength 1)
            '#ffcc00', // Yellow (strength 2)
            '#32ff32', // Green (strength 3)
            '#3232ff'  // Blue (strength 4+)
        ];
        
        return colors[Math.min(this.strength, 4) - 1];
    }
}

// ======================
// Powerup Class
// ======================
class Powerup {
    constructor(x, y, type) {
        // Size
        this.width = 30;
        this.height = 30;
        this.size = 30;
        
        // Position
        this.x = x;
        this.y = y;
        
        // Properties
        this.type = type;       // Type of powerup
        this.speed = 150;       // Falling speed (pixels per second)
        this.collected = false; // Has it been collected?
        
        // Visual effects
        this.angle = 0;  // For rotation
    }
    
    // Update powerup position
    update(deltaTime) {
        if (this.collected) return;
        
        // Move downward
        this.y += this.speed * deltaTime;
        
        // Rotate for visual effect
        this.angle = (this.angle + 180 * deltaTime) % 360;
    }
    
    // Get color based on powerup type
    getColor() {
        const colors = [
            '#32ff32', // Expand (green)
            '#ff3232', // Shrink (red)
            '#00ccff', // Multi (cyan)
            '#3232ff', // Slow (blue)
            '#ff9900', // Fast (orange)
            '#ffcc00', // Laser (yellow)
            '#cc00ff', // Life (purple)
            '#ffcc00'  // Thru (yellow)
        ];
        
        return colors[this.type];
    }
    
    // Get symbol based on powerup type
    getSymbol() {
        const symbols = ['+', '-', 'M', 'S', 'F', 'L', '♥', 'T'];
        return symbols[this.type];
    }
}

// ======================
// Laser Class
// ======================
class Laser {
    constructor(x, y) {
        // Size
        this.width = 3;
        this.height = 15;
        
        // Position
        this.x = x;
        this.y = y;
        
        // Speed
        this.speed = 500; // pixels per second
    }
    
    // Update laser position
    update(deltaTime) {
        this.y -= this.speed * deltaTime;
    }
}