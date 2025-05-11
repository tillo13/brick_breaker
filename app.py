from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import json
import time
import socket
import webbrowser
import threading
import subprocess
import sys
import platform
from utils.level_loader import load_level, save_level, generate_level, create_sample_levels, save_editor_level
from utils.game_renderer import generate_level_preview, generate_game_screenshot
from utils.game_engine import GameEngine

def check_port_available(port, host='127.0.0.1'):
    """Check if the specified port is available on the host"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind((host, port))
            return True
    except:
        return False

def get_processes_on_port(port):
    """Get list of process IDs using the specified port"""
    system = platform.system()
    pids = []
    
    try:
        if system == 'Darwin':  # macOS
            try:
                # Find process IDs using lsof
                cmd = ["lsof", "-i", f":{port}", "-t"]
                output = subprocess.check_output(cmd).decode().strip()
                if output:
                    pids = output.split('\n')
            except subprocess.CalledProcessError:
                pass
                
        elif system == 'Linux':
            try:
                # Find process IDs using fuser
                cmd = ["fuser", f"{port}/tcp"]
                output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
                if output:
                    pids = output.split()
            except subprocess.CalledProcessError:
                pass
                
        elif system == 'Windows':
            try:
                # Windows command to find process on port
                cmd = f'netstat -ano | findstr :{port}'
                output = subprocess.check_output(cmd, shell=True).decode()
                if output:
                    lines = output.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line and ('LISTENING' in line or 'ESTABLISHED' in line):
                            # The PID is the last column
                            pid = line.strip().split()[-1]
                            pids.append(pid)
            except subprocess.CalledProcessError:
                pass
                
    except Exception as e:
        print(f"Error getting processes on port {port}: {e}")
        
    return [pid.strip() for pid in pids if pid.strip()]

def kill_process_on_port(port):
    """Force kill all processes using the specified port"""
    system = platform.system()
    killed = False
    
    pids = get_processes_on_port(port)
    if not pids:
        print(f"No processes found using port {port}")
        return True  # Port should be available
        
    print(f"Found {len(pids)} processes using port {port}")
    
    for pid in pids:
        try:
            print(f"Killing process {pid} using port {port}")
            
            if system == 'Windows':
                subprocess.call(f'taskkill /F /PID {pid}', shell=True)
            else:
                # For macOS and Linux
                subprocess.call(['kill', '-9', pid])
                
            killed = True
        except Exception as e:
            print(f"Error killing process {pid}: {e}")
    
    # Wait for processes to terminate
    time.sleep(2)
    
    # Verify port is available now
    return check_port_available(port)

def open_browser(port):
    """Open browser after a short delay to ensure server is running"""
    time.sleep(2)  # Wait for the Flask server to start
    url = f"http://127.0.0.1:{port}/"
    print(f"Opening browser at {url}")
    webbrowser.open(url)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.DevelopmentConfig')

# Initialize game engine with config
game_engine = GameEngine(app.config['GAME_SETTINGS'])

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/game')
def game():
    """Render the game page"""
    # Get level parameter if provided - use the full level ID
    level = request.args.get('level', 'level-1')
    return render_template('game.html', level=level)

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.route('/api/levels')
def get_levels():
    """Return a list of available levels"""
    levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
    
    # Create directory if it doesn't exist
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
        
    # Create sample levels if no levels exist
    level_files = [f for f in os.listdir(levels_dir) if f.endswith('.json')]
    if not level_files:
        create_sample_levels(levels_dir)
        level_files = [f for f in os.listdir(levels_dir) if f.endswith('.json')]
    
    levels = []
    
    for level_file in level_files:
        level_path = os.path.join(levels_dir, level_file)
        try:
            with open(level_path, 'r') as f:
                level_data = json.load(f)
                
                # Generate a preview image for this level
                preview_image = generate_level_preview(level_data)
                
                # Extract level ID
                level_id = level_data.get('id', level_file.split('.')[0])
                
                # Extract level name
                level_name = level_data.get('name', f"Level {level_id}")
                
                # Try to extract a level number for sorting
                level_num = 0
                if level_id.startswith('level-'):
                    parts = level_id.split('-')
                    if len(parts) > 1:
                        # Try to get the first numeric part
                        part = parts[1].split('_')[0] if '_' in parts[1] else parts[1]
                        if part.isdigit():
                            level_num = int(part)
                
                # Check if this is an editor-created level
                is_editor_level = level_data.get('editor_version', False)
                
                levels.append({
                    'id': level_id,
                    'name': level_name,
                    'preview': preview_image,
                    'level_num': level_num,  # Store level number separately for sorting
                    'is_editor_level': is_editor_level  # Add flag for editor levels
                })
        except Exception as e:
            print(f"Error loading level file {level_file}: {e}")
    
    # Sort levels by their numeric id
    levels.sort(key=lambda x: x['level_num'])
    
    return jsonify(levels)

@app.route('/api/levels/<level_id>')
def get_level(level_id):
    """Return data for a specific level"""
    levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
    
    # First try exact match with provided level_id
    level_file = f"{level_id}.json"
    level_path = os.path.join(levels_dir, level_file)
    
    # Check if the file exists with the exact requested level_id
    if os.path.exists(level_path):
        try:
            with open(level_path, 'r') as f:
                level_data = json.load(f)
            print(f"Found and loaded level: {level_id}")
            return jsonify(level_data)
        except Exception as e:
            print(f"Error reading level file {level_path}: {e}")
            return jsonify({'error': 'Invalid level file'}), 500
    
    # If not found, try legacy format (level-N)
    if level_id.startswith('level-'):
        try:
            # Try to extract level number for backward compatibility
            level_parts = level_id.split('-')
            if len(level_parts) > 1:
                # Handle complex level IDs that contain multiple hyphens
                level_num_part = level_parts[1].split('_')[0]  # Get part before first underscore if exists
                if level_num_part.isdigit():
                    level_num = int(level_num_part)
                    
                    # Try standard level file name format
                    std_level_file = f"level-{level_num}.json"
                    std_level_path = os.path.join(levels_dir, std_level_file)
                    
                    if os.path.exists(std_level_path):
                        with open(std_level_path, 'r') as f:
                            level_data = json.load(f)
                        print(f"Found and loaded legacy level: {std_level_file}")
                        return jsonify(level_data)
        except Exception as e:
            print(f"Error handling legacy level format: {e}")
    
    # If not found, generate a level
    print(f"Level {level_id} not found, generating a level")
    try:
        # Try to extract a level number for generation
        level_num = 1  # Default
        if level_id.startswith('level-'):
            parts = level_id.split('-')
            if len(parts) > 1:
                try:
                    # Try to get first numeric part
                    for part in parts[1:]:
                        if '_' in part:
                            # Handle underscore separator
                            subparts = part.split('_')
                            if subparts[0].isdigit():
                                level_num = int(subparts[0])
                                break
                        elif part.isdigit():
                            level_num = int(part)
                            break
                except:
                    pass
        
        # Generate the level
        level_data = generate_level(level_num, 
                                   app.config['GAME_SETTINGS']['SCREEN_WIDTH'],
                                   app.config['GAME_SETTINGS']['SCREEN_HEIGHT'])
        
        # Ensure the level ID matches request
        level_data['id'] = level_id
        
        # Save the generated level
        with open(level_path, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        return jsonify(level_data)
    except Exception as e:
        print(f"Error generating level: {e}")
        # Return a very basic level as fallback
        return jsonify({
            "id": level_id,
            "name": f"Level {level_id}",
            "bricks": []
        })

@app.route('/api/levels/<level_id>', methods=['POST'])
def save_level_data(level_id):
    """Save data for a specific level"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    level_data = request.json
    
    # Ensure the level ID matches
    level_data['id'] = level_id
    
    # Save the level data
    levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
    
    # Extract level number if available
    level_num = 1  # Default
    if level_id.startswith('level-'):
        parts = level_id.split('-')
        if len(parts) > 1 and parts[1].isdigit():
            level_num = int(parts[1])
    
    # Use standard save (not editor mode)
    save_level(level_data, level_num, levels_dir, editor_mode=False)
    
    return jsonify({'status': 'success'})

