# src/pickups.py

import os
import pygame
import random
from src.constants import (
    GROUND_Y, HEALTH_PACK_VALUE, HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX,
    AMMO_SPAWN_MIN, AMMO_SPAWN_MAX, AMMO_PACK_LIFETIME_MIN, AMMO_PACK_LIFETIME_MAX,
    MEDKIT_LIFETIME_MIN, MEDKIT_LIFETIME_MAX,
    SHOTGUN_PICKUP_LIFETIME, BAZOOKA_PICKUP_LIFETIME,
    MEDKIT_DISPLAY_W, MEDKIT_DISPLAY_H,
    AMMOBOX_DISPLAY_W, AMMOBOX_DISPLAY_H,
    PICKUP_GROUND_Y_OFFSET, PICKUP_GROUND_X_OFFSET,
    PICKUP_PLATFORM_Y_OFFSET, PICKUP_PLATFORM_X_OFFSET
)


def _load_custom_image(path, display_w, display_h):
    """Try to load a custom PNG, scale it, and strip black background.
    Returns the scaled Surface or None if the file doesn't exist."""
    if not os.path.isfile(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        # Scale FIRST — much fewer pixels to iterate for the strip loop
        img = pygame.transform.smoothscale(img, (display_w, display_h))
        # Strip black / near-black pixels (set alpha to 0)
        for px in range(display_w):
            for py in range(display_h):
                r, g, b, a = img.get_at((px, py))
                if r < 15 and g < 15 and b < 15:
                    img.set_at((px, py), (r, g, b, 0))
        tag = os.path.basename(path)
        print(f"[PICKUP] Loaded custom image: {tag} -> {display_w}x{display_h}")
        return img
    except Exception as e:
        print(f"[PICKUP] Failed to load {path}: {e}")
        return None


# ── Cached custom surfaces (loaded once) ───────────────────────
_cached_medkit = None
_cached_ammo   = None
_cache_loaded  = False

def _get_custom_medkit():
    global _cache_loaded
    if not _cache_loaded:
        _load_all_custom_cache()
    return _cached_medkit

def _get_custom_ammo():
    global _cache_loaded
    if not _cache_loaded:
        _load_all_custom_cache()
    return _cached_ammo

def _load_all_custom_cache():
    global _cached_medkit, _cached_ammo, _cache_loaded
    _cache_loaded = True
    _cached_medkit = _load_custom_image(
        "assets/pickups/medkit.png", MEDKIT_DISPLAY_W, MEDKIT_DISPLAY_H)
    _cached_ammo = _load_custom_image(
        "assets/pickups/ammo_box.png", AMMOBOX_DISPLAY_W, AMMOBOX_DISPLAY_H)

def preload_pickup_images():
    """Call at game startup to avoid lag on first pickup spawn."""
    _load_all_custom_cache()


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
        custom = _get_custom_medkit()
        self.image = custom if custom else create_healthpack_art()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.value = HEALTH_PACK_VALUE
        self.lifetime = random.uniform(MEDKIT_LIFETIME_MIN, MEDKIT_LIFETIME_MAX)
    
    def update(self, dt):
        """Update medkit lifetime — disappears if not collected."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface, camera):
        """Draw health pack."""
        surface.blit(self.image, self.rect)


class AmmoPack(pygame.sprite.Sprite):
    """Ammo pickup that refills player ammo."""
    
    def __init__(self, x, y, image):
        super().__init__()
        custom = _get_custom_ammo()
        self.image = custom if custom else create_ammobox_art()
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


class BazookaPickup(pygame.sprite.Sprite):
    """
    A Bazooka that spawned from a destroyed box.
    """

    def __init__(self, x, y):
        super().__init__()
        from src.constants import BAZOOKA_PICKUP_LIFETIME
        self.lifetime = BAZOOKA_PICKUP_LIFETIME
        self.glow_timer = 0.0
        self.image = self._make_bazooka_art()
        self.rect  = self.image.get_rect(
            bottomleft=(x, y))

    def _make_bazooka_art(self):
        """Simple side-view bazooka silhouette."""
        s = pygame.Surface((50, 16), pygame.SRCALPHA)
        body = (60, 80, 60)
        metal = (50, 50, 50)
        dark = (30, 40, 30)
        
        # Main tube
        pygame.draw.rect(s, body, (0, 3, 50, 10), border_radius=2)
        pygame.draw.rect(s, dark, (0, 3, 50, 10), 1, border_radius=2)
        
        # Exhaust bell (back)
        pygame.draw.polygon(s, metal, [(0, 3), (6, 3), (6, 13), (0, 13), (-4, 8)])
        # Front bell
        pygame.draw.rect(s, metal, (46, 2, 4, 12))
        
        # Sights
        pygame.draw.rect(s, dark, (15, 0, 4, 3))
        pygame.draw.rect(s, dark, (35, 0, 4, 3))
        
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
            glow.fill((0, 255, 140, alpha))
            surface.blit(glow,
                (self.rect.x - 6, self.rect.y - 6))
        
        surface.blit(self.image, self.rect)
        surface.blit(self.image, self.rect)


class PickupSpawnManager:
    """Manages timed spawning of health and ammo pickups."""
    
    def __init__(self, arena_platforms):
        from src.constants import (
            GROUND_LEFT, GROUND_RIGHT, BARREL_X, BARREL_WIDTH,
            BOX_X, BOX_WIDTH, MEDKIT_DISPLAY_W, MEDKIT_DISPLAY_H,
            AMMOBOX_DISPLAY_W, AMMOBOX_DISPLAY_H
        )
        
        self.platforms = arena_platforms
        
        # Build obstacle exclusion zones (x_start, x_end) with 30px padding
        pad = 30
        self.obstacles = [
            (BARREL_X - pad, BARREL_X + BARREL_WIDTH + pad),
            (BOX_X - pad, BOX_X + BOX_WIDTH + pad),
        ]
        
        # Ground spawn range
        self.ground_left = GROUND_LEFT + 20  # small inset from cliff edge
        self.ground_right = GROUND_RIGHT - 20
        
        # Pickup display sizes for overlap checking
        self.medkit_w = MEDKIT_DISPLAY_W
        self.medkit_h = MEDKIT_DISPLAY_H
        self.ammo_w = AMMOBOX_DISPLAY_W
        self.ammo_h = AMMOBOX_DISPLAY_H
        
        self.health_timer = random.uniform(HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX)
        self.ammo_timer = random.uniform(AMMO_SPAWN_MIN, AMMO_SPAWN_MAX)
    
    def _overlaps_obstacle(self, x):
        """Return True if x is inside an obstacle exclusion zone."""
        for left, right in self.obstacles:
            if left <= x <= right:
                return True
        return False
    
    def _overlaps_existing(self, x, y, w, h, health_group, ammo_group):
        """Return True if the proposed rect overlaps any existing pickup."""
        new_rect = pygame.Rect(x, y, w, h)
        for pack in health_group:
            if new_rect.colliderect(pack.rect):
                return True
        for pack in ammo_group:
            if new_rect.colliderect(pack.rect):
                return True
        return False
    
    def _pick_ground_spot(self, pw, ph, health_group, ammo_group):
        """Pick a random ground spawn position that doesn't overlap anything.
        Returns (x, y) or None if no valid spot found after attempts."""
        y = GROUND_Y - ph + PICKUP_GROUND_Y_OFFSET
        for _ in range(15):
            x = random.randint(self.ground_left, self.ground_right - pw) + PICKUP_GROUND_X_OFFSET
            if self._overlaps_obstacle(x) or self._overlaps_obstacle(x + pw):
                continue
            if self._overlaps_existing(x, y, pw, ph, health_group, ammo_group):
                continue
            return (x, y)
        return None
    
    def _pick_platform_spot(self, pw, ph, health_group, ammo_group):
        """Pick a random platform spawn position.
        Returns (x, y) or None if no valid spot found."""
        if not self.platforms:
            return None
        plats = list(self.platforms)
        random.shuffle(plats)
        for plat in plats:
            pr = plat.rect
            # Place pickup centered on platform, slightly above
            max_left = pr.left + 5
            max_right = pr.right - pw - 5
            if max_right <= max_left:
                # Platform too narrow
                x = pr.centerx - pw // 2 + PICKUP_PLATFORM_X_OFFSET
            else:
                x = random.randint(max_left, max_right) + PICKUP_PLATFORM_X_OFFSET
            y = pr.top - ph + PICKUP_PLATFORM_Y_OFFSET
            if not self._overlaps_existing(x, y, pw, ph, health_group, ammo_group):
                return (x, y)
        return None
    
    def _pick_spawn(self, pw, ph, health_group, ammo_group):
        """Pick either ground or platform spawn (50/50 chance)."""
        if random.random() < 0.5:
            # Try platform first, fallback to ground
            spot = self._pick_platform_spot(pw, ph, health_group, ammo_group)
            if spot:
                return spot
            return self._pick_ground_spot(pw, ph, health_group, ammo_group)
        else:
            # Try ground first, fallback to platform
            spot = self._pick_ground_spot(pw, ph, health_group, ammo_group)
            if spot:
                return spot
            return self._pick_platform_spot(pw, ph, health_group, ammo_group)
    
    def update(self, dt, health_group, ammo_group, images):
        """Update spawn timers and create new pickups."""
        self.health_timer -= dt
        self.ammo_timer -= dt
        
        # Spawn health pack (max 1 on screen)
        if self.health_timer <= 0:
            self.health_timer = random.uniform(HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX)
            if len(health_group) < 1:
                spot = self._pick_spawn(
                    self.medkit_w, self.medkit_h, health_group, ammo_group)
                if spot:
                    health_group.add(HealthPack(spot[0], spot[1], images["health_pack"]))
        
        # Spawn ammo pack (max 2 on screen)
        if self.ammo_timer <= 0:
            self.ammo_timer = random.uniform(AMMO_SPAWN_MIN, AMMO_SPAWN_MAX)
            if len(ammo_group) < 2:
                spot = self._pick_spawn(
                    self.ammo_w, self.ammo_h, health_group, ammo_group)
                if spot:
                    ammo_group.add(AmmoPack(spot[0], spot[1], images["ammo_box"]))
