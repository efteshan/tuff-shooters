# src/bullet.py — All projectile types: pistol bullets, shotgun pellets, rockets, and explosions.

import pygame
import math
from src.constants import BULLET_SPEED, BULLET_DAMAGE, VIRTUAL_W, BAZOOKA_SPEED, BAZOOKA_DAMAGE, BAZOOKA_SPLASH_DAMAGE, BAZOOKA_SPLASH_RADIUS, SHOTGUN_PELLET_DAMAGE, SHOTGUN_PELLET_SPEED, SHOTGUN_MAX_RANGE, SHOTGUN_MIN_RANGE


class Bullet(pygame.sprite.Sprite):
    """Standard pistol bullet — travels in a straight line at high speed."""
    
    def __init__(self, x, y, direction, owner_id, aim_x=None, aim_y=None):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        
        # If given an aim vector, normalize it and use that direction instead of just left/right
        if aim_x is not None and aim_y is not None:
            mag = math.sqrt(aim_x**2 + aim_y**2)
            if mag > 0:
                self.vel_x = BULLET_SPEED * (aim_x / mag)
                self.vel_y = BULLET_SPEED * (aim_y / mag)
            else:
                self.vel_x = BULLET_SPEED * direction
                self.vel_y = 0.0
        else:
            self.vel_x = BULLET_SPEED * direction
            self.vel_y = 0.0
        
        self.owner_id = owner_id  # Which player fired this (1 or 2), so we don't hit ourselves
        self.damage = BULLET_DAMAGE
        self.alive = True
        
        # Small yellow rectangle as the bullet visual
        self.image = pygame.Surface((10, 4), pygame.SRCALPHA)
        self.image.fill((255, 230, 80))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self, dt):
        self.x += self.vel_x * dt
        self.rect.centerx = int(self.x)
        
        # Remove bullet once it flies off-screen
        if self.x < -50 or self.x > VIRTUAL_W + 50:
            self.kill()
            self.alive = False
    
    def draw(self, surface, camera):
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        adjusted_rect = self.rect.copy()
        adjusted_rect.x = self.x - self.rect.width // 2
        adjusted_rect.y = self.y - self.rect.height // 2
        surface.blit(self.image, adjusted_rect)


class ShotgunPellet(pygame.sprite.Sprite):
    """One pellet from a shotgun blast. Multiple of these fire at once in a spread pattern.
    Does zero damage at point-blank range (min_range) to prevent instant kills up close."""

    def __init__(self, x, y, direction, angle_deg, owner_id, base_aim_angle=None):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.owner_id = owner_id
        self.damage = SHOTGUN_PELLET_DAMAGE
        self.max_range = SHOTGUN_MAX_RANGE
        self.min_range = SHOTGUN_MIN_RANGE
        self.distance_traveled = 0.0
        self.alive = True
        self.VIRTUAL_W = VIRTUAL_W

        # Calculate pellet direction: base aim angle + per-pellet spread offset
        if base_aim_angle is not None:
            actual_angle = base_aim_angle + angle_deg
        else:
            actual_angle = angle_deg if direction == 1 else (180 - angle_deg)
        rad = math.radians(actual_angle)
        self.vel_x = math.cos(rad) * SHOTGUN_PELLET_SPEED
        self.vel_y = math.sin(rad) * SHOTGUN_PELLET_SPEED
        self.spawn_x = x
        self.spawn_y = y

        # Small orange dot as the pellet visual
        self.image = pygame.Surface((6, 3), pygame.SRCALPHA)
        self.image.fill((255, 160, 50))
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def get_effective_damage(self, target_x):
        """Returns 0 if the target is too close (prevents point-blank abuse)."""
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

        # Kill pellet when it reaches max range or flies off screen
        if (self.distance_traveled >= self.max_range or
                self.x < -50 or self.x > self.VIRTUAL_W + 50):
            self.kill()
            self.alive = False

    def draw(self, surface, camera):
        surface.blit(self.image, self.rect)

    def kill(self):
        self.alive = False
        super().kill()


