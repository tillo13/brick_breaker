import os
import json

# Configuration
levels_dir = "levels"
test_level_id = "level-test"

def check_levels_dir():
    """Check if levels directory exists and is writable"""
    print(f"Checking levels directory: {levels_dir}")
    
    # Check if directory exists
    if os.path.exists(levels_dir):
        print(f"✓ Directory exists: {levels_dir}")
        
        # Check if it's a directory
        if os.path.isdir(levels_dir):
            print(f"✓ Path is a directory: {levels_dir}")
        else:
            print(f"✗ Path is not a directory: {levels_dir}")
            return False
        
        # Check if it's writable
        if os.access(levels_dir, os.W_OK):
            print(f"✓ Directory is writable: {levels_dir}")
        else:
            print(f"✗ Directory is not writable: {levels_dir}")
            return False
    else:
        print(f"✗ Directory does not exist: {levels_dir}")
        
        # Try to create the directory
        try:
            os.makedirs(levels_dir)
            print(f"✓ Created directory: {levels_dir}")
        except Exception as e:
            print(f"✗ Failed to create directory: {e}")
            return False
    
    return True

def test_save_level():
    """Test creating a level file"""
    if not check_levels_dir():
        return False
    
    # Create a simple test level
    test_level = {
        "id": test_level_id,
        "name": "Test Level",
        "editor_version": True,
        "bricks": [
            {
                "row": 0,
                "col": 0,
                "x": 50,
                "y": 40,
                "width": 75,
                "height": 20,
                "strength": 1,
                "has_powerup": True,
                "powerup_type": 0,
                "editor_placed": True
            }
        ]
    }
    
    # Save the test level
    level_file = f"{test_level_id}.json"
    level_path = os.path.join(levels_dir, level_file)
    
    try:
        with open(level_path, 'w') as f:
            json.dump(test_level, f, indent=2)
        print(f"✓ Successfully saved test level: {level_path}")
        print(f"  File size: {os.path.getsize(level_path)} bytes")
        return True
    except Exception as e:
        print(f"✗ Failed to save test level: {e}")
        return False

def list_existing_levels():
    """List existing level files"""
    print("\nExisting level files:")
    
    if not os.path.exists(levels_dir):
        print("  (levels directory does not exist)")
        return
    
    level_files = [f for f in os.listdir(levels_dir) if f.endswith('.json')]
    
    if not level_files:
        print("  (no level files found)")
        return
    
    for file in level_files:
        path = os.path.join(levels_dir, file)
        print(f"  - {file} ({os.path.getsize(path)} bytes)")
        
        # Try to open and validate the file
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            print(f"    ✓ Valid JSON: {data.get('name', 'Unnamed')}")
        except Exception as e:
            print(f"    ✗ Invalid JSON: {e}")

if __name__ == "__main__":
    print("=== Brick Breaker Level Saving Debug Tool ===\n")
    
    # List existing levels first
    list_existing_levels()
    
    # Test saving a level
    print("\nTesting level save functionality:")
    if test_save_level():
        print("\n✓ Level saving test PASSED")
    else:
        print("\n✗ Level saving test FAILED")
    
    # List levels again to confirm the test level was saved
    list_existing_levels()