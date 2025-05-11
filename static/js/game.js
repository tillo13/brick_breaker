/**
 * Main game script that initializes and runs the game loop
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
    console.log("Game initializing...");
    
    // Get the canvas element and context
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    
    // Initialize game objects
    const gameState = new GameState();
    const renderer = new GameRenderer(ctx);
    const controls = new GameControls(canvas);
    const soundManager = new SoundManager();
    
    // Make soundManager globally available
    window.soundManager = soundManager;
    
    // Get UI elements
    const livesEl = document.getElementById('lives');
    const scoreEl = document.getElementById('score');
    const levelEl = document.getElementById('level');
    const gameOverEl = document.getElementById('gameOver');
    const levelCompleteEl = document.getElementById('levelComplete');
    const pauseMenuEl = document.getElementById('pauseMenu');
    const finalScoreEl = document.getElementById('finalScore');
    const highScoreEl = document.getElementById('highScore');
    const levelScoreEl = document.getElementById('levelScore');

    // Get URL parameters to determine if we're in test mode
    const urlParams = new URLSearchParams(window.location.search);
    const levelParam = urlParams.get('level');
    const modeParam = urlParams.get('mode');
    
    // Set test mode flag
    gameState.isTestMode = (modeParam === 'test');
    
    console.log(`Game mode: ${gameState.isTestMode ? 'TEST' : 'NORMAL'}`);
    console.log(`Loading level: ${levelParam || 1}`);
    
    // Update UI elements for test mode
    if (gameState.isTestMode) {
        // Change game title
        document.title = `TESTING - Level ${levelParam || 1}`;
        
        // Update level complete UI
        const levelCompleteTitle = document.querySelector('#levelComplete h2');
        if (levelCompleteTitle) {
            levelCompleteTitle.textContent = 'Test Complete!';
        }
        
        const nextLevelBtn = document.getElementById('nextLevelButton');
        if (nextLevelBtn) {
            nextLevelBtn.textContent = 'Return to Editor';
        }
        
        // Update game over UI
        const gameOverTitle = document.querySelector('#gameOver h2');
        if (gameOverTitle) {
            gameOverTitle.textContent = 'Test Failed!';
        }
        
        const restartBtn = document.getElementById('restartButton');
        if (restartBtn) {
            restartBtn.textContent = 'Try Again';
        }
    }
    
    // Add button event listeners
    document.getElementById('restartButton').addEventListener('click', () => {
        console.log("Restart button clicked");
        gameOverEl.style.display = 'none';
        
        if (gameState.isTestMode) {
            // In test mode, reload the current level
            const levelParam = urlParams.get('level');
            if (levelParam) {
                console.log(`Reloading test level: ${levelParam}`);
                fetch(`/api/levels/level-${levelParam}`)
                    .then(response => response.json())
                    .then(levelData => {
                        gameState.init(levelData);
                    })
                    .catch(error => {
                        console.error('Error reloading test level:', error);
                        gameState.resetGame();
                    });
            } else {
                gameState.resetGame();
            }
        } else {
            // Normal game mode
            gameState.resetGame();
        }
    });
    
    document.getElementById('nextLevelButton').addEventListener('click', () => {
        console.log("Next level/return button clicked");
        levelCompleteEl.style.display = 'none';
        
        if (gameState.isTestMode) {
            // In test mode, return to editor
            // The lastEditedLevel is already in localStorage from when the test started
            console.log("Returning to editor with last edited level");
            window.location.href = '/editor';
            return;
        }
        
        // Normal game mode - advance to next level
        console.log(`Advancing to level ${gameState.level + 1}`);
        fetch(`/api/levels/advance`, {
            method: 'POST'
        })
        .then(() => {
            // Load the new level data
            return fetch(`/api/levels/level-${gameState.level + 1}`);
        })
        .then(response => response.json())
        .then(levelData => {
            gameState.nextLevel();
        })
        .catch(error => {
            console.error('Error advancing to next level:', error);
            gameState.nextLevel(); // Fall back to client-side handling
        });
    });
    
    document.getElementById('resumeButton').addEventListener('click', () => {
        console.log("Resume button clicked");
        pauseMenuEl.style.display = 'none';
        gameState.paused = false;
    });
    
    document.getElementById('quitButton').addEventListener('click', () => {
        console.log("Quit button clicked");
        if (gameState.isTestMode) {
            // In test mode, return to editor
            console.log("Returning to editor from pause menu");
            window.location.href = '/editor';
        } else {
            // Normal game mode, return to home
            window.location.href = '/';
        }
    });
    
    // Keyboard shortcuts for testing
    if (gameState.isTestMode) {
        window.addEventListener('keydown', (e) => {
            // Add test-specific shortcuts
            if (e.key === 'Escape') {
                // Escape key returns to editor
                console.log("Escape key pressed - returning to editor");
                window.location.href = '/editor';
            }
        });
    }
    

    // Load the level data
    function loadLevel() {
        console.log('Loading game level...');
        
        // Get level from URL query param if present
        // Use the full level ID instead of just the number
        const urlParams = new URLSearchParams(window.location.search);
        const levelId = urlParams.get('level') || 'level-1';
        
        console.log(`Attempting to load level with ID: ${levelId}`);
        
        // Fetch level data from server using the full level ID
        return fetch(`/api/levels/${levelId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(levelData => {
                console.log('Level data loaded:', levelData.id);
                
                // Check if this is an editor-created level
                if (levelData.editor_version) {
                    console.log('This is an editor-created level');
                    gameState.isEditorLevel = true;
                }
                
                return levelData;
            })
            .catch(error => {
                console.error('Error loading level data:', error);
                
                // Return a default level if API fails
                return {
                    id: levelId,
                    name: `Level ${levelId}`,
                    editor_version: false,
                    bricks: []
                };
            });
    }
    
    // Initialize game with level data
    function initGame(levelData) {
        console.log('Initializing game with level:', levelData.id);
        
        gameState.init(levelData);
        updateUI();
        
        // Start the game loop
        requestAnimationFrame(gameLoop);
    }
    
    // Main game loop
    let lastTimestamp = 0;
    function gameLoop(timestamp) {
        // Calculate time since last frame (in seconds)
        if (!lastTimestamp) lastTimestamp = timestamp;
        const deltaTime = Math.min((timestamp - lastTimestamp) / 1000, 0.1); // Cap at 100ms
        lastTimestamp = timestamp;
        
        // Get user input
        const input = controls.getInput();
        
        // Update keyboard mode state in gameState
        if (input.keyboardModePressed) {
            gameState.forceKeyboardMode = input.forceKeyboardMode;
        }
        
        // Update fullscreen state in gameState
        gameState.isFullscreen = input.isFullscreen;
        
        // Handle pause toggle
        if (input.pausePressed) {
            gameState.paused = !gameState.paused;
            
            // Show/hide pause menu
            if (gameState.paused) {
                pauseMenuEl.style.display = 'flex';
            } else {
                pauseMenuEl.style.display = 'none';
            }
        }
        
        // Always update paddle (even when paused)
        gameState.paddle.update(deltaTime, input);
        
        // Update game objects if not paused
        if (!gameState.paused && !gameState.gameOver && !gameState.levelComplete) {
            gameState.update(deltaTime, input);
            
            // Check for level completion
            if (gameState.levelComplete) {
                console.log("Level complete!");
                levelScoreEl.textContent = `Score: ${gameState.score}`;
                levelCompleteEl.style.display = 'flex';
            }
            
            // Check for game over
            if (gameState.gameOver) {
                console.log("Game over!");
                finalScoreEl.textContent = `Score: ${gameState.score}`;
                highScoreEl.textContent = `High Score: ${gameState.highScore}`;
                gameOverEl.style.display = 'flex';
            }
            
            // Update score and lives display
            updateUI();
        }
        
        // Draw everything
        renderer.render(gameState);
        
        // Continue game loop
        requestAnimationFrame(gameLoop);
    }
    
    // Update UI elements
    function updateUI() {
        // Update basic game info
        livesEl.textContent = `Lives: ${gameState.lives}`;
        scoreEl.textContent = `Score: ${gameState.score}`;
        
        // Show level number with appropriate indicators
        let levelText = `Level: ${gameState.level}`;
        
        // Add special indicators
        if (gameState.isEditorLevel) {
            levelText += " (Editor)";
        }
        if (gameState.isTestMode) {
            levelText += " [TEST]";
        }
        
        levelEl.textContent = levelText;
    }
    
    // Start the game
    console.log("Starting game...");
    loadLevel().then(initGame);
});