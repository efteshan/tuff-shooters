# main.py

import os
import pygame
from src.game import Game


def main():
    """Entry point for Duel-Strike game."""
    # Set SDL render quality to "best" (anisotropic) BEFORE init.
    # Without this, pygame.SCALED uses nearest-neighbour upscaling
    # which makes the entire game look pixelated/crispy on fullscreen.
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "best"
    pygame.init()
    screen = pygame.display.set_mode(
        (1280, 720),
        pygame.FULLSCREEN | pygame.SCALED
    )
    pygame.display.set_caption("Duel-Strike")
    
    game = Game(screen)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Bug fix #10: Cap dt at 0.05 to prevent physics explosion
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)
        
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
    
    pygame.quit()


if __name__ == "__main__":
    main()
