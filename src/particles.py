# src/particles.py

import pygame
import random


class GifPlayer:
    """Plays GIF animations from horizontal PNG strips."""
    
    def __init__(self, strip_path: str, frame_count: int, fps: float = 24):
        try:
            strip = pygame.image.load(strip_path).convert_alpha()
        except FileNotFoundError:
            # Create transparent placeholder (no visible effect)
            strip = pygame.Surface((frame_count * 40, 40), pygame.SRCALPHA)
        
        fw = strip.get_width() // frame_count
        fh = strip.get_height()
        self.frames = [
            strip.subsurface(pygame.Rect(i * fw, 0, fw, fh))
            for i in range(frame_count)
        ]
        self.fps = fps
        self.spf = 1.0 / fps
        self.timer = 0.0
        self.current = 0
    
    def update(self, dt) -> bool:
        """Returns True when animation completes."""
        self.timer += dt
        if self.timer >= self.spf:
            self.timer -= self.spf
            self.current += 1
        return self.current >= len(self.frames)
    
    def get_frame(self) -> pygame.Surface:
        """Get current frame."""
        idx = min(self.current, len(self.frames) - 1)
        return self.frames[idx]


class BaseParticle:
    def update(self, dt): pass
    def draw(self, surface, camera): pass

class FastParticle:
    """Super lightweight particle using elementary Pygame shapes for maximum performance."""
    __slots__ = ['x', 'y', 'vx', 'vy', 'color', 'size', 'lifetime']
    def __init__(self, x, y, color, speed_x, speed_y, size, lifetime):
        self.x = x
        self.y = y
        self.vx = speed_x
        self.vy = speed_y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 800 * dt  # basic gravity
        self.lifetime -= dt
        return self.lifetime <= 0
        
    def draw(self, surface, camera):
        pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.size, self.size))

class MuzzleFlash:
    def __init__(self, x, y, facing, size=1.0):
        self.x = x
        self.y = y
        self.facing = facing
        self.size = size
        self.lifetime = 0.05
    
    def update(self, dt):
        self.lifetime -= dt
        return self.lifetime <= 0
        
    def draw(self, surface, camera):
        # Draw directly to the screen using fast primitives instead of slow per-frame transparent surfaces
        offset_x = 10 if self.facing == 1 else -10
        cx = int(self.x + offset_x)
        cy = int(self.y)
        
        outer_r = int(15 * self.size)
        inner_r = int(6 * self.size)
        
        # Use simple overlapping circles
        pygame.draw.circle(surface, (255, 180, 0), (cx, cy), outer_r)
        pygame.draw.circle(surface, (255, 255, 200), (cx, cy), inner_r)

class BloodSpark:
    """Blood particle effect that plays once and disappears."""
    
    def __init__(self, x, y, gif_strip_path, frame_count):
        self.x = x
        self.y = y
        self.player = GifPlayer(gif_strip_path, frame_count, fps=20)
        self.done = False
    
    def update(self, dt):
        """Update animation."""
        self.done = self.player.update(dt)
    
    def draw(self, surface, camera):
        """Draw blood spark."""
        if not self.done:
            frame = self.player.get_frame()
            # Center the spark on the hit point, small scale (~40x40)
            scaled = pygame.transform.scale(frame, (40, 40))
            # Draw at world position
            surface.blit(scaled, (self.x - 20, self.y - 20))


class ParticleSystem:
    """Manages all particle effects in the game."""
    
    def __init__(self, blood_strip_path, blood_frames):
        self.blood_strip_path = blood_strip_path
        self.blood_frames = blood_frames
        self.active_sparks = []
        self.muzzle_flashes = []
        self.fast_particles = []
    
    def spawn_blood(self, x, y):
        """Spawn a blood spark at the given position."""
        self.active_sparks.append(BloodSpark(x, y, self.blood_strip_path, self.blood_frames))
        
        # Add a few fast blood droplets
        import random
        for _ in range(5):
            vx = random.uniform(-150, 150)
            vy = random.uniform(-250, 50)
            life = random.uniform(0.1, 0.3)
            self.fast_particles.append(FastParticle(x, y, (200, 0, 0), vx, vy, 3, life))
            
    def spawn_sparks(self, x, y, color=(255, 200, 50)):
        """Spawn generic sparks (e.g. for explosions or metal hits)"""
        import random
        for _ in range(8):
            vx = random.uniform(-200, 200)
            vy = random.uniform(-300, 50)
            life = random.uniform(0.1, 0.4)
            self.fast_particles.append(FastParticle(x, y, color, vx, vy, 2, life))
            
    def spawn_dash_dust(self, x, y, facing):
        """Spawn a quick burst of horizontal dust/lines for dashed movement."""
        import random
        for _ in range(3):
            # Burst backwards relative to dash
            vx = random.uniform(-100, 400) * -facing
            vy = random.uniform(-50, 50)
            life = random.uniform(0.1, 0.2)
            c = random.randint(180, 220)
            # Dust uses white/gray fast particles
            self.fast_particles.append(FastParticle(x, y, (c, c, c), vx, vy, random.randint(2, 4), life))
        
    def spawn_muzzle_flash(self, x, y, facing, size=1.0):
        """Spawn a muzzle flash."""
        self.muzzle_flashes.append(MuzzleFlash(x, y, facing, size))
    
    def update(self, dt):
        """Update all active particles."""
        for i in range(len(self.active_sparks) - 1, -1, -1):
            self.active_sparks[i].update(dt)
            if self.active_sparks[i].done:
                self.active_sparks.pop(i)
                
        for i in range(len(self.muzzle_flashes) - 1, -1, -1):
            if self.muzzle_flashes[i].update(dt):
                self.muzzle_flashes.pop(i)
                
        for i in range(len(self.fast_particles) - 1, -1, -1):
            if self.fast_particles[i].update(dt):
                self.fast_particles.pop(i)
    
    def draw(self, surface, camera):
        """Draw all active particles."""
        for spark in self.active_sparks:
            spark.draw(surface, camera)
            
        for mf in self.muzzle_flashes:
            mf.draw(surface, camera)
            
        for fp in self.fast_particles:
            fp.draw(surface, camera)
