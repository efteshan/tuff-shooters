# src/pickups.py — Everything players can pick up: health packs, ammo boxes, shotguns, bazookas.
# Also includes the spawn manager that decides when and where pickups appear.

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
    """Load a custom PNG from disk, scale it to the display size, and make black pixels transparent.
    Returns the processed Surface, or None if the file doesn't exist."""
    if not os.path.isfile(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (display_w, display_h))
        # Turn near-black pixels fully transparent (strips dark backgrounds from imported art)
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


# Cache custom pickup images so we only load from disk once
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
    """Call at game startup so the first pickup spawn doesn't cause a frame hitch."""
    _load_all_custom_cache()


def create_healthpack_art():
    """Draw a white medkit box with a red cross — used when no custom medkit.png exists."""
    s = pygame.Surface((28, 26), pygame.SRCALPHA)
    pygame.draw.rect(s, (220, 220, 220), (0, 0, 28, 26), border_radius=3)
    pygame.draw.rect(s, (140, 140, 140), (0, 0, 28, 26), 2, border_radius=3)
    pygame.draw.rect(s, (210, 30, 30), (11, 4, 6, 18))     # Vertical bar of cross
    pygame.draw.rect(s, (210, 30, 30), (4, 10, 20, 6))      # Horizontal bar of cross
    pygame.draw.rect(s, (240, 80, 80), (12, 5, 3, 4))       # Highlight on cross
    pygame.draw.rect(s, (160, 160, 160), (2, 22, 24, 3), border_radius=2)   # Bottom shadow
    pygame.draw.rect(s, (160, 160, 160), (9, -2, 10, 4), border_radius=2)   # Handle on top
    pygame.draw.rect(s, (120, 120, 120), (9, -2, 10, 4), 1, border_radius=2)
    return s

def create_ammobox_art():
    """Draw an olive green military ammo crate — used when no custom ammo_box.png exists."""
    s = pygame.Surface((28, 22), pygame.SRCALPHA)
    pygame.draw.rect(s, (90, 110, 50), (0, 2, 28, 20), border_radius=2)     # Main body
    pygame.draw.rect(s, (55, 70, 25), (0, 2, 28, 20), 2, border_radius=2)   # Outline
    pygame.draw.rect(s, (110, 130, 65), (0, 2, 28, 6), border_radius=2)     # Lid (lighter)
    pygame.draw.line(s, (55, 70, 25), (0, 7), (28, 7), 1)                   # Lid seam line
    # Three small bullet icons on the front
    for i in range(3):
        bx = 5 + i * 8
        pygame.draw.rect(s, (210, 190, 60), (bx, 10, 4, 9), border_radius=1)
        pygame.draw.rect(s, (180, 150, 30), (bx, 10, 4, 3), border_radius=1)
    pygame.draw.rect(s, (160, 150, 100), (11, 4, 6, 3), border_radius=1)    # Metal latch
    pygame.draw.rect(s, (55, 70, 25), (2, 19, 24, 3), border_radius=1)      # Bottom shadow
    return s


class HealthPack(pygame.sprite.Sprite):
    """Restores player HP when walked over. Despawns after a random time if not collected."""
    
    def __init__(self, x, y, image):
        super().__init__()
        custom = _get_custom_medkit()
        self.image = custom if custom else create_healthpack_art()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.value = HEALTH_PACK_VALUE
        self.lifetime = random.uniform(MEDKIT_LIFETIME_MIN, MEDKIT_LIFETIME_MAX)
    
    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface, camera):
        surface.blit(self.image, self.rect)


class AmmoPack(pygame.sprite.Sprite):
    """Refills player ammo when walked over. Despawns after a few seconds."""
    
    def __init__(self, x, y, image):
        super().__init__()
        custom = _get_custom_ammo()
        self.image = custom if custom else create_ammobox_art()
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.lifetime = random.uniform(AMMO_PACK_LIFETIME_MIN, AMMO_PACK_LIFETIME_MAX)
    
    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface, camera):
        surface.blit(self.image, self.rect)


