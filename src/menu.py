# src/menu.py

import pygame
from src.constants import SCREEN_W, SCREEN_H


class MainMenu:
    """Main menu screen."""
    
    def __init__(self, bg_image, font_large, font_medium):
        self.bg = bg_image
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Play button rect (centered on screen)
        self.play_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 - 40, 200, 80)
    
    def handle_event(self, event) -> str:
        """Returns 'play' if play was clicked, else None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "play"
        return None
    
    def draw(self, screen):
        """Draw main menu."""
        screen.blit(self.bg, (0, 0))
        
        # Title
        title = self.font_large.render("DUEL-STRIKE", True, (255, 220, 50))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=180))
        
        # Play button
        mouse_pos = pygame.mouse.get_pos()
        hover = self.play_rect.collidepoint(mouse_pos)
        btn_color = (80, 200, 80) if hover else (50, 150, 50)
        pygame.draw.rect(screen, btn_color, self.play_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.play_rect, 3, border_radius=12)
        play_text = self.font_medium.render("PLAY", True, (255, 255, 255))
        screen.blit(play_text, play_text.get_rect(center=self.play_rect.center))


class PauseMenu:
    """Pause menu overlay."""
    
    def __init__(self, font):
        self.font = font
        self.audio_manager = None
        w, h = 340, 320
        self.panel_rect = pygame.Rect(SCREEN_W//2 - w//2, SCREEN_H//2 - h//2, w, h)
        
        # Buttons stacked vertically, centered
        bw, bh = 240, 56
        cx = SCREEN_W // 2 - bw // 2
        base_y = self.panel_rect.y + 80
        gap = 68
        self.btn_continue = pygame.Rect(cx, base_y, bw, bh)
        self.btn_new = pygame.Rect(cx, base_y + gap, bw, bh)
        self.btn_exit = pygame.Rect(cx, base_y + gap * 2, bw, bh)
    
    def handle_event(self, event) -> str:
        """Returns 'continue', 'new', 'exit', or None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_continue.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "continue"
            if self.btn_new.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "new"
            if self.btn_exit.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "exit"
        # Also support Escape to resume
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_click")
            return "continue"
        return None
    
    def draw(self, screen):
        """Draw pause menu overlay."""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # Panel background
        pygame.draw.rect(screen, (30, 30, 40), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (100, 100, 120), self.panel_rect, 3, border_radius=16)
        
        # Pause title
        title = self.font.render("PAUSED", True, (255, 220, 60))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 24))
        
        # Buttons
        mouse = pygame.mouse.get_pos()
        for rect, label in [
            (self.btn_continue, "Continue"),
            (self.btn_new, "Start New"),
            (self.btn_exit, "Exit"),
        ]:
            hover = rect.collidepoint(mouse)
            color = (70, 130, 200) if hover else (45, 90, 150)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 220), rect, 2, border_radius=10)
            text = self.font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))


class GameOverMenu:
    """Game over menu overlay."""

    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        w, h = 400, 380
        self.panel_rect = pygame.Rect(SCREEN_W//2 - w//2, SCREEN_H//2 - h//2, w, h)

        # Buttons stacked vertically, centered
        bw, bh = 280, 60
        cx = SCREEN_W // 2 - bw // 2
        base_y = self.panel_rect.y + 150
        gap = 72
        self.btn_new = pygame.Rect(cx, base_y, bw, bh)
        self.btn_exit = pygame.Rect(cx, base_y + gap, bw, bh)

    def handle_event(self, event) -> str:
        """Returns 'new', 'exit', or None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_new.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "new"
            if self.btn_exit.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "exit"
        return None

    def draw(self, screen, winner_name):
        """Draw game over menu overlay."""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Panel background
        pygame.draw.rect(screen, (40, 30, 30), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (120, 100, 100), self.panel_rect, 3, border_radius=16)

        # Title
        title = self.font_large.render("GAME OVER", True, (255, 80, 80))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 30))

        # Winner text
        winner_text = self.font_medium.render(f"{winner_name} WINS!", True, (255, 255, 100))
        screen.blit(winner_text, winner_text.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 100))

        # Buttons
        mouse = pygame.mouse.get_pos()
        for rect, label in [
            (self.btn_new, "Play Again"),
            (self.btn_exit, "Main Menu"),
        ]:
            hover = rect.collidepoint(mouse)
            color = (200, 70, 70) if hover else (150, 45, 45)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (220, 200, 200), rect, 2, border_radius=10)
            text = self.font_medium.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))

