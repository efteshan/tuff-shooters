# src/audio.py — Handles all sound effects and background music.
# Sound files go in assets/sounds/. If a file is missing, it just won't play (no crash).

import pygame

class AudioManager:
    """Loads .wav files by name and plays them on demand.
    Music and SFX volumes are controlled independently."""

    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}       # {"gunshot": <Sound>, "jump": <Sound>, ...}
        self.music_path = None
        self.sfx_volume = 1.0  # Independent volume for all sound effects (0.0 – 1.0)

    def load_sound(self, name, path):
        """Try to load a sound file. If the file doesn't exist, store None so it fails silently."""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except Exception:
            self.sounds[name] = None

    def play_sound(self, name):
        """Play a previously loaded sound by its name, scaled by sfx_volume."""
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].set_volume(self.sfx_volume)
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

    # Raw music is significantly louder than SFX in pygame.
    # This multiplier scales the user's 0.0-1.0 range down so sound effects
    # remain audible. A value of 0.3 means user "100%" = 30% raw volume.
    _MUSIC_VOLUME_MULTIPLIER = 0.3

    def set_music_volume(self, volume):
        """Set music volume. volume is a float from 0.0 (mute) to 1.0 (full).
        Internally scaled by _MUSIC_VOLUME_MULTIPLIER so SFX stay punchy."""
        self._music_volume_logical = max(0.0, min(1.0, volume))
        raw = self._music_volume_logical * self._MUSIC_VOLUME_MULTIPLIER
        pygame.mixer.music.set_volume(raw)

    def get_music_volume(self):
        """Return the logical music volume (0.0 – 1.0) as set by the user."""
        return getattr(self, '_music_volume_logical', pygame.mixer.music.get_volume())

    def set_sfx_volume(self, volume):
        """Set SFX volume. volume is a float from 0.0 (mute) to 1.0 (full).
        Affects all sounds: weapons, pickups, jumps, UI clicks, etc."""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def get_sfx_volume(self):
        """Return the current SFX volume (0.0 – 1.0)."""
        return self.sfx_volume

    def stop_music(self):
        """Stop whatever music is currently playing."""
        pygame.mixer.music.stop()
