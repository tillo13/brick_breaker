/**
 * Game Controls for Brick Breaker
 * This file handles all user input for the game.
 */

class GameControls {
    constructor(canvas) {
        this.canvas = canvas;
        
        // Current input state
        this.keys = {
            left: false,
            right: false,
            space: false,
            p: false,
            m: false,
            k: false,  // Keyboard mode toggle
            f: false   // Fullscreen toggle
        };
        
        // Previous state for one-shot detection
        this.prevKeys = {
            space: false,
            p: false,
            m: false,
            k: false,
            f: false
        };
        
        // Mouse/touch position
        this.mouseX = null;
        
        // Flag to completely ignore mouse input
        this.forceKeyboardMode = false;
        
        // Flag to track fullscreen state
        this.isFullscreen = false;
        
        // Bind event handlers to this object
        this.keyDown = this.keyDown.bind(this);
        this.keyUp = this.keyUp.bind(this);
        this.mouseMove = this.mouseMove.bind(this);
        this.touchMove = this.touchMove.bind(this);
        this.touchStart = this.touchStart.bind(this);
        this.touchEnd = this.touchEnd.bind(this);
        this.toggleFullscreen = this.toggleFullscreen.bind(this);
        
        // Set up event listeners
        window.addEventListener('keydown', this.keyDown);
        window.addEventListener('keyup', this.keyUp);
        canvas.addEventListener('mousemove', this.mouseMove);
        canvas.addEventListener('touchmove', this.touchMove, { passive: false });
        canvas.addEventListener('touchstart', this.touchStart, { passive: false });
        canvas.addEventListener('touchend', this.touchEnd, { passive: false });
        
        // Handle fullscreen change events
        document.addEventListener('fullscreenchange', () => {
            this.isFullscreen = !!document.fullscreenElement;
        });
        document.addEventListener('webkitfullscreenchange', () => {
            this.isFullscreen = !!document.webkitFullscreenElement;
        });
    }
    
    // Handle keydown events
    keyDown(e) {
        switch (e.key) {
            case 'ArrowLeft':
            case 'a':
            case 'A':
                this.keys.left = true;
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                this.keys.right = true;
                break;
            case ' ':
                this.keys.space = true;
                break;
            case 'p':
            case 'P':
                this.keys.p = true;
                break;
            case 'm':
            case 'M':
                this.keys.m = true;
                break;
            case 'k':
            case 'K':
                this.keys.k = true;
                break;
            case 'f':
            case 'F':
                this.keys.f = true;
                break;
            case 's':
            case 'S':
                // Toggle sound immediately
                if (window.soundManager) {
                    const soundOn = window.soundManager.toggle();
                    console.log(`Sound ${soundOn ? 'enabled' : 'disabled'}`);
                }
                break;
        }
    }
    
    // Handle keyup events
    keyUp(e) {
        switch (e.key) {
            case 'ArrowLeft':
            case 'a':
            case 'A':
                this.keys.left = false;
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                this.keys.right = false;
                break;
            case ' ':
                this.keys.space = false;
                break;
            case 'p':
            case 'P':
                this.keys.p = false;
                break;
            case 'm':
            case 'M':
                this.keys.m = false;
                break;
            case 'k':
            case 'K':
                this.keys.k = false;
                break;
            case 'f':
            case 'F':
                this.keys.f = false;
                break;
        }
    }
    
    // Toggle fullscreen mode
    toggleFullscreen() {
        const gameContainer = document.querySelector('.game-container') || this.canvas.parentElement;
        
        if (!this.isFullscreen) {
            // Enter fullscreen
            if (gameContainer.requestFullscreen) {
                gameContainer.requestFullscreen();
            } else if (gameContainer.webkitRequestFullscreen) { // Safari
                gameContainer.webkitRequestFullscreen();
            } else if (gameContainer.msRequestFullscreen) { // IE11
                gameContainer.msRequestFullscreen();
            }
        } else {
            // Exit fullscreen
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) { // Safari
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { // IE11
                document.msExitFullscreen();
            }
        }
    }
    
