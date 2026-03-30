# src/physics.py — Base physics for anything that moves (players, ragdoll parts, etc.)

import pygame
from src.constants import GRAVITY, MAX_FALL_SPEED, GROUND_Y, GROUND_FRICTION, VIRTUAL_W, GROUND_LEFT, GROUND_RIGHT, PLAYER_GROUND_Y_OFFSET


class PhysicsObject:
    """Base class for anything that needs gravity, velocity, and ground collision."""
    
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        
        # Track how high this object was before falling, used for fall damage calculation
        self._highest_y = float(y)
        self._was_on_ground = True
        self._fall_damage_pending = 0
    
    def apply_physics(self, dt):
        """Run one frame of physics: gravity, movement, ground collision."""
        # Pull downward unless standing on something
        if not self.on_ground:
            self.vel_y += GRAVITY * dt
            self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        # Move by current velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Reset on_ground each frame — platform/barrel collision handlers will set it back
        # to True if the player is actually standing on something
        self.on_ground = False
        
        # Only collide with ground if the player's center is within the walkable area
        center_x = self.x + self.width / 2
        on_walkable = (center_x >= GROUND_LEFT and center_x <= GROUND_RIGHT)
        if on_walkable and self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height + PLAYER_GROUND_Y_OFFSET
            self.vel_y = 0
            self.on_ground = True
        
        # Remember the highest point reached during a jump/fall for fall damage
        if not self.on_ground:
            if self.y < self._highest_y:
                self._highest_y = self.y
        
        # Players can walk off cliff edges but can't leave the screen entirely
        self.x = max(-self.width, min(self.x, VIRTUAL_W))
    
    def apply_friction(self, moving=False):
        """Slow down horizontal speed when on ground and not pressing any movement keys."""
        if self.on_ground and self.vel_x != 0 and not moving:
            self.vel_x *= GROUND_FRICTION
            if abs(self.vel_x) < 5:
                self.vel_x = 0
    
    def get_rect(self) -> pygame.Rect:
        """Collision rectangle for this object."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