@app.route('/api/editor/levels/create', methods=['POST'])
def create_editor_level():
    """Create a new level from editor data with editor-specific handling"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    try:
        level_data = request.json
        
        # Ensure required fields
        if 'id' not in level_data or 'name' not in level_data or 'bricks' not in level_data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get the level ID directly from the data
        level_id = level_data['id']
        
        # Mark as editor-created
        level_data['editor_version'] = True
        
        # Process bricks to ensure all properties are set
        if 'bricks' in level_data:
            for brick in level_data['bricks']:
                # Mark as editor-placed
                brick['editor_placed'] = True
                
                # Ensure has_powerup is set
                if 'has_powerup' not in brick:
                    brick['has_powerup'] = False
                    
                # Ensure powerup_type is set if has_powerup is True
                if brick['has_powerup'] and 'powerup_type' not in brick:
                    brick['powerup_type'] = 0
        
        # Save the level
        levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
        
        # Ensure the directory exists
        if not os.path.exists(levels_dir):
            os.makedirs(levels_dir)
        
        # Create the level file name
        level_file = f"{level_id}.json"
        level_path = os.path.join(levels_dir, level_file)
        
        # Save the level file
        with open(level_path, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        print(f"Successfully saved editor level: {level_id}")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"Error creating editor level: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/levels/create', methods=['POST'])
def create_new_level():
    """Create a new level from editor data"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    level_data = request.json
    
    # Ensure required fields
    if 'id' not in level_data or 'name' not in level_data or 'bricks' not in level_data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get level ID
    level_id = level_data['id']
    
    # Check if this is an editor-created level
    editor_mode = level_data.get('editor_version', False)
    
    # Save the level using the appropriate function
    levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
    
    # Ensure the directory exists
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
    
    # Save the level file
    level_file = f"{level_id}.json"
    level_path = os.path.join(levels_dir, level_file)
    
    with open(level_path, 'w') as f:
        json.dump(level_data, f, indent=2)
    
    return jsonify({'status': 'success'})

