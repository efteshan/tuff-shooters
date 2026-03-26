# src/camera.py

import pygame
import random
from src.constants import SCREEN_W, SCREEN_H, VIRTUAL_W, VIRTUAL_H


class Camera:
    def __init__(self):
        self.virtual_surface = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def add_shake(self, intensity: float, duration: float):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)

    def update(self, p1_cx, p2_cx, dt):
        if self.shake_duration > 0:
            self.shake_duration -= dt
            # Rapid intense quadratic falloff for a more punchy screen shake
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
        # Simply blit with offset without zooming to preserve pixel-perfect resolution and high performance
        screen.blit(self.virtual_surface, (int(self.offset_x), int(self.offset_y)))
