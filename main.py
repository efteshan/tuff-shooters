# main.py

import os
import gc
import pygame
from src.game import Game


def main():
    """Entry point for Duel-Strike game."""
    # Set SDL render quality to "linear" (bilinear) BEFORE init.
    # "best" uses anisotropic filtering which is very slow with pygame.SCALED.
    # "linear" still looks smooth but is much faster.
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "linear"
    pygame.init()
    screen = pygame.display.set_mode(
        (1280, 720),
        pygame.FULLSCREEN | pygame.SCALED
    )
    pygame.display.set_caption("Duel-Strike")
    
    game = Game(screen)
    
    clock = pygame.time.Clock()
    running = True
    
    # Disable automatic GC — it causes periodic 10-30ms freezes.
    # Instead, do manual gen-0 collection every 10 seconds (~1ms).
    gc.disable()
    gc_timer = 0.0
    GC_INTERVAL = 10.0
    
    while running:
        # Bug fix #10: Cap dt at 0.05 to prevent physics explosion
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)
        
        # Manual GC — gen-0 only, fast and predictable
        gc_timer += dt
        if gc_timer >= GC_INTERVAL:
            gc_timer = 0.0
            gc.collect(0)  # gen-0 only: ~1ms, no full sweep
        
        # === EVENT HANDLING ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            game.handle_event(event)
        
        # === UPDATE ===
        game.update(dt)
        
        # === DRAW ===
        game.draw()
        
        pygame.display.flip()
    
    # Re-enable GC before exit for clean shutdown
    gc.enable()
    gc.collect()
    pygame.quit()


if __name__ == "__main__":
    main()
