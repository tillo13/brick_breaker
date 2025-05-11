/**
 * Game State for Brick Breaker
 * This file manages the game state and logic.
 */

class GameState {
    constructor() {
        // Canvas dimensions
        this.width = 800;
        this.height = 600;
        
        // Game state
        this.lives = 3;
        this.score = 0;
        this.level = 1;
        this.highScore = this.loadHighScore();
        this.gameOver = false;
        this.levelComplete = false;
        this.paused = false;
        this.forceKeyboardMode = false;
        
        // Game objects
        this.paddle = null;
        this.balls = [];
        this.bricks = [];
        this.powerups = [];
        this.lasers = [];
        this.particles = [];
        
        // Special flags
        this.isEditorLevel = false;
        this.isTestMode = false;
    }
    
    // Initialize game with level data
    init(levelData) {
        // Create game objects
        this.paddle = new Paddle(this.width, this.height);
        this.balls = [new Ball(this.width, this.height)];
        this.powerups = [];
        this.lasers = [];
        this.particles = [];
        
        // Check if this is an editor-created level
        this.isEditorLevel = levelData && levelData.editor_version === true;
        
        // Create bricks from level data
        this.bricks = [];
        if (levelData && levelData.bricks && Array.isArray(levelData.bricks)) {
            levelData.bricks.forEach(brickData => {
                // Create brick with base properties
                const brick = new Brick(
                    brickData.x,
                    brickData.y,
                    brickData.strength || 1,
                    0.0 // No random powerups for loaded levels
                );
                
                // Set explicit properties from level data
                brick.editorPlaced = brickData.editor_placed || this.isEditorLevel;
                brick.hasPowerup = brickData.has_powerup || false;
                if (brick.hasPowerup) {
                    brick.powerupType = brickData.powerup_type || 0;
                }
                
                this.bricks.push(brick);
            });
        }
        
        // Create default bricks if none exist
        if (this.bricks.length === 0) {
            this.createDefaultBricks();
        }
        
        // Reset game state
        this.gameOver = false;
        this.levelComplete = false;
        this.paused = false;
    }
    
    // Update game state each frame
    update(deltaTime, input) {
        // Update keyboard mode flag if set in input
        if (input && input.keyboardModePressed) {
            this.forceKeyboardMode = input.forceKeyboardMode;
        }
        
        // Update balls
        this.updateBalls(deltaTime, input);
        
        // Update lasers
        this.updateLasers(deltaTime);
        
        // Update powerups
        this.updatePowerups(deltaTime);
        
        // Update particles
        this.updateParticles(deltaTime);
        
        // Check if level is complete
        if (this.bricks.length === 0 && !this.levelComplete) {
            this.levelComplete = true;
            this.playSound('levelup');
        }
    }
    
    // Update all balls
    updateBalls(deltaTime, input) {
        for (let i = this.balls.length - 1; i >= 0; i--) {
            const ball = this.balls[i];
            
            // Launch inactive ball if space is pressed
            if (!ball.active && input && input.launchPressed) {
                ball.active = true;
                continue;
            }
            
            // Skip inactive balls
            if (!ball.active) {
                ball.stickToPaddle(this.paddle);
                continue;
            }
            
            // Move ball
            ball.update(deltaTime);
            
            // Check wall collisions
            ball.handleWallCollision(this.width, this.height);
            
            // Check paddle collision
            if (this.checkCollision(ball, this.paddle) && ball.speedY > 0) {
                ball.handlePaddleCollision(this.paddle);
                this.playSound('bounce');
            }
            
            // Check brick collisions
            this.checkBallBrickCollisions(ball);
            
            // Check if ball is lost
            if (ball.y > this.height) {
                this.balls.splice(i, 1);
                
                // If no balls left, lose a life
                if (this.balls.length === 0) {
                    this.lives--;
                    
                    if (this.lives <= 0) {
                        this.gameOver = true;
                        this.updateHighScore();
                        this.playSound('gameover');
                    } else {
                        // Add a new ball
                        this.balls.push(new Ball(this.width, this.height));
                    }
                }
            }
        }
    }
    
    // Check all brick collisions for a ball
    checkBallBrickCollisions(ball) {
        for (let i = this.bricks.length - 1; i >= 0; i--) {
            const brick = this.bricks[i];
            
            if (this.checkCollision(ball, brick)) {
                // Bounce the ball unless it has thru powerup
                if (!ball.thru) {
                    ball.handleBrickCollision(brick);
                }
                
                // Damage the brick
                const brickBroken = brick.hit(ball);
                this.playSound('brick');
                
                if (brickBroken) {
                    // Create particle effects
                    this.createParticleEffect(
                        brick.x + brick.width / 2,
                        brick.y + brick.height / 2,
                        brick.getColor()
                    );
                    
                    // Create powerup if brick has one - EDITOR MODE RESPECT
                    if (brick.hasPowerup) {
                        this.powerups.push(new Powerup(
                            brick.x + brick.width / 2 - 15,
                            brick.y + brick.height,
                            brick.powerupType
                        ));
                    }
                    
                    // Add score and remove brick
                    this.score += 10 * brick.maxStrength;
                    this.bricks.splice(i, 1);
                }
                
                // Stop checking more bricks if ball can't go through them
                if (!ball.thru) break;
            }
        }
    }
    