class ShotgunPickup(pygame.sprite.Sprite):
    """Shotgun dropped from a destroyed box. Sits on the ground with a pulsing glow.
    Walk over it to pick up. Disappears after SHOTGUN_PICKUP_LIFETIME seconds."""

    def __init__(self, x, y):
        super().__init__()
        from src.constants import SHOTGUN_PICKUP_LIFETIME
        self.lifetime = SHOTGUN_PICKUP_LIFETIME
        self.glow_timer = 0.0
        self.image = self._make_shotgun_art()
        self.rect  = self.image.get_rect(bottomleft=(x, y))

    def _make_shotgun_art(self):
        """Draw shotgun at 2x scale then downscale for smooth pixel art look."""
        S = 2
        s = pygame.Surface((36*S, 18*S), pygame.SRCALPHA)
        import math
        # Ground shadow ellipse
        pygame.draw.ellipse(s, (0, 0, 0, 100), (0, 12*S, 36*S, 6*S))
        # Wooden stock
        pygame.draw.rect(s, (110,  60, 20),  ( 0,  6*S, 12*S, 4*S), border_radius=S)
        pygame.draw.rect(s, (140,  80, 30),  ( 1*S, 7*S, 10*S, 2*S), border_radius=S)
        # Metal receiver
        pygame.draw.rect(s, (50, 50, 50),  (10*S, 5*S, 10*S, 5*S), border_radius=S)
        pygame.draw.rect(s, (80, 80, 80),  (11*S, 6*S, 8*S, 2*S), border_radius=S)
        # Barrel and magazine tube
        pygame.draw.rect(s, (40, 40, 40), (20*S, 5*S, 16*S, 2*S))
        pygame.draw.rect(s, (30, 30, 30), (20*S, 8*S, 12*S, 2*S))
        pygame.draw.line(s, (100, 100, 100), (21*S, 5*S), (35*S, 5*S), 1)
        # Pump foregrip with grip lines
        pygame.draw.rect(s, (90, 50, 15), (22*S, 7*S, 6*S, 4*S), border_radius=1)
        for px in range(23, 28, 2):
            pygame.draw.line(s, (50, 25, 5), (px*S, 7*S), (px*S, 10*S), 1)
        # Downscale to final size for crisp edges
        return pygame.transform.smoothscale(s, (36, 18))

    def update(self, dt):
        self.lifetime -= dt
        self.glow_timer += dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, surface, camera):
        import math
        # Glow effect when about to despawn (last 4 seconds)
        if self.lifetime < 4.0:
            alpha = int(abs(math.sin(self.glow_timer * 6)) * 160)
            glow = pygame.Surface(
                (self.rect.width + 12, self.rect.height + 12),
                pygame.SRCALPHA)
            glow.fill((255, 140, 0, alpha))
            surface.blit(glow, (self.rect.x - 6, self.rect.y - 6))
        surface.blit(self.image, self.rect)


class BazookaPickup(pygame.sprite.Sprite):
    """Bazooka dropped from a destroyed box. Same pickup behavior as shotgun but with green glow."""

    def __init__(self, x, y):
        super().__init__()
        from src.constants import BAZOOKA_PICKUP_LIFETIME
        self.lifetime = BAZOOKA_PICKUP_LIFETIME
        self.glow_timer = 0.0
        self.image = self._make_bazooka_art()
        self.rect  = self.image.get_rect(bottomleft=(x, y))

    def _make_bazooka_art(self):
        """Draw bazooka at 2x scale then downscale for smooth pixel art look."""
        S = 2
        s = pygame.Surface((44*S, 20*S), pygame.SRCALPHA)
        import math
        # Ground shadow
        pygame.draw.ellipse(s, (0, 0, 0, 100), (0, 14*S, 44*S, 6*S))
        # Main tube body with top highlight and bottom shadow
        pygame.draw.rect(s, (50,  65,  50), (4*S, 6*S, 36*S, 8*S), border_radius=S)
        pygame.draw.rect(s, (70,  90,  70), (4*S, 6*S, 36*S, 3*S), border_radius=S)
        pygame.draw.rect(s, (30,  40,  30), (4*S, 11*S, 36*S, 3*S), border_radius=S)
        # Red warhead cone at front
        pygame.draw.polygon(s, (150, 40, 40), [(40*S, 6*S), (44*S, 10*S), (40*S, 14*S)])
        # Exhaust bell at back
        pygame.draw.polygon(s, (40, 40, 40), [(0, 4*S), (5*S, 6*S), (5*S, 14*S), (0, 16*S)])
        # Front band
        pygame.draw.rect(s, (40, 40, 40), (36*S, 4*S, 4*S, 12*S), border_radius=1)
        # Optical scope on top
        pygame.draw.rect(s, (30, 30, 30), (16*S, 2*S, 12*S, 4*S), border_radius=1)
        pygame.draw.rect(s, (20, 20, 20), (18*S, 0*S,  8*S, 2*S), border_radius=1)
        # Front and rear grip handles underneath
        pygame.draw.rect(s, (30, 30, 30), (12*S, 14*S, 4*S, 4*S), border_radius=1)
        pygame.draw.rect(s, (30, 30, 30), (28*S, 14*S, 4*S, 4*S), border_radius=1)
        return pygame.transform.smoothscale(s, (44, 20))

    def update(self, dt):
        self.lifetime -= dt
        self.glow_timer += dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, surface, camera):
        import math
        # Green pulsing glow when about to despawn
        if self.lifetime < 4.0:
            alpha = int(abs(math.sin(self.glow_timer * 6)) * 160)
            glow = pygame.Surface(
                (self.rect.width + 12, self.rect.height + 12),
                pygame.SRCALPHA)
            glow.fill((0, 255, 140, alpha))
            surface.blit(glow, (self.rect.x - 6, self.rect.y - 6))
        surface.blit(self.image, self.rect)