@app.route('/api/highscores', methods=['GET'])
def get_highscores():
    """Return the high scores list"""
    high_scores_path = os.path.join(os.path.dirname(__file__), 'high_scores.json')
    
    if not os.path.exists(high_scores_path):
        # Create default high scores if file doesn't exist
        high_scores = [
            {'name': 'AAA', 'score': 5000, 'level': 3},
            {'name': 'BBB', 'score': 4000, 'level': 2},
            {'name': 'CCC', 'score': 3000, 'level': 2},
            {'name': 'DDD', 'score': 2000, 'level': 1},
            {'name': 'EEE', 'score': 1000, 'level': 1}
        ]
        
        with open(high_scores_path, 'w') as f:
            json.dump(high_scores, f)
    else:
        # Load existing high scores
        with open(high_scores_path, 'r') as f:
            high_scores = json.load(f)
    
    return jsonify(high_scores)

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    """Add a new high score"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    score_data = request.json
    
    # Validate required fields
    if 'name' not in score_data or 'score' not in score_data:
        return jsonify({'error': 'Name and score are required'}), 400
    
    # Load existing high scores
    high_scores_path = os.path.join(os.path.dirname(__file__), 'high_scores.json')
    
    if os.path.exists(high_scores_path):
        with open(high_scores_path, 'r') as f:
            high_scores = json.load(f)
    else:
        high_scores = []
    
    # Add the new score
    high_scores.append({
        'name': score_data['name'],
        'score': score_data['score'],
        'level': score_data.get('level', 1),
        'date': time.strftime('%Y-%m-%d')
    })
    
    # Sort and limit to top 10
    high_scores.sort(key=lambda x: x['score'], reverse=True)
    high_scores = high_scores[:10]
    
    # Save the updated high scores
    with open(high_scores_path, 'w') as f:
        json.dump(high_scores, f)
    
    return jsonify({'status': 'success', 'rank': high_scores.index(score_data) + 1})

@app.route('/api/level_preview/<level_id>')
def get_level_preview(level_id):
    """Generate a preview image for a level"""
    levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
    level_file = f"{level_id}.json"
    level_path = os.path.join(levels_dir, level_file)
    
    if not os.path.exists(level_path):
        return jsonify({'error': 'Level not found'}), 404
    
    with open(level_path, 'r') as f:
        level_data = json.load(f)
    
    # Generate the preview image
    preview_image = generate_level_preview(level_data)
    
    return jsonify({'preview': preview_image})

@app.route('/admin/levels')
def admin_levels():
    """Admin page for managing levels"""
    # In a real app, this would require authentication
    return render_template('admin_levels.html')

@app.route('/admin/create_level/<int:level_num>', methods=['GET'])
def create_level(level_num):
    """Create a new level"""
    # Generate the level
    level_data = generate_level(level_num, 
                               app.config['GAME_SETTINGS']['SCREEN_WIDTH'],
                               app.config['GAME_SETTINGS']['SCREEN_HEIGHT'])
    
    # Save the level
    levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
    save_level(level_data, level_num, levels_dir)
    
    return redirect(url_for('admin_levels'))

@app.route('/api/levels/advance', methods=['POST'])
def advance_level():
    """Advance to the next level"""
    game_engine.advance_to_next_level()
    return jsonify({'status': 'success'})


@app.route('/editor')
def editor():
    """Render the level editor page"""
    return render_template('editor.html')

if __name__ == '__main__':
    # Handle command-line arguments for debug mode
    import argparse
    parser = argparse.ArgumentParser(description='Run the Super Brick Breaker Deluxe game')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (may use other ports)')
    args = parser.parse_args()

    # Create levels directory if it doesn't exist
    levels_dir = os.path.join(os.path.dirname(__file__), 'levels')
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
        # Create sample levels
        create_sample_levels(levels_dir)
    
    port = 5000
    
    # If we're not in debug mode, ensure port 5000 is available
    if not args.debug:
        print(f"Checking if port {port} is available...")
        if not check_port_available(port):
            print(f"Port {port} is busy, attempting to kill processes...")
            if kill_process_on_port(port):
                print(f"Successfully freed port {port}")
            else:
                print(f"WARNING: Could not free port {port}, but will try to use it anyway")
    
        # Launch browser in a separate thread
        browser_thread = threading.Thread(target=open_browser, args=(port,))
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run Flask with debug mode OFF
        print(f"Starting Super Brick Breaker Deluxe on port {port} (debug mode OFF)")
        app.run(debug=False, port=port)
    else:
        # In debug mode, Flask will handle port conflicts automatically
        print(f"Starting Super Brick Breaker Deluxe in debug mode (may use alternate port)")
        app.run(debug=True)