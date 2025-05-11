/**
 * Level Editor for Super Brick Breaker Deluxe
 * This file provides the level editor functionality.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Get canvas and context
    const canvas = document.getElementById('editorCanvas');
    const ctx = canvas.getContext('2d');
    
    // Editor state
    const state = {
        bricks: [],
        gridWidth: 10,
        gridHeight: 20,
        brickWidth: 75,
        brickHeight: 20,
        gridOffset: { x: 50, y: 40 },
        selectedTool: 'place', // 'place' or 'remove'
        selectedStrength: 1,
        hasPowerup: false,
        powerupType: 0,
        levelId: '',  // Will be generated based on name
        levelName: 'New Level',
        nextLevelNumber: 1,
        currentSessionId: null // To track the current editing session
    };
    
    // Brick colors (copied from game_objects.js)
    const brickColors = [
        '#ff3232', // Red (strength 1)
        '#ffcc00', // Yellow (strength 2)
        '#32ff32', // Green (strength 3)
        '#3232ff'  // Blue (strength 4+)
    ];
    
    // Powerup colors and symbols (from game_objects.js)
    const powerupColors = [
        '#32ff32', // Expand (green)
        '#ff3232', // Shrink (red)
        '#00ccff', // Multi (cyan)
        '#3232ff', // Slow (blue)
        '#ff9900', // Fast (orange)
        '#ffcc00', // Laser (yellow)
        '#cc00ff', // Life (purple)
        '#ffcc00'  // Thru (yellow)
    ];
    
    const powerupSymbols = ['+', '-', 'M', 'S', 'F', 'L', '♥', 'T'];
    
    // DOM elements
    const levelSelect = document.getElementById('levelSelect');
    const loadLevelBtn = document.getElementById('loadLevelBtn');
    const newLevelBtn = document.getElementById('newLevelBtn');
    const placeBrickBtn = document.getElementById('placeBrickBtn');
    const removeBrickBtn = document.getElementById('removeBrickBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const brickTypes = document.getElementById('brickTypes');
    const hasPowerupCheckbox = document.getElementById('hasPowerup');
    const powerupTypeSelect = document.getElementById('powerupType');
    const levelNameInput = document.getElementById('levelName');
    const levelIdInput = document.getElementById('levelId');
    const saveBtn = document.getElementById('saveBtn');
    const testBtn = document.getElementById('testBtn');
    
    // Initialize the editor
    function init() {
        console.log('Initializing level editor...');
        
        // Set up event listeners
        setupEventListeners();
        
        // Generate a new unique session ID for this editing session
        state.currentSessionId = generateSessionId();
        
        // Load available levels for the dropdown (but don't select any)
        loadLevelList().then(() => {
            // Check for returning from test mode - load the last edited level
            const lastEditedLevel = localStorage.getItem('lastEditedLevel');
            
            // If we're returning from testing the level we were just working on
            if (lastEditedLevel) {
                console.log(`Loading last edited level: ${lastEditedLevel}`);
                
                // Select the level in the dropdown if it exists
                if (levelSelect.querySelector(`option[value="${lastEditedLevel}"]`)) {
                    levelSelect.value = lastEditedLevel;
                }
                
                // Fetch the level data
                fetch(`/api/levels/${lastEditedLevel}`)
                    .then(response => response.json())
                    .then(levelData => {
                        // Update state
                        state.levelId = levelData.id;
                        state.levelName = levelData.name;
                        state.bricks = levelData.bricks || [];
                        
                        // Mark all loaded bricks as editor-placed
                        state.bricks.forEach(brick => {
                            brick.editor_placed = true;
                        });
                        
                        // Update inputs
                        levelNameInput.value = state.levelName;
                        levelIdInput.value = state.levelId;
                        
                        // Update display
                        render();
                        
                        // Don't clear the localStorage - keep the same level in memory
                        // for continued editing/testing cycle
                        
                        console.log(`Successfully loaded level: ${state.levelName}`);
                    })
                    .catch(error => {
                        console.error('Error loading last edited level:', error);
                        // Fall back to creating a new level
                        createNewLevel();
                    });
            } else {
                // No last level to load, create a new level immediately
                createNewLevel();
            }
        });
    }
    
    // Generate a unique ID for the editing session
    function generateSessionId() {
        return `session_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
    }
    
    // Generate a unique ID based on the level name and session
    function generateUniqueId(name) {
        // Start with name, remove special chars, replace spaces with underscores
        let id = name.trim()
            .replace(/[^a-zA-Z0-9 ]/g, '')
            .replace(/\s+/g, '_')
            .toLowerCase();
        
        // Add current session ID to ensure uniqueness but consistency across tests
        return `level-${id}_${state.currentSessionId}`;
    }
    
    // Set up editor defaults
    function setupDefaults() {
        // Set initial tool
        selectTool('place');
        
        // Select default brick type
        selectBrickType(1);
        
        // Initial render
        render();
    }
    
    // Load the list of available levels
    function loadLevelList() {
        return fetch('/api/levels')
            .then(response => response.json())
            .then(levels => {
                // Clear existing options
                levelSelect.innerHTML = '';
                
                // Find the highest level number for new levels
                let maxLevel = 0;
                
                // Add options for each level
                levels.forEach(level => {
                    const option = document.createElement('option');
                    option.value = level.id;
                    option.textContent = level.name;
                    levelSelect.appendChild(option);
                    
                    // Extract level number if it follows the pattern level-X
                    if (level.id.startsWith('level-')) {
                        const levelNumStr = level.id.split('-')[1];
                        if (levelNumStr && !isNaN(parseInt(levelNumStr))) {
                            const levelNum = parseInt(levelNumStr);
                            if (levelNum > maxLevel) {
                                maxLevel = levelNum;
                            }
                        }
                    }
                });
                
                // Set next level number
                state.nextLevelNumber = maxLevel + 1;
            })
            .catch(error => {
                console.error('Error loading level list:', error);
            });
    }
    
    // Set up event listeners
    function setupEventListeners() {
        // Tool buttons
        placeBrickBtn.addEventListener('click', () => selectTool('place'));
        removeBrickBtn.addEventListener('click', () => selectTool('remove'));
        clearAllBtn.addEventListener('click', clearAllBricks);
        
        // Brick type selection
        Array.from(brickTypes.children).forEach(preview => {
            preview.addEventListener('click', () => {
                const strength = parseInt(preview.dataset.strength, 10);
                selectBrickType(strength);
            });
        });
        
        // Powerup controls
        hasPowerupCheckbox.addEventListener('change', () => {
            state.hasPowerup = hasPowerupCheckbox.checked;
        });
        
        powerupTypeSelect.addEventListener('change', () => {
            state.powerupType = parseInt(powerupTypeSelect.value, 10);
        });
        
        // Canvas click
        canvas.addEventListener('click', handleCanvasClick);
        
        // Level controls
        loadLevelBtn.addEventListener('click', loadSelectedLevel);
        newLevelBtn.addEventListener('click', createNewLevel);
        
        // Save and test
        saveBtn.addEventListener('click', saveLevel);
        testBtn.addEventListener('click', testLevel);
        
        // Update level name and generate new ID on name change
        levelNameInput.addEventListener('input', () => {
            state.levelName = levelNameInput.value;
            // Don't automatically update ID as user types, wait until save
        });
    }
    
    // Handle clicks on the canvas
    function handleCanvasClick(e) {
        // Get mouse position
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Convert to grid position
        const gridX = Math.floor((mouseX - state.gridOffset.x) / state.brickWidth);
        const gridY = Math.floor((mouseY - state.gridOffset.y) / state.brickHeight);
        
        // Check if position is valid
        if (gridX >= 0 && gridX < state.gridWidth && gridY >= 0 && gridY < state.gridHeight) {
            if (state.selectedTool === 'place') {
                placeBrick(gridX, gridY);
            } else if (state.selectedTool === 'remove') {
                removeBrick(gridX, gridY);
            }
        }
    }
    
    // Place a brick at the specified grid position
    function placeBrick(gridX, gridY) {
        // Check if a brick already exists at this position
        const existingBrickIndex = state.bricks.findIndex(brick => 
            brick.col === gridX && brick.row === gridY);
        
        // If exists, remove it (will be replaced)
        if (existingBrickIndex !== -1) {
            state.bricks.splice(existingBrickIndex, 1);
        }
        
        // Create new brick with explicit editor properties
        const brick = {
            row: gridY,
            col: gridX,
            x: state.gridOffset.x + gridX * state.brickWidth,
            y: state.gridOffset.y + gridY * state.brickHeight,
            width: state.brickWidth,
            height: state.brickHeight,
            strength: state.selectedStrength,
            has_powerup: state.hasPowerup,
            powerup_type: state.powerupType,
            editor_placed: true  // Mark as placed in the editor
        };
        
        // Add to bricks array
        state.bricks.push(brick);
        
        // Update display
        render();
    }
    
    // Remove a brick at the specified grid position
    function removeBrick(gridX, gridY) {
        // Find the brick at this position
        const brickIndex = state.bricks.findIndex(brick => 
            brick.col === gridX && brick.row === gridY);
        
        // If found, remove it
        if (brickIndex !== -1) {
            state.bricks.splice(brickIndex, 1);
            
            // Update display
            render();
        }
    }
    
    // Clear all bricks from the level
    function clearAllBricks() {
        if (confirm('Are you sure you want to clear all bricks?')) {
            state.bricks = [];
            render();
        }
    }
    
    // Select a tool (place or remove)
    function selectTool(tool) {
        state.selectedTool = tool;
        
        // Update button styling
        if (tool === 'place') {
            placeBrickBtn.classList.add('selected');
            removeBrickBtn.classList.remove('selected');
        } else {
            placeBrickBtn.classList.remove('selected');
            removeBrickBtn.classList.add('selected');
        }
    }
    
    // Select a brick type (strength)
    function selectBrickType(strength) {
        state.selectedStrength = strength;
        
        // Update preview styling
        Array.from(brickTypes.children).forEach(preview => {
            const previewStrength = parseInt(preview.dataset.strength, 10);
            if (previewStrength === strength) {
                preview.classList.add('selected');
            } else {
                preview.classList.remove('selected');
            }
        });
    }
    
    // Load the selected level
    function loadSelectedLevel() {
        const selectedLevelId = levelSelect.value;
        if (!selectedLevelId) return;
        
        fetch(`/api/levels/${selectedLevelId}`)
            .then(response => response.json())
            .then(levelData => {
                // Update state
                state.levelId = levelData.id;
                state.levelName = levelData.name;
                state.bricks = levelData.bricks || [];
                
                // Mark all loaded bricks as editor-placed
                state.bricks.forEach(brick => {
                    brick.editor_placed = true;
                });
                
                // Update inputs
                levelNameInput.value = state.levelName;
                levelIdInput.value = state.levelId;
                
                // Update display
                render();
                
                console.log(`Loaded level: ${state.levelName}`);
            })
            .catch(error => {
                console.error('Error loading level:', error);
                alert('Error loading level. Please try again.');
            });
    }
    
    // Create a new empty level
    function createNewLevel() {
        // Generate a new unique level ID
        state.levelName = `New Level ${state.nextLevelNumber}`;
        state.levelId = generateUniqueId(state.levelName);
        state.bricks = [];
        
        // Update inputs
        levelNameInput.value = state.levelName;
        levelIdInput.value = state.levelId;
        
        // Set up editor defaults
        setupDefaults();
        
        console.log(`Created new level: ${state.levelName} with ID: ${state.levelId}`);
    }
    
    // Save the current level
    function saveLevel() {
        // Check if we have any bricks
        if (state.bricks.length === 0) {
            alert("Cannot save an empty level. Please add some bricks first.");
            return;
        }
        
        // If not already assigned, generate a unique ID based on the name
        if (!state.levelId) {
            state.levelId = generateUniqueId(state.levelName);
            levelIdInput.value = state.levelId;
        }
        
        // Prepare level data with editor flags
        const levelData = {
            id: state.levelId,
            name: state.levelName,
            editor_version: true,  // Mark as editor-created
            bricks: state.bricks.map(brick => ({
                ...brick,
                editor_placed: true  // Ensure all bricks are marked as editor-placed
            }))
        };
        
        // Show saving indicator
        const originalText = saveBtn.textContent;
        saveBtn.textContent = 'Saving...';
        saveBtn.disabled = true;
        
        // Use editor-specific endpoint
        fetch('/api/editor/levels/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(levelData)
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                // Show success message
                saveBtn.textContent = 'Saved!';
                setTimeout(() => {
                    saveBtn.textContent = originalText;
                    saveBtn.disabled = false;
                }, 1500);
                
                // Reload level list to include new level
                loadLevelList();
                
                console.log(`Saved level: ${state.levelName} with ID: ${state.levelId}`);
                
                // Save the current level ID to localStorage for returning from test
                localStorage.setItem('lastEditedLevel', state.levelId);
            } else {
                // Fallback to standard endpoint
                return fetch('/api/levels/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(levelData)
                }).then(response => response.json());
            }
            return null; // Return null to indicate no need for further processing
        })
        .then(result => {
            if (result === null) {
                // Already handled by first endpoint
                return;
            }
            
            if (result && result.status === 'success') {
                // Show success message if using fallback
                saveBtn.textContent = 'Saved!';
                setTimeout(() => {
                    saveBtn.textContent = originalText;
                    saveBtn.disabled = false;
                }, 1500);
                
                // Reload level list to include new level
                loadLevelList();
                
                console.log(`Saved level with fallback: ${state.levelName}`);
                
                // Save the current level ID to localStorage for returning from test
                localStorage.setItem('lastEditedLevel', state.levelId);
            } else if (result && result.error) {
                // Show error message
                saveBtn.textContent = 'Error!';
                setTimeout(() => {
                    saveBtn.textContent = originalText;
                    saveBtn.disabled = false;
                }, 1500);
                
                alert('Error saving level: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error saving level:', error);
            
            // Show error message
            saveBtn.textContent = 'Error!';
            setTimeout(() => {
                saveBtn.textContent = originalText;
                saveBtn.disabled = false;
            }, 1500);
            
            alert('Error saving level: ' + error.message);
        });
    }
    
    // Test the current level
    function testLevel() {
        // Make sure we have bricks to test
        if (state.bricks.length === 0) {
            alert("Cannot test an empty level. Please add some bricks first.");
            return;
        }
        
        // If not already saved, save the level automatically first
        if (!state.levelId) {
            state.levelId = generateUniqueId(state.levelName);
            levelIdInput.value = state.levelId;
        }
        
        // Show saving indicator
        const originalText = testBtn.textContent;
        testBtn.textContent = 'Saving...';
        testBtn.disabled = true;
        
        // Save level first with editor flags - automatically without user confirmation
        const levelData = {
            id: state.levelId,
            name: state.levelName,
            editor_version: true,  // Mark as editor-created
            bricks: state.bricks.map(brick => ({
                ...brick,
                editor_placed: true  // Ensure all bricks are marked as editor-placed
            }))
        };
        
        // Save the current level ID to localStorage for returning from test
        localStorage.setItem('lastEditedLevel', state.levelId);
        
        // Use editor-specific endpoint
        fetch('/api/editor/levels/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(levelData)
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success' || (result && result.status === 'success')) {
                // Show launching message
                testBtn.textContent = 'Launching...';
                
                // Use the full level ID in the URL to ensure correct level loading
                console.log(`Testing level with ID: ${state.levelId}`);
                window.location.href = `/game?level=${state.levelId}&mode=test`;
            } else if (result && result.error) {
                // Show error message
                testBtn.textContent = 'Error!';
                setTimeout(() => {
                    testBtn.textContent = originalText;
                    testBtn.disabled = false;
                }, 1500);
                
                alert('Error saving level: ' + result.error);
            }
        })
        .catch(error => {
            console.error('Error saving level:', error);
            
            // Show error message
            testBtn.textContent = 'Error!';
            setTimeout(() => {
                testBtn.textContent = originalText;
                testBtn.disabled = false;
            }, 1500);
            
            alert('Error saving level: ' + error.message);
        });
    }
    
    // Render the editor
    function render() {
        // Clear canvas
        ctx.fillStyle = '#000033';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid
        drawGrid();
        
        // Draw bricks
        drawBricks();
    }
    
    // Draw the grid
    function drawGrid() {
        // Draw light grid
        ctx.strokeStyle = 'rgba(100, 100, 255, 0.3)';
        ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x <= state.gridWidth; x++) {
            const xPos = state.gridOffset.x + x * state.brickWidth;
            ctx.beginPath();
            ctx.moveTo(xPos, state.gridOffset.y);
            ctx.lineTo(xPos, state.gridOffset.y + state.gridHeight * state.brickHeight);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= state.gridHeight; y++) {
            const yPos = state.gridOffset.y + y * state.brickHeight;
            ctx.beginPath();
            ctx.moveTo(state.gridOffset.x, yPos);
            ctx.lineTo(state.gridOffset.x + state.gridWidth * state.brickWidth, yPos);
            ctx.stroke();
        }
    }
    
    // Draw the bricks
    function drawBricks() {
        for (const brick of state.bricks) {
            // Fill with color based on strength
            ctx.fillStyle = brickColors[Math.min(brick.strength, 4) - 1];
            ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
            
            // Top and left highlight
            ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.fillRect(brick.x, brick.y, brick.width, 2);
            ctx.fillRect(brick.x, brick.y, 2, brick.height);
            
            // Bottom and right shadow
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.fillRect(brick.x, brick.y + brick.height - 2, brick.width, 2);
            ctx.fillRect(brick.x + brick.width - 2, brick.y, 2, brick.height);
            
            // If strength > 1, add number
            if (brick.strength > 1) {
                ctx.fillStyle = '#FFFFFF';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(
                    brick.strength.toString(),
                    brick.x + brick.width / 2,
                    brick.y + brick.height / 2
                );
            }
            
            // If has powerup, add a more noticeable indicator with symbol
            if (brick.has_powerup) {
                // Draw small powerup indicator in the corner
                const powerupType = brick.powerup_type;
                const powerupColor = powerupColors[powerupType];
                const powerupSymbol = powerupSymbols[powerupType];
                
                // Draw circular background
                ctx.fillStyle = powerupColor;
                ctx.beginPath();
                ctx.arc(
                    brick.x + brick.width - 10,
                    brick.y + 10,
                    8,
                    0,
                    Math.PI * 2
                );
                ctx.fill();
                
                // Draw symbol
                ctx.fillStyle = '#FFFFFF';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(
                    powerupSymbol,
                    brick.x + brick.width - 10,
                    brick.y + 10
                );
            }
        }
    }
    
    // Initialize the editor
    init();
});