# src/pickups.py

import pygame
import random
from src.constants import (
    GROUND_Y, HEALTH_PACK_VALUE, HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX,
    AMMO_SPAWN_MIN, AMMO_SPAWN_MAX, AMMO_PACK_LIFETIME_MIN, AMMO_PACK_LIFETIME_MAX
)


def create_healthpack_art():
    """Pixel art medkit — white box with red cross."""
    s = pygame.Surface((28, 26), pygame.SRCALPHA)
    # White box body
    pygame.draw.rect(s, (220, 220, 220), (0, 0, 28, 26), border_radius=3)
    # Dark outline
    pygame.draw.rect(s, (140, 140, 140), (0, 0, 28, 26), 2, border_radius=3)
    # Red cross — vertical bar
    pygame.draw.rect(s, (210, 30, 30), (11, 4, 6, 18))
    # Red cross — horizontal bar
    pygame.draw.rect(s, (210, 30, 30), (4, 10, 20, 6))
    # Cross highlight
    pygame.draw.rect(s, (240, 80, 80), (12, 5, 3, 4))
    # Bottom shadow
    pygame.draw.rect(s, (160, 160, 160), (2, 22, 24, 3), border_radius=2)
    # Handle on top
    pygame.draw.rect(s, (160, 160, 160), (9, -2, 10, 4), border_radius=2)
    pygame.draw.rect(s, (120, 120, 120), (9, -2, 10, 4), 1, border_radius=2)
    return s

def create_ammobox_art():
    """Pixel art ammo box — olive green military crate."""
    s = pygame.Surface((28, 22), pygame.SRCALPHA)
    # Main body — olive green
    pygame.draw.rect(s, (90, 110, 50), (0, 2, 28, 20), border_radius=2)
    # Darker outline
    pygame.draw.rect(s, (55, 70, 25), (0, 2, 28, 20), 2, border_radius=2)
    # Lid — slightly lighter
    pygame.draw.rect(s, (110, 130, 65), (0, 2, 28, 6), border_radius=2)
    # Lid line
    pygame.draw.line(s, (55, 70, 25), (0, 7), (28, 7), 1)
    # Bullet icon — 3 small yellow rectangles
    for i in range(3):
        bx = 5 + i * 8
        pygame.draw.rect(s, (210, 190, 60), (bx, 10, 4, 9),
                         border_radius=1)
        pygame.draw.rect(s, (180, 150, 30), (bx, 10, 4, 3),
                         border_radius=1)
    # Metal latch in center of lid
    pygame.draw.rect(s, (160, 150, 100), (11, 4, 6, 3), border_radius=1)
    # Shadow on bottom
    pygame.draw.rect(s, (55, 70, 25), (2, 19, 24, 3), border_radius=1)
    return s


class HealthPack(pygame.sprite.Sprite):
    """Health pickup that restores player health."""
    
    def __init__(self, x, y, image):
        super().__init__()
        self.image = create_healthpack_art()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.value = HEALTH_PACK_VALUE
    
    def draw(self, surface, camera):
        """Draw health pack."""
        surface.blit(self.image, self.rect)


