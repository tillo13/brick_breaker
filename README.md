# Super Brick Breaker Deluxe

<<<<<<< HEAD
A modern implementation of the classic brick breaker game using Flask for the backend and vanilla JavaScript for the frontend. This project includes a full game engine, level editor, and testing environment.

![Brick Breaker Game](screenshot.png)

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Game Overview](#game-overview)
- [Controls](#controls)
- [Powerups](#powerups)
- [Level Editor](#level-editor)
- [Development](#development)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Complete Game Engine**: Fully implemented game physics, collision detection, and scoring system
- **Multiple Levels**: Play through progressively challenging levels
- **Interactive Level Editor**: Create and test your own custom levels
- **8 Unique Powerups**: Enhance gameplay with various special abilities
- **Responsive Design**: Play on desktop or mobile devices
- **Sound Effects**: Immersive audio feedback
- **Persistent High Scores**: Track your best performances

## Technologies

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Canvas API**: For rendering the game
- **LocalStorage API**: For saving player data and level information
- **RESTful API**: For level management and game state

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/tillo13/brick_breaker.git
   cd brick_breaker
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Game Overview

Super Brick Breaker Deluxe is a modern remake of the classic brick breaker arcade game. The goal is to break all bricks in each level by bouncing a ball off your paddle. Different colored bricks require different numbers of hits to break:

- **Red Bricks**: 1 hit
- **Yellow Bricks**: 2 hits
- **Green Bricks**: 3 hits
- **Blue Bricks**: 4 hits

Some bricks contain powerups that fall when broken. Collect these with your paddle to gain special abilities.

## Controls

- **Mouse Movement**: Move the paddle horizontally
- **Left/Right Arrow Keys**: Alternative paddle control
- **Spacebar**: Launch the ball from the paddle
- **P**: Pause the game
- **M**: Toggle between mouse and keyboard controls
- **K**: Force keyboard-only mode (ignores mouse input)
- **F**: Toggle fullscreen mode
- **S**: Toggle sound on/off

## Powerups

The game features 8 different powerups that can dramatically change gameplay:

| Symbol | Color  | Effect | Description |
|--------|--------|--------|-------------|
| +      | Green  | Expand | Increases paddle size |
| -      | Red    | Shrink | Decreases paddle size (negative) |
| M      | Cyan   | Multi  | Adds two extra balls to the game |
| S      | Blue   | Slow   | Decreases ball speed |
| F      | Orange | Fast   | Increases ball speed (negative) |
| L      | Yellow | Laser  | Allows the paddle to shoot lasers |
| ♥      | Purple | Life   | Grants an extra life |
| T      | Yellow | Thru   | Ball passes through bricks without bouncing |

## Level Editor

A key feature of Super Brick Breaker Deluxe is the built-in level editor that allows you to create custom levels.

### Editor Features

- **Grid-Based Layout**: Place bricks on a precise grid
- **Multiple Brick Types**: Choose from different brick strengths
- **Powerup Assignment**: Add powerups to specific bricks
- **Live Testing**: Test your level immediately
- **Save & Load**: Save your levels and come back to them later

### How to Use the Editor

1. **Access the Editor**: Click on "Editor" in the main navigation menu
2. **Create a New Level**: When the editor loads, it automatically creates a new blank level
3. **Place Bricks**: Click on the grid to place bricks
   - Use the brick type selector to change brick strength (1-4)
   - Check the "Add Powerup" box and select a type to add powerups to bricks
4. **Remove Bricks**: Switch to the "Remove Brick" tool and click on existing bricks
5. **Save Your Level**: Enter a name for your level and click "Save Level"
6. **Test Your Creation**: Click "Test Level" to play your level immediately
   - When you return from testing, you'll be back in the editor with the same level loaded
   - Continue refining and testing as needed

The editor now provides a seamless workflow:
- Creates a new level automatically when first opened
- Maintains your level state between test runs
- Returns to the same level after testing

## Development

### Running in Debug Mode

For development purposes, you can run the application in debug mode:

```
python app.py --debug
```

This will enable Flask's debug mode with hot reloading and detailed error messages.

### Creating Sample Levels

The application automatically generates sample levels if none exist. To force regeneration:

```
python debug_save.py
```

## Project Structure

```
.
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── debug_save.py           # Utility for creating test levels
├── gather_files.py         # Utility for project structure analysis
├── levels/                 # JSON files for game levels
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── sounds/             # Audio files
├── templates/              # HTML templates
└── utils/                  # Python utility modules
    ├── game_engine.py      # Core game logic
    ├── game_objects.py     # Game object definitions
    ├── game_renderer.py    # Rendering utilities
    └── level_loader.py     # Level loading/saving utilities
```

### Key Components

- **app.py**: The main Flask application that serves routes and handles API requests
- **game_engine.py**: The core game logic that handles physics, collisions, and game state
- **game_objects.py**: Definitions for the game objects (ball, paddle, bricks, powerups)
- **game_renderer.py**: Utilities for rendering game objects and generating previews
- **level_loader.py**: Functions to load, save, and generate levels
- **game.js**: Main frontend script that initializes and runs the game loop
- **game_state.js**: Manages game state on the frontend
- **level_editor.js**: Provides the level editor functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created by [tillo13](https://github.com/tillo13) - Feel free to contact me for any questions!
=======
A feature-rich implementation of the classic Brick Breaker game using Python and Pygame.

## Description

Super Brick Breaker Deluxe is a modern take on the classic arcade game where players control a paddle to bounce a ball and break bricks. This implementation includes multiple powerups, levels with increasing difficulty, special effects, and much more!

## Features

### Multiple Ball Types
- **Normal Ball**: Bounces off bricks and walls
- **Thru-Ball**: Can pass through multiple bricks without bouncing

### Advanced Powerup System
- **Expand Paddle** (Green +): Makes your paddle wider
- **Shrink Paddle** (Red -): Negative powerup that makes your paddle smaller
- **Multi-Ball** (Cyan M): Adds extra balls to the game
- **Slow Ball** (Blue S): Reduces ball speed for easier control
- **Fast Ball** (Orange F): Negative powerup that increases ball speed
- **Laser** (Yellow L): Gives your paddle the ability to shoot lasers
- **Extra Life** (Purple ♥): Gives you an additional life
- **Thru-Ball** (Yellow T): Makes balls pass through bricks without bouncing

### Level Progression
- Multiple unique level layouts that get progressively more challenging
- Bricks with different strength values (1-4 hits required to break)
- Visual indication of brick strength with numbers and colors

### Visual Effects
- Particle effects when bricks break
- Glowing effects for special powerups
- Animated powerups that rotate as they fall

### Game Mechanics
- Paddle physics that angles the ball based on where it hits
- Lasers that can destroy bricks from a distance
- Lives system with visual indicators
- Score tracking and high score saving

### User Experience
- Mouse or keyboard controls (toggle with M key)
- Pause functionality (P key)
- Level transition screens
- Game over screen with high score tracking

## Controls
- **Mouse Movement**: Move the paddle left and right
- **Left/Right Arrow Keys**: Alternative paddle control
- **Space Bar**: Launch ball / Start level
- **M Key**: Toggle between mouse and keyboard controls
- **P Key**: Pause game
- **R Key**: Reset (when all balls are lost)
- **Esc Key**: Quit game

## Requirements
- Python 3.x
- Pygame library

## Installation
1. Make sure you have Python installed on your system.
2. Install the Pygame library:
pip install pygame
3. Clone this repository or download the source code.
4. Run the game:
python brick_breaker.py

## Optional: Adding Sound Files
The game looks for the following sound files (not included):
- bounce.wav - Ball bouncing off walls/paddle
- brick.wav - Ball hitting bricks
- powerup.wav - Collecting powerups
- life_lost.wav - Losing a life
- level_complete.wav - Completing a level

If these files aren't present, the game will still run without sound.

## Screenshot
![Game Screenshot](screenshot.png)

## License
This project is open source and available under the MIT License.

## Credits
Created using Python and Pygame.
>>>>>>> c9b58f9b6b5210c1a80e74bceb16a1196c5e9847
