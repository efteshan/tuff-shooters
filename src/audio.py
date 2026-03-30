# src/audio.py — Handles all sound effects and background music.
# Sound files go in assets/sounds/. If a file is missing, it just won't play (no crash).

import pygame

class AudioManager:
    """Loads .wav files by name and plays them on demand."""

    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}       # {"gunshot": <Sound>, "jump": <Sound>, ...}
        self.music_path = None

    def load_sound(self, name, path):
        """Try to load a sound file. If the file doesn't exist, store None so it fails silently."""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except Exception:
            self.sounds[name] = None

    def play_sound(self, name):
        """Play a previously loaded sound by its name."""
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def load_music(self, path):
        """Set the path for background music (loaded later when play_music is called)."""
        self.music_path = path

    def play_music(self, loops=-1):
        """Start background music. loops=-1 means loop forever."""
        if self.music_path:
            try:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.play(loops)
            except Exception:
                pass

    def stop_music(self):
        """Stop whatever music is currently playing."""
        pygame.mixer.music.stop()