    // Update all lasers
    updateLasers(deltaTime) {
        // Fire new lasers if paddle has laser power
        if (this.paddle.laserActive && this.paddle.canFireLaser()) {
            const newLasers = this.paddle.fireLaser();
            if (newLasers.length > 0) {
                this.lasers.push(...newLasers);
                this.playSound('laser');
            }
        }
        
        // Update existing lasers
        for (let i = this.lasers.length - 1; i >= 0; i--) {
            const laser = this.lasers[i];
            laser.update(deltaTime);
            
            // Remove lasers that are off-screen
            if (laser.y < 0) {
                this.lasers.splice(i, 1);
                continue;
            }
            
            // Check for brick collisions
            let hitBrick = false;
            for (let j = this.bricks.length - 1; j >= 0; j--) {
                const brick = this.bricks[j];
                
                if (this.checkCollision(laser, brick)) {
                    // Damage the brick
                    const brickBroken = brick.hit();
                    this.playSound('brick');
                    
                    if (brickBroken) {
                        // Create visual effects
                        this.createParticleEffect(
                            brick.x + brick.width / 2,
                            brick.y + brick.height / 2,
                            brick.getColor()
                        );
                        
                        // Create powerup if brick has one - EDITOR MODE RESPECT
                        if (brick.hasPowerup) {
                            this.powerups.push(new Powerup(
                                brick.x + brick.width / 2 - 15,
                                brick.y + brick.height,
                                brick.powerupType
                            ));
                        }
                        
                        // Add score and remove brick
                        this.score += 10 * brick.maxStrength;
                        this.bricks.splice(j, 1);
                    }
                    
                    // Remove the laser after hitting brick
                    this.lasers.splice(i, 1);
                    hitBrick = true;
                    break;
                }
            }
            
            if (hitBrick) continue;
        }
    }
    
    // Update all powerups
    updatePowerups(deltaTime) {
        for (let i = this.powerups.length - 1; i >= 0; i--) {
            const powerup = this.powerups[i];
            powerup.update(deltaTime);
            
            // Remove powerups that fall off screen
            if (powerup.y > this.height) {
                this.powerups.splice(i, 1);
                continue;
            }
            
            // Check paddle collision
            if (this.checkCollision(powerup, this.paddle) && !powerup.collected) {
                powerup.collected = true;
                this.applyPowerup(powerup);
                this.playSound('powerup');
                this.powerups.splice(i, 1);
            }
        }
    }
    
    // Apply powerup effect
    applyPowerup(powerup) {
        switch (powerup.type) {
            case 0: // Expand paddle
                this.paddle.width = Math.min(this.paddle.width * 1.5, this.width / 2);
                break;
                
            case 1: // Shrink paddle (negative)
                this.paddle.width = Math.max(this.paddle.width / 1.5, 40);
                break;
                
            case 2: // Multi-ball
                // Add 2 extra balls
                for (let i = 0; i < 2; i++) {
                    if (this.balls.length > 0) {
                        const sourceBall = this.balls[0];
                        const newBall = new Ball(this.width, this.height, sourceBall.x, sourceBall.y);
                        newBall.active = true;
                        
                        // Set random direction
                        const angle = Math.random() * Math.PI * 2;
                        const speed = Math.sqrt(sourceBall.speedX**2 + sourceBall.speedY**2);
                        newBall.speedX = Math.cos(angle) * speed;
                        newBall.speedY = Math.sin(angle) * speed;
                        
                        this.balls.push(newBall);
                    }
                }
                break;
                
            case 3: // Slow balls
                this.balls.forEach(ball => {
                    const speed = Math.sqrt(ball.speedX**2 + ball.speedY**2);
                    const direction = { 
                        x: ball.speedX / speed, 
                        y: ball.speedY / speed 
                    };
                    const newSpeed = Math.max(300, speed * 0.7);
                    
                    ball.speedX = direction.x * newSpeed;
                    ball.speedY = direction.y * newSpeed;
                });
                break;
                
            case 4: // Fast balls (negative)
                this.balls.forEach(ball => {
                    const speed = Math.sqrt(ball.speedX**2 + ball.speedY**2);
                    const direction = { 
                        x: ball.speedX / speed, 
                        y: ball.speedY / speed 
                    };
                    const newSpeed = Math.min(900, speed * 1.5);
                    
                    ball.speedX = direction.x * newSpeed;
                    ball.speedY = direction.y * newSpeed;
                });
                break;
                
            case 5: // Laser
                this.paddle.activateLaser(10); // 10 seconds
                break;
                
            case 6: // Extra life
                this.lives++;
                break;
                
            case 7: // Thru ball
                this.balls.forEach(ball => {
                    ball.thru = true;
                });
                break;
        }
    }
    
