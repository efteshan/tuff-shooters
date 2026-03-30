# main.py — Game entry point. Run this file to start the game.

import os
import gc
import pygame
from src.game import Game


def main():
    # Use "linear" texture filtering for smooth scaling without killing performance
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
    
    # Python's automatic garbage collector causes random frame stutters (10-30ms freezes).
    # We disable it and manually run a lightweight gen-0 sweep every 10 seconds instead.
    gc.disable()
    gc_timer = 0.0
    GC_INTERVAL = 10.0
    
    while running:
        # Delta time in seconds. Capped at 0.05s so physics don't explode on lag spikes.
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)
        
        # Run lightweight garbage collection on a timer instead of letting Python decide
        gc_timer += dt
        if gc_timer >= GC_INTERVAL:
            gc_timer = 0.0
            gc.collect(0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            game.handle_event(event)
        
        game.update(dt)
        game.draw()
        
        pygame.display.flip()
    
    # Re-enable GC before exit so Python cleans up properly
    gc.enable()
    gc.collect()
    pygame.quit()


if __name__ == "__main__":
    main()
