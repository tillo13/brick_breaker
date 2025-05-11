/**
 * Game Renderer for Brick Breaker
 * This file handles drawing the game on the canvas.
 */

class GameRenderer {
    constructor(ctx) {
        this.ctx = ctx;
        this.canvas = ctx.canvas;
        this.width = ctx.canvas.width;
        this.height = ctx.canvas.height;
        
        // Generate stars for background
        this.generateStars();
    }
    
    // Main render function - draws everything
    render(gameState) {
        // Clear the canvas
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Draw background
        this.drawBackground();
        
        // Draw game objects
        this.drawBricks(gameState.bricks);
        this.drawPowerups(gameState.powerups);
        this.drawLasers(gameState.lasers);
        this.drawParticles(gameState.particles);
        this.drawBalls(gameState.balls);
        this.drawPaddle(gameState.paddle);
        
        // Draw UI elements
        this.drawUI(gameState);
    }
    
    // Generate random stars for the background
    generateStars() {
        this.stars = [];
        for (let i = 0; i < 100; i++) {
            this.stars.push({
                x: Math.random() * this.width,
                y: Math.random() * this.height,
                size: Math.random() * 2 + 0.5,
                brightness: Math.random() * 0.7 + 0.3
            });
        }
    }
    
    // Draw the space background
    drawBackground() {
        // Gradient background
        const gradient = this.ctx.createLinearGradient(0, 0, 0, this.height);
        gradient.addColorStop(0, '#000033');
        gradient.addColorStop(1, '#000022');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw stars
        for (const star of this.stars) {
            this.ctx.fillStyle = `rgba(255, 255, 255, ${star.brightness})`;
            this.ctx.beginPath();
            this.ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    // Draw the paddle
    drawPaddle(paddle) {
        if (!paddle) return;
        
        // Main paddle body
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
        
        // Inner detail
        this.ctx.fillStyle = '#8888FF';
        this.ctx.fillRect(
            paddle.x + 2, 
            paddle.y + 2, 
            paddle.width - 4, 
            paddle.height - 4
        );
        
        // Draw laser cannons if active
        if (paddle.laserActive) {
            this.ctx.fillStyle = '#FF0000';
            this.ctx.fillRect(paddle.x + 10, paddle.y - 5, 5, 5);
            this.ctx.fillRect(paddle.x + paddle.width - 15, paddle.y - 5, 5, 5);
            
            // Glow effect
            this.ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
            this.ctx.beginPath();
            this.ctx.arc(paddle.x + 12.5, paddle.y - 2.5, 8, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.beginPath();
            this.ctx.arc(paddle.x + paddle.width - 12.5, paddle.y - 2.5, 8, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    // Draw all balls
    drawBalls(balls) {
        if (!balls || !balls.length) return;
        
        for (const ball of balls) {
            if (ball.thru) {
                // Thru-ball with glow effect
                for (let i = 3; i > 0; i--) {
                    this.ctx.fillStyle = `rgba(255, 200, 0, ${0.3 - i * 0.05})`;
                    this.ctx.beginPath();
                    this.ctx.arc(
                        ball.x + ball.size / 2, 
                        ball.y + ball.size / 2, 
                        ball.size / 2 + i * 2, 
                        0, 
                        Math.PI * 2
                    );
                    this.ctx.fill();
                }
                
                // Ball itself
                this.ctx.fillStyle = '#FFCC00';
            } else {
                // Regular ball
                this.ctx.fillStyle = '#FFFFFF';
            }
            
            // Draw the ball
            this.ctx.beginPath();
            this.ctx.arc(
                ball.x + ball.size / 2, 
                ball.y + ball.size / 2, 
                ball.size / 2, 
                0, 
                Math.PI * 2
            );
            this.ctx.fill();
            
            // Add a shine effect
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
            this.ctx.beginPath();
            this.ctx.arc(
                ball.x + ball.size / 2 - ball.size / 5, 
                ball.y + ball.size / 2 - ball.size / 5,
                ball.size / 5,
                0, 
                Math.PI * 2
            );
            this.ctx.fill();
        }
    }
    
    // Draw all bricks
    drawBricks(bricks) {
        if (!bricks || !bricks.length) return;
        
        for (const brick of bricks) {
            // Fill with color based on strength
            this.ctx.fillStyle = brick.getColor();
            this.ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
            
            // Top and left highlight
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            this.ctx.fillRect(brick.x, brick.y, brick.width, 2);
            this.ctx.fillRect(brick.x, brick.y, 2, brick.height);
            
            // Bottom and right shadow
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            this.ctx.fillRect(brick.x, brick.y + brick.height - 2, brick.width, 2);
            this.ctx.fillRect(brick.x + brick.width - 2, brick.y, 2, brick.height);
            
            // If strength > 1, add number
            if (brick.strength > 1) {
                this.ctx.fillStyle = '#FFFFFF';
                this.ctx.font = '12px Arial';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(
                    brick.strength.toString(),
                    brick.x + brick.width / 2,
                    brick.y + brick.height / 2
                );
            }
        }
    }
    
    // Draw all powerups
    drawPowerups(powerups) {
        if (!powerups || !powerups.length) return;
        
        for (const powerup of powerups) {
            if (powerup.collected) continue;
            
            // Save context for rotation
            this.ctx.save();
            
            // Translate to center of powerup
            this.ctx.translate(
                powerup.x + powerup.size / 2,
                powerup.y + powerup.size / 2
            );
            
            // Rotate
            this.ctx.rotate(powerup.angle * Math.PI / 180);
            
            // Draw powerup background
            this.ctx.fillStyle = powerup.getColor();
            this.roundRect(
                -powerup.size / 2,
                -powerup.size / 2,
                powerup.size,
                powerup.size,
                5
            );
            
            // Draw powerup symbol
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.font = 'bold 16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(powerup.getSymbol(), 0, 0);
            
            // Restore context
            this.ctx.restore();
        }
    }
    
    // Draw all lasers
    drawLasers(lasers) {
        if (!lasers || !lasers.length) return;
        
        for (const laser of lasers) {
            // Main laser beam
            this.ctx.fillStyle = '#FF0000';
            this.ctx.fillRect(laser.x, laser.y, laser.width, laser.height);
            
            // Glow effect
            this.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
            this.ctx.fillRect(
                laser.x - 2,
                laser.y,
                laser.width + 4,
                laser.height
            );
        }
    }
    
    // Draw all particles
    drawParticles(particles) {
        if (!particles || !particles.length) return;
        
        for (const particle of particles) {
            // Calculate alpha based on remaining lifetime
            const alpha = particle.lifetime / particle.initialLifetime;
            
            // Set color with alpha
            if (typeof particle.color === 'string') {
                // If color is a hex or named color
                this.ctx.fillStyle = this.getColorWithAlpha(particle.color, alpha);
            } else {
                // Fallback to white with alpha
                this.ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
            }
            
            // Draw the particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    // Draw UI elements
// Draw UI elements
drawUI(gameState) {
    // Show current control mode and fullscreen state
    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    this.ctx.font = '14px Arial';
    this.ctx.textAlign = 'left';
    this.ctx.textBaseline = 'top';
    
    // Get the control mode text
    let controlMode;
    if (gameState.forceKeyboardMode) {
        controlMode = "Control: Keyboard-only (K to toggle)";
    } else if (gameState.paddle && gameState.paddle.useMouseControl) {
        controlMode = "Control: Mouse (M to toggle, K for keyboard-only)";
    } else {
        controlMode = "Control: Keyboard (M to toggle, K for keyboard-only)";
    }
    
    // Display the control mode
    this.ctx.fillText(controlMode, 10, 10);
    
    // Display fullscreen info
    const fullscreenText = gameState.isFullscreen ? 
        "Fullscreen: ON (F to exit)" : 
        "Fullscreen: OFF (F to toggle)";
    this.ctx.fillText(fullscreenText, 10, 30);
    
    // If game is paused
    if (gameState.paused) {
        // Semi-transparent overlay
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Pause text
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = 'bold 32px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('PAUSED', this.width / 2, this.height / 2);
        
        // Instructions
        this.ctx.font = '16px Arial';
        this.ctx.fillText(
            'Press P to resume',
            this.width / 2,
            this.height / 2 + 40
        );
    }
    
    // Show launch instructions if ball not launched
    if (gameState.balls.some(ball => !ball.active)) {
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = '16px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(
            'Press SPACE to launch',
            this.width / 2,
            this.height - 30
        );
    }
}
    
    // Helper method to draw rounded rectangles
    roundRect(x, y, width, height, radius) {
        this.ctx.beginPath();
        this.ctx.moveTo(x + radius, y);
        this.ctx.lineTo(x + width - radius, y);
        this.ctx.arc(x + width - radius, y + radius, radius, Math.PI * 1.5, 0, false);
        this.ctx.lineTo(x + width, y + height - radius);
        this.ctx.arc(x + width - radius, y + height - radius, radius, 0, Math.PI * 0.5, false);
        this.ctx.lineTo(x + radius, y + height);
        this.ctx.arc(x + radius, y + height - radius, radius, Math.PI * 0.5, Math.PI, false);
        this.ctx.lineTo(x, y + radius);
        this.ctx.arc(x + radius, y + radius, radius, Math.PI, Math.PI * 1.5, false);
        this.ctx.closePath();
        this.ctx.fill();
    }
    
    // Helper to apply alpha to a color
    getColorWithAlpha(color, alpha) {
        // Handle hex colors
        if (color.startsWith('#')) {
            const r = parseInt(color.slice(1, 3), 16);
            const g = parseInt(color.slice(3, 5), 16);
            const b = parseInt(color.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }
        
        // Handle named colors (create a temp element)
        const tempEl = document.createElement('div');
        tempEl.style.color = color;
        document.body.appendChild(tempEl);
        const computedColor = getComputedStyle(tempEl).color;
        document.body.removeChild(tempEl);
        
        // Extract RGB values and add alpha
        const rgbValues = computedColor.match(/\d+/g).map(Number);
        return `rgba(${rgbValues[0]}, ${rgbValues[1]}, ${rgbValues[2]}, ${alpha})`;
    }
}