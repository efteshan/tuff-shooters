# src/camera.py

import pygame
from src.constants import SCREEN_W, SCREEN_H, VIRTUAL_W, VIRTUAL_H


class Camera:
    def __init__(self):
        self.virtual_surface = pygame.Surface((VIRTUAL_W, VIRTUAL_H))

    def update(self, p1_cx, p2_cx, dt):
        pass

    def render(self, screen):
        screen.blit(self.virtual_surface, (0, 0))
