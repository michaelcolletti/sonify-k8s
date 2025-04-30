import fluidsynth

# --- FluidSynth Setup ---
class MidiPlayer:
    """Handles MIDI playback using FluidSynth."""
    
    def __init__(self, soundfont_path: str):
        """Initialize FluidSynth MIDI player with specified soundfont.
        
        Args:
            soundfont_path: Path to the SoundFont (.sf2) file
        """
        # Check dependencies
        try:
            # Verify fluidsynth functionality
            fluidsynth.Synth
        except (ImportError, AttributeError):
            raise ImportError("FluidSynth Python package is not installed. Install with 'pip install pyfluidsynth'")
        
        # Validate soundfont file
        if not os.path.exists(soundfont_path):
            raise FileNotFoundError(f"SoundFont file not found: {soundfont_path}")
        
        # Initialize synth
        self.fs = fluidsynth.Synth(gain=0.5)
        self._setup_audio_driver()
        self._load_soundfont(soundfont_path)
    
    def _setup_audio_driver(self):
        """Set up the appropriate audio driver based on platform."""
        # Select driver based on OS
        if sys.platform == 'darwin':
            drivers = ["coreaudio"]
        elif sys.platform == 'linux':
            drivers = ["pulseaudio", "alsa", "jack"]
        elif sys.platform == 'win32':
            drivers = ["dsound", "wasapi"]
        else:
            drivers = [None]  # Let FluidSynth choose
        
        # Try each driver until one works
        for driver in drivers:
            try:
                self.fs.start(driver=driver)
                logger.info(f"Started FluidSynth with {driver or 'default'} audio driver")
                return
            except Exception as e:
                logger.warning(f"Failed to start FluidSynth with driver '{driver}': {e}")
        
        raise RuntimeError("Failed to initialize audio. Please ensure FluidSynth is properly installed on your system.")
    
    def _load_soundfont(self, soundfont_path):
        """Load the specified SoundFont file."""
        try:
            self.sfid = self.fs.sfload(soundfont_path)
            # Set default instrument (piano)
            self.fs.program_select(0, self.sfid, 0, 0)
            logger.info(f"Loaded SoundFont: {soundfont_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load SoundFont: {e}")
    
    def __del__(self):
        """Clean up resources when object is destroyed."""
        if hasattr(self, 'fs'):
            self.fs.delete()
