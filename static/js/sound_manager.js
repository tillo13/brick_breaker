/**
 * Sound Manager for Brick Breaker
 * Provides easy access to play game sounds with proper caching
 */
class SoundManager {
    constructor() {
        // Sound cache
        this.sounds = {};
        
        // Default volume
        this.volume = 0.5;
        
        // Whether sound is enabled
        this.enabled = true;
        
        // Preload common sounds
        this.preloadSounds();
    }
    
    preloadSounds() {
        // Define sounds to preload
        const soundFiles = {
            'bounce': 'bounce.mp3',
            'brick': 'brick.mp3',
            'powerup': 'powerup.mp3',
            'laser': 'laser.mp3',
            'gameover': 'gameover.mp3',
            'levelup': 'levelup.mp3'
        };
        
        // Load each sound
        for (const [name, file] of Object.entries(soundFiles)) {
            this.loadSound(name, file);
        }
    }
    
    loadSound(name, file) {
        // Create audio element
        const audio = new Audio(`/static/sounds/${file}`);
        audio.volume = this.volume;
        
        // Store in cache
        this.sounds[name] = audio;
    }
    
    play(name) {
        // Skip if sound is disabled
        if (!this.enabled) return;
        
        // Get sound from cache
        const sound = this.sounds[name];
        if (!sound) return;
        
        // Clone the audio to allow overlapping sounds
        const soundInstance = sound.cloneNode();
        soundInstance.volume = this.volume;
        soundInstance.play().catch(e => {
            // Ignore errors - common due to user interaction requirements
        });
    }
    
    setVolume(volume) {
        // Set volume (0-1)
        this.volume = Math.max(0, Math.min(1, volume));
        
        // Update all cached sounds
        for (const sound of Object.values(this.sounds)) {
            sound.volume = this.volume;
        }
    }
    
    toggle() {
        // Toggle sound on/off
        this.enabled = !this.enabled;
        return this.enabled;
    }
}