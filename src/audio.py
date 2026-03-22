# src/audio.py

import pygame

class AudioManager:
    """A manager for loading and playing sounds and music."""

    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_path = None

    def load_sound(self, name, path):
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except Exception:
            self.sounds[name] = None

    def play_sound(self, name):
        """Play a sound effect."""
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def load_music(self, path):
        """Load background music."""
        self.music_path = path

    def play_music(self, loops=-1):
        """Play background music."""
        if self.music_path:
            try:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.play(loops)
            except Exception:
                pass

    def stop_music(self):
        """Stop the music."""
        pygame.mixer.music.stop()
