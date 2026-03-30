# src/camera.py — Manages the game camera with screen shake support.
# The game renders to a virtual surface first, then this class blits it to the real screen.

import pygame
import random
from src.constants import SCREEN_W, SCREEN_H, VIRTUAL_W, VIRTUAL_H


class Camera:
    def __init__(self):
        # Everything draws to this surface first, then gets copied to the real screen
        self.virtual_surface = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def add_shake(self, intensity: float, duration: float):
        """Trigger a screen shake. If one is already active, keep the stronger one."""
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)

    def update(self, p1_cx, p2_cx, dt):
        """Update screen shake each frame — intensity fades out quickly for a punchy feel."""
        if self.shake_duration > 0:
            self.shake_duration -= dt
            # Shake strength decays fast so it feels like a sharp impact, not a wobble
            factor = self.shake_duration * 5.0
            current_shake = min(self.shake_intensity, self.shake_intensity * factor)
            
            self.offset_x = random.uniform(-current_shake, current_shake)
            self.offset_y = random.uniform(-current_shake, current_shake)
            
            if self.shake_duration <= 0:
                self.shake_intensity = 0.0
                self.offset_x = 0
                self.offset_y = 0
        else:
            self.shake_intensity = 0.0
            self.offset_x = 0
            self.offset_y = 0

    def render(self, screen):
        """Copy the virtual surface to the real screen, offset by shake amount."""
        screen.blit(self.virtual_surface, (int(self.offset_x), int(self.offset_y)))
