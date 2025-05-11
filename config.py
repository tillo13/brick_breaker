class Config:
    """Base configuration"""
    DEBUG = False
    SECRET_KEY = 'your-secret-key-here'
    GAME_SETTINGS = {
        'SCREEN_WIDTH': 800,
        'SCREEN_HEIGHT': 600,
        'FPS': 60
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False