class Rocket(pygame.sprite.Sprite):
    """Bazooka rocket — slower than bullets but explodes on impact for splash damage."""
    
    def __init__(self, x, y, direction, owner_id, aim_x=None, aim_y=None):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        # Use aim vector if provided, otherwise fire straight left/right
        if hasattr(self, 'aim_x') and aim_x is not None and aim_y is not None:
            self.vel_x = BAZOOKA_SPEED * aim_x
            self.vel_y = BAZOOKA_SPEED * aim_y
            angle = math.degrees(math.atan2(-aim_y, aim_x))
        elif aim_x is not None and aim_y is not None:
            self.vel_x = BAZOOKA_SPEED * aim_x
            self.vel_y = BAZOOKA_SPEED * aim_y
            angle = math.degrees(math.atan2(-aim_y, aim_x))
        else:
            self.vel_x = BAZOOKA_SPEED * direction
            self.vel_y = 0.0
            angle = 0 if direction == 1 else 180
        self.owner_id = owner_id
        self.damage = BAZOOKA_DAMAGE
        self.alive = True
        
        # Draw the rocket shape: green body, red warhead tip, grey fins
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (80, 100, 80), (0, 1, 16, 8))    # Body
        pygame.draw.ellipse(self.image, (200, 50, 50), (12, 1, 8, 8))    # Warhead tip
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, 4, 3))         # Top fin
        pygame.draw.rect(self.image, (50, 50, 50), (0, 7, 4, 3))         # Bottom fin
        
        # Flip the sprite if firing left
        if direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self, dt):
        self.x += self.vel_x * dt
        self.rect.centerx = int(self.x)
        
        if self.x < -50 or self.x > VIRTUAL_W + 50:
            self.kill()
            self.alive = False
    
    def draw(self, surface, camera):
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        # Draw a small fire trail behind the rocket for visual flair
        trail_x = self.x - (10 if self.vel_x > 0 else -10)
        pygame.draw.circle(surface, (255, 150, 50), (int(trail_x), int(self.y)), 3)
        pygame.draw.circle(surface, (200, 200, 200), (int(trail_x - (5 if self.vel_x > 0 else -5)), int(self.y)), 2)
        surface.blit(self.image, self.rect)


class Explosion(pygame.sprite.Sprite):
    """Visual + damage explosion created when a rocket hits something.
    Damages all players within splash_radius on the first frame, then fades out visually."""
    
    def __init__(self, x, y, owner_id):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.owner_id = owner_id
        self.damage = BAZOOKA_SPLASH_DAMAGE
        self.radius = BAZOOKA_SPLASH_RADIUS
        self.alive = True
        self.life = 0.3          # How long the explosion visual lasts
        self.max_life = 0.3
        self.has_damaged = False  # Only deal damage once (on the first frame)
        
    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.kill()
            self.alive = False
            
    def draw(self, surface, camera):
        # Animate the explosion as expanding circles that fade from fire to smoke
        progress = 1.0 - (self.life / self.max_life)
        if progress < 1.0:
            # Grow fast at first, then slow down (ease-out curve)
            current_radius = int(self.radius * (0.2 + 0.8 * (1.0 - (1.0 - progress)**2)))
            
            cx = int(self.x)
            cy = int(self.y)
            
            if progress < 0.8:
                # Fire phase: red outer ring, orange middle, white-hot center
                pygame.draw.circle(surface, (255, 60, 0), (cx, cy), current_radius)
                pygame.draw.circle(surface, (255, 180, 0), (cx, cy), int(current_radius * 0.7))
                pygame.draw.circle(surface, (255, 255, 200), (cx, cy), int(current_radius * 0.4))
            else:
                # Smoke phase: grey circles as the explosion fades away
                pygame.draw.circle(surface, (100, 100, 100), (cx, cy), current_radius)
                pygame.draw.circle(surface, (150, 150, 150), (cx, cy), int(current_radius * 0.6))