class AmmoPack(pygame.sprite.Sprite):
    """Ammo pickup that refills player ammo."""
    
    def __init__(self, x, y, image):
        super().__init__()
        self.image = create_ammobox_art()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.lifetime = random.uniform(AMMO_PACK_LIFETIME_MIN, AMMO_PACK_LIFETIME_MAX)
    
    def update(self, dt):
        """Update ammo pack lifetime."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface, camera):
        """Draw ammo pack."""
        surface.blit(self.image, self.rect)


class ShotgunPickup(pygame.sprite.Sprite):
    """
    A shotgun that spawned from a destroyed box.
    Sits on the ground glowing. Player walks over it to pick up.
    Expires after SHOTGUN_PICKUP_LIFETIME seconds if not collected.
    """

    def __init__(self, x, y):
        super().__init__()
        from src.constants import SHOTGUN_PICKUP_LIFETIME
        self.lifetime = SHOTGUN_PICKUP_LIFETIME
        self.glow_timer = 0.0
        self.image = self._make_shotgun_art()
        self.rect  = self.image.get_rect(
            bottomleft=(x, y))  # y = GROUND_Y

    def _make_shotgun_art(self):
        """Simple side-view shotgun silhouette — 44x16px."""
        s = pygame.Surface((44, 16), pygame.SRCALPHA)
        body   = (130,  80, 30)
        metal  = ( 80,  80, 90)
        dark   = ( 40,  25, 10)
        # Stock (rear wooden part)
        pygame.draw.rect(s, body,  ( 0,  4, 18, 10), border_radius=2)
        pygame.draw.rect(s, dark,  ( 0,  4, 18, 10), 1, border_radius=2)
        # Receiver body
        pygame.draw.rect(s, body,  (14,  3, 18, 11), border_radius=2)
        pygame.draw.rect(s, dark,  (14,  3, 18, 11), 1, border_radius=2)
        # Barrel (metal tube)
        pygame.draw.rect(s, metal, (28,  5, 16,  5), border_radius=1)
        pygame.draw.rect(s, dark,  (28,  5, 16,  5), 1, border_radius=1)
        # Trigger guard
        pygame.draw.arc(s, dark,
            pygame.Rect(16, 7, 8, 7), 3.14, 0, 1)
        # Highlight line on barrel
        pygame.draw.line(s, (140, 140, 155), (30, 6), (42, 6), 1)
        return s

    def update(self, dt):
        self.lifetime -= dt
        self.glow_timer += dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, surface, camera):
        import math
        # Pulsing glow behind gun when lifetime < 4s
        if self.lifetime < 4.0:
            alpha = int(abs(math.sin(self.glow_timer * 6)) * 160)
            glow = pygame.Surface(
                (self.rect.width + 12, self.rect.height + 12),
                pygame.SRCALPHA)
            glow.fill((255, 140, 0, alpha))
            surface.blit(glow,
                (self.rect.x - 6, self.rect.y - 6))
        surface.blit(self.image, self.rect)


class PickupSpawnManager:
    """Manages timed spawning of health and ammo pickups."""
    
    def __init__(self, arena_platforms):
        # Valid spawn X positions — between barrels, no overlap
        self.spawn_points_ground = [80, 200, 470, 560, 750, 840, 1050, 1180]
        self.spawn_points_platform = [192, 448, 640, 864, 1024]
        
        self.health_timer = random.uniform(HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX)
        self.ammo_timer = random.uniform(AMMO_SPAWN_MIN, AMMO_SPAWN_MAX)
    
    def _too_close_to_barrel(self, spawn_x):
        """Return True if spawn_x is within 40px of any barrel edge."""
        barrel_xs = [460, 760]  # barrel + box positions
        barrel_w  = 58
        for bx in barrel_xs:
            if bx - 40 <= spawn_x <= bx + barrel_w + 40:
                return True
        return False
    
    def update(self, dt, health_group, ammo_group, images):
        """Update spawn timers and create new pickups."""
        self.health_timer -= dt
        self.ammo_timer -= dt
        
        # Spawn health pack (max 1 on screen)
        if self.health_timer <= 0:
            self.health_timer = random.uniform(HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX)
            if len(health_group) < 1:
                x = random.choice(self.spawn_points_ground + self.spawn_points_platform)
                if not self._too_close_to_barrel(x):
                    y = GROUND_Y - 40
                    health_group.add(HealthPack(x, y, images["health_pack"]))
        
        # Spawn ammo pack (max 2 on screen)
        if self.ammo_timer <= 0:
            self.ammo_timer = random.uniform(AMMO_SPAWN_MIN, AMMO_SPAWN_MAX)
            if len(ammo_group) < 2:
                x = random.choice(self.spawn_points_ground + self.spawn_points_platform)
                if not self._too_close_to_barrel(x):
                    y = GROUND_Y - 40
                    ammo_group.add(AmmoPack(x, y, images["ammo_box"]))

