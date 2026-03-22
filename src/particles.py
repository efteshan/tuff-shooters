# src/particles.py

import pygame


class GifPlayer:
    """Plays GIF animations from horizontal PNG strips."""
    
    def __init__(self, strip_path: str, frame_count: int, fps: float = 24):
        try:
            strip = pygame.image.load(strip_path).convert_alpha()
        except FileNotFoundError:
            # Create placeholder strip
            strip = pygame.Surface((frame_count * 40, 40), pygame.SRCALPHA)
            for i in range(frame_count):
                color = (255, 0, 0, 200 - i * 40)  # Fading red
                pygame.draw.circle(strip, color, (i * 40 + 20, 20), 15)
        
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
    
    def spawn_blood(self, x, y):
        """Spawn a blood spark at the given position."""
        self.active_sparks.append(BloodSpark(x, y, self.blood_strip_path, self.blood_frames))
    
    def update(self, dt):
        """Update all active particles."""
        for spark in self.active_sparks[:]:
            spark.update(dt)
            if spark.done:
                self.active_sparks.remove(spark)
    
    def draw(self, surface, camera):
        """Draw all active particles."""
        for spark in self.active_sparks:
            spark.draw(surface, camera)