    // Update all particles
    updateParticles(deltaTime) {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            particle.update(deltaTime);
            
            // Remove expired particles
            if (particle.lifetime <= 0) {
                this.particles.splice(i, 1);
            }
        }
    }
    
    // Create particles for visual effects
    createParticleEffect(x, y, color, count = 12) {
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 80 + 40;
            const size = Math.random() * 4 + 2;
            const lifetime = Math.random() * 0.6 + 0.3;
            
            this.particles.push({
                x: x,
                y: y,
                speedX: Math.cos(angle) * speed,
                speedY: Math.sin(angle) * speed,
                size: size,
                color: color,
                lifetime: lifetime,
                initialLifetime: lifetime,
                update: function(dt) {
                    this.x += this.speedX * dt;
                    this.y += this.speedY * dt;
                    this.lifetime -= dt;
                }
            });
        }
    }
    
    // Create default brick layout
    createDefaultBricks() {
        const brickWidth = 75;
        const brickHeight = 20;
        const gap = 2;
        const rows = 5;
        const cols = 10;
        
        // Calculate total width and starting position to center
        const totalWidth = cols * brickWidth + (cols - 1) * gap;
        const startX = (this.width - totalWidth) / 2;
        
        // Create rows of bricks
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = startX + col * (brickWidth + gap);
                const y = 50 + row * (brickHeight + gap);
                
                // Bricks get stronger as rows go down
                const strength = Math.min(row + 1, 3);
                
                // Create brick
                const brick = new Brick(x, y, strength);
                
                // In test mode, we can give each default brick a powerup for testing
                if (this.isTestMode) {
                    brick.hasPowerup = true;
                    brick.powerupType = (row * cols + col) % 8; // Different powerup for each brick
                }
                
                this.bricks.push(brick);
            }
        }
    }
    
    // Simple collision detection between two objects
    checkCollision(objA, objB) {
        return (
            objA.x < objB.x + objB.width &&
            objA.x + objA.width > objB.x &&
            objA.y < objB.y + objB.height &&
            objA.y + objA.height > objB.y
        );
    }
    
    // Reset the game completely
    resetGame() {
        this.lives = 3;
        this.score = 0;
        this.level = 1;
        this.gameOver = false;
        
        // Maintain the editor and test mode flags
        const wasEditorLevel = this.isEditorLevel;
        const wasTestMode = this.isTestMode;
        
        if (wasTestMode) {
            // In test mode, reload the current level
            const urlParams = new URLSearchParams(window.location.search);
            const levelParam = urlParams.get('level');
            if (levelParam) {
                fetch(`/api/levels/level-${levelParam}`)
                    .then(response => response.json())
                    .then(levelData => {
                        this.init(levelData);
                        this.isEditorLevel = wasEditorLevel;
                        this.isTestMode = wasTestMode;
                    })
                    .catch(() => {
                        this.init(null);
                        this.isEditorLevel = false;
                        this.isTestMode = wasTestMode;
                    });
                return;
            }
        }
        
        // Normal reset process
        fetch(`/api/levels/level-${this.level}`)
            .then(response => response.json())
            .then(levelData => {
                this.init(levelData);
                this.isEditorLevel = wasEditorLevel;
                this.isTestMode = wasTestMode;
            })
            .catch(() => {
                this.init(null);
                this.isEditorLevel = false;
                this.isTestMode = wasTestMode;
            });
    }
    
    // Move to the next level
    nextLevel() {
        // If in test mode, don't advance to the next level
        if (this.isTestMode) {
            this.levelComplete = false;
            return;
        }
        
        this.level++;
        this.levelComplete = false;
        
        // Bonus points for completing a level
        this.score += 100 * this.level;
        
        fetch(`/api/levels/level-${this.level}`)
            .then(response => response.json())
            .then(levelData => {
                this.init(levelData);
            })
            .catch(() => {
                this.init(null);
            });
    }
    
    // Load the high score from localStorage
    loadHighScore() {
        const savedScore = localStorage.getItem('brickBreakerHighScore');
        return savedScore ? parseInt(savedScore, 10) : 0;
    }
    
    // Update high score if score is higher
    updateHighScore() {
        // In test mode, don't update high score
        if (this.isTestMode) return;
        
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('brickBreakerHighScore', this.score);
        }
    }
    
    // Play a sound effect
    playSound(soundName) {
        if (window.soundManager) {
            window.soundManager.play(soundName);
        }
    }
}