class PickupSpawnManager:
    """Controls when and where health packs and ammo boxes spawn on the map.
    Uses timers to periodically place pickups on valid ground or platform spots,
    avoiding obstacles and existing pickups."""
    
    def __init__(self, arena_platforms):
        from src.constants import (
            GROUND_LEFT, GROUND_RIGHT, BARREL_X, BARREL_WIDTH,
            BOX_X, BOX_WIDTH, MEDKIT_DISPLAY_W, MEDKIT_DISPLAY_H,
            AMMOBOX_DISPLAY_W, AMMOBOX_DISPLAY_H
        )
        
        self.platforms = arena_platforms
        
        # Don't spawn pickups too close to the barrel or box (30px padding around each)
        pad = 30
        self.obstacles = [
            (BARREL_X - pad, BARREL_X + BARREL_WIDTH + pad),
            (BOX_X - pad, BOX_X + BOX_WIDTH + pad),
        ]
        
        # Inset slightly from cliff edges so pickups don't spawn right at the edge
        self.ground_left = GROUND_LEFT + 20
        self.ground_right = GROUND_RIGHT - 20
        
        self.medkit_w = MEDKIT_DISPLAY_W
        self.medkit_h = MEDKIT_DISPLAY_H
        self.ammo_w = AMMOBOX_DISPLAY_W
        self.ammo_h = AMMOBOX_DISPLAY_H
        
        # Randomize initial timers so pickups don't all spawn at the same time
        self.health_timer = random.uniform(HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX)
        self.ammo_timer = random.uniform(AMMO_SPAWN_MIN, AMMO_SPAWN_MAX)
    
    def _overlaps_obstacle(self, x):
        """Check if this X position is inside an obstacle's no-spawn zone."""
        for left, right in self.obstacles:
            if left <= x <= right:
                return True
        return False
    
    def _overlaps_existing(self, x, y, w, h, health_group, ammo_group):
        """Make sure we don't stack pickups on top of each other."""
        new_rect = pygame.Rect(x, y, w, h)
        for pack in health_group:
            if new_rect.colliderect(pack.rect):
                return True
        for pack in ammo_group:
            if new_rect.colliderect(pack.rect):
                return True
        return False
    
    def _pick_ground_spot(self, pw, ph, health_group, ammo_group):
        """Try up to 15 random ground positions. Returns (x,y) or None if all blocked."""
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
        """Try each platform in random order, place pickup on top. Returns (x,y) or None."""
        if not self.platforms:
            return None
        plats = list(self.platforms)
        random.shuffle(plats)
        for plat in plats:
            pr = plat.rect
            max_left = pr.left + 5
            max_right = pr.right - pw - 5
            if max_right <= max_left:
                x = pr.centerx - pw // 2 + PICKUP_PLATFORM_X_OFFSET
            else:
                x = random.randint(max_left, max_right) + PICKUP_PLATFORM_X_OFFSET
            y = pr.top - ph + PICKUP_PLATFORM_Y_OFFSET
            if not self._overlaps_existing(x, y, pw, ph, health_group, ammo_group):
                return (x, y)
        return None
    
    def _pick_spawn(self, pw, ph, health_group, ammo_group):
        """50/50 chance to try ground vs platform first, with the other as fallback."""
        if random.random() < 0.5:
            spot = self._pick_platform_spot(pw, ph, health_group, ammo_group)
            if spot:
                return spot
            return self._pick_ground_spot(pw, ph, health_group, ammo_group)
        else:
            spot = self._pick_ground_spot(pw, ph, health_group, ammo_group)
            if spot:
                return spot
            return self._pick_platform_spot(pw, ph, health_group, ammo_group)
    
    def update(self, dt, health_group, ammo_group, images):
        """Tick spawn timers. When a timer hits zero, try to place a new pickup."""
        self.health_timer -= dt
        self.ammo_timer -= dt
        
        # Only 1 health pack on screen at a time
        if self.health_timer <= 0:
            self.health_timer = random.uniform(HEALTH_SPAWN_MIN, HEALTH_SPAWN_MAX)
            if len(health_group) < 1:
                spot = self._pick_spawn(
                    self.medkit_w, self.medkit_h, health_group, ammo_group)
                if spot:
                    health_group.add(HealthPack(spot[0], spot[1], images["health_pack"]))
        
        # Up to 2 ammo packs on screen at a time
        if self.ammo_timer <= 0:
            self.ammo_timer = random.uniform(AMMO_SPAWN_MIN, AMMO_SPAWN_MAX)
            if len(ammo_group) < 2:
                spot = self._pick_spawn(
                    self.ammo_w, self.ammo_h, health_group, ammo_group)
                if spot:
                    ammo_group.add(AmmoPack(spot[0], spot[1], images["ammo_box"]))