    // Handle mouse movement
    mouseMove(e) {
        // Skip updating mouse position if in forced keyboard mode
        if (this.forceKeyboardMode) return;
        
        // Get mouse position relative to canvas
        const rect = this.canvas.getBoundingClientRect();
        this.mouseX = e.clientX - rect.left;
    }
    
    // Handle touch movement
    touchMove(e) {
        // Skip updating touch position if in forced keyboard mode
        if (this.forceKeyboardMode) {
            e.preventDefault();
            return;
        }
        
        if (e.touches.length > 0) {
            const rect = this.canvas.getBoundingClientRect();
            this.mouseX = e.touches[0].clientX - rect.left;
            e.preventDefault();
        }
    }
    
    // Handle touch start
    touchStart(e) {
        // Skip handling touches if in forced keyboard mode
        if (this.forceKeyboardMode) {
            e.preventDefault();
            return;
        }
        
        if (e.touches.length > 0) {
            const rect = this.canvas.getBoundingClientRect();
            this.mouseX = e.touches[0].clientX - rect.left;
            
            // If touch is in bottom area, trigger space (launch)
            const touchY = e.touches[0].clientY - rect.top;
            if (touchY > rect.height * 0.8) {
                this.keys.space = true;
            }
            
            e.preventDefault();
        }
    }
    
    // Handle touch end
    touchEnd(e) {
        // Reset space key on touch end
        this.keys.space = false;
        e.preventDefault();
    }
    
    // Get the current input state
    getInput() {
        // Detect one-shot button presses (pressed this frame but not last frame)
        const launchPressed = this.keys.space && !this.prevKeys.space;
        const pausePressed = this.keys.p && !this.prevKeys.p;
        const toggleControlPressed = this.keys.m && !this.prevKeys.m;
        const keyboardModePressed = this.keys.k && !this.prevKeys.k;
        const fullscreenPressed = this.keys.f && !this.prevKeys.f;
        
        // Handle keyboard mode toggle
        if (keyboardModePressed) {
            this.forceKeyboardMode = !this.forceKeyboardMode;
            console.log("Keyboard-only mode:", this.forceKeyboardMode ? "ON" : "OFF");
            // Reset mouse position if entering keyboard mode
            if (this.forceKeyboardMode) {
                this.mouseX = null;
            }
        }
        
        // Handle fullscreen toggle
        if (fullscreenPressed) {
            this.toggleFullscreen();
        }
        
        // Update previous state for next frame
        this.prevKeys.space = this.keys.space;
        this.prevKeys.p = this.keys.p;
        this.prevKeys.m = this.keys.m;
        this.prevKeys.k = this.keys.k;
        this.prevKeys.f = this.keys.f;
        
        // Return current input state
        return {
            leftPressed: this.keys.left,
            rightPressed: this.keys.right,
            launchPressed: launchPressed,
            pausePressed: pausePressed,
            toggleControlPressed: toggleControlPressed,
            keyboardModePressed: keyboardModePressed,
            fullscreenPressed: fullscreenPressed,
            forceKeyboardMode: this.forceKeyboardMode,
            isFullscreen: this.isFullscreen,
            mouseX: this.forceKeyboardMode ? null : this.mouseX
        };
    }
    
    // Clean up event listeners (call when game ends)
    destroy() {
        window.removeEventListener('keydown', this.keyDown);
        window.removeEventListener('keyup', this.keyUp);
        this.canvas.removeEventListener('mousemove', this.mouseMove);
        this.canvas.removeEventListener('touchmove', this.touchMove);
        this.canvas.removeEventListener('touchstart', this.touchStart);
        this.canvas.removeEventListener('touchend', this.touchEnd);
        document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
        document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
    }
}