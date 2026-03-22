# src/bullet.py

import pygame
from src.constants import BULLET_SPEED, BULLET_DAMAGE, VIRTUAL_W


class Bullet(pygame.sprite.Sprite):
    """Bullet projectile fired by players."""
    
    def __init__(self, x, y, direction, owner_id):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.vel_x = BULLET_SPEED * direction  # direction: 1 or -1
        self.vel_y = 0.0  # strictly horizontal, no arc
        self.owner_id = owner_id  # 1 or 2 — prevents self-damage
        self.damage = BULLET_DAMAGE
        self.alive = True
        
        # Visual: 10px wide, 4px tall rectangle in yellow/white
        self.image = pygame.Surface((10, 4), pygame.SRCALPHA)
        self.image.fill((255, 230, 80))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self, dt):
        """Update bullet position."""
        self.x += self.vel_x * dt
        self.rect.centerx = int(self.x)
        
        # Destroy if outside virtual canvas
        if self.x < -50 or self.x > VIRTUAL_W + 50:
            self.kill()
            self.alive = False
    
    def draw(self, surface, camera):
        """Draw bullet."""
        # Update rect position for collision detection
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        # Draw bullet at world position
        adjusted_rect = self.rect.copy()
        adjusted_rect.x = self.x - self.rect.width // 2
        adjusted_rect.y = self.y - self.rect.height // 2
        surface.blit(self.image, adjusted_rect)


class ShotgunPellet(pygame.sprite.Sprite):
    """
    A single pellet from a shotgun blast.
    Travels at an angle, slows slightly, dies at max range.
    Damage is 0 if target is closer than SHOTGUN_MIN_RANGE.
    """

    def __init__(self, x, y, direction, angle_deg, owner_id):
        """
        direction: 1 (right) or -1 (left) — flips the spread
        angle_deg: offset angle from horizontal, e.g. -25 to +25
        """
        super().__init__()
        import math
        from src.constants import (
            SHOTGUN_PELLET_SPEED, SHOTGUN_PELLET_DAMAGE,
            SHOTGUN_MAX_RANGE, SHOTGUN_MIN_RANGE, VIRTUAL_W
        )
        self.x = float(x)
        self.y = float(y)
        self.owner_id = owner_id
        self.damage = SHOTGUN_PELLET_DAMAGE
        self.max_range = SHOTGUN_MAX_RANGE
        self.min_range = SHOTGUN_MIN_RANGE
        self.distance_traveled = 0.0
        self.alive = True
        self.VIRTUAL_W = VIRTUAL_W

        # Apply direction flip to angle
        actual_angle = angle_deg if direction == 1 else (180 - angle_deg)
        rad = math.radians(actual_angle)
        self.vel_x = math.cos(rad) * SHOTGUN_PELLET_SPEED
        self.vel_y = math.sin(rad) * SHOTGUN_PELLET_SPEED
        self.spawn_x = x
        self.spawn_y = y

        # Visual: small 6x3 orange pellet
        self.image = pygame.Surface((6, 3), pygame.SRCALPHA)
        self.image.fill((255, 160, 50))
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def get_effective_damage(self, target_x):
        """Return actual damage based on distance. 0 if too close."""
        dist = abs(self.x - self.spawn_x)
        if dist < self.min_range:
            return 0
        return self.damage

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.distance_traveled = (
            (self.x - self.spawn_x) ** 2 +
            (self.y - self.spawn_y) ** 2
        ) ** 0.5
        self.rect.center = (int(self.x), int(self.y))

        # Die at max range or off screen
        if (self.distance_traveled >= self.max_range or
                self.x < -50 or self.x > self.VIRTUAL_W + 50):
            self.kill()
            self.alive = False

    def draw(self, surface, camera):
        surface.blit(self.image, self.rect)

    def kill(self):
        """Override kill to always set alive=False."""
        self.alive = False
        super().kill()

