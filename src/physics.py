# src/physics.py

import pygame
from src.constants import GRAVITY, MAX_FALL_SPEED, GROUND_Y, GROUND_FRICTION, VIRTUAL_W, GROUND_LEFT, GROUND_RIGHT


class PhysicsObject:
    """Base class for all objects that need physics simulation."""
    
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
    
    def apply_physics(self, dt):
        """Apply gravity and velocity to position."""
        # Apply gravity if not on ground
        if not self.on_ground:
            self.vel_y += GRAVITY * dt
            self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        # Apply velocity to position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Ground collision — only if player center is on walkable ground
        center_x = self.x + self.width / 2
        on_walkable = (center_x >= GROUND_LEFT and center_x <= GROUND_RIGHT)
        if on_walkable and self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Allow players to walk off cliff edges but not leave screen entirely
        self.x = max(-self.width, min(self.x, VIRTUAL_W))
    
    def apply_friction(self, moving=False):
        """Apply friction when on ground and not actively moving."""
        if self.on_ground and self.vel_x != 0 and not moving:
            self.vel_x *= GROUND_FRICTION
            if abs(self.vel_x) < 5:
                self.vel_x = 0
    
    def get_rect(self) -> pygame.Rect:
        """Return pygame Rect for collision detection."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
