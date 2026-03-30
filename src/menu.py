# src/menu.py

import pygame
import os
from src.constants import SCREEN_W, SCREEN_H


class MainMenu:
    """Main menu screen."""
    
    def __init__(self, bg_image, font_large, font_medium):
        self.bg = bg_image
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Play button rect (centered on screen)
        self.play_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 - 100, 200, 60)
        # Head War button (below Play)
        self.headwar_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 - 28, 200, 60)
        # Drop Faces button (below Head War)
        self.faces_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 + 44, 200, 48)
    
    def handle_event(self, event) -> str:
        """Returns 'play', 'head_war', 'drop_faces', or None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "play"
            if self.headwar_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "head_war"
            if self.faces_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "drop_faces"
        return None
    
    def draw(self, screen):
        """Draw main menu."""
        screen.blit(self.bg, (0, 0))
        
        # Title
        title = self.font_large.render("tuff shooters", True, (255, 220, 50))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=180))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Play button
        hover = self.play_rect.collidepoint(mouse_pos)
        btn_color = (80, 200, 80) if hover else (50, 150, 50)
        pygame.draw.rect(screen, btn_color, self.play_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.play_rect, 3, border_radius=12)
        play_text = self.font_medium.render("PLAY", True, (255, 255, 255))
        screen.blit(play_text, play_text.get_rect(center=self.play_rect.center))
        
        # Head War button
        hover_hw = self.headwar_rect.collidepoint(mouse_pos)
        hw_color = (220, 90, 40) if hover_hw else (180, 60, 25)
        pygame.draw.rect(screen, hw_color, self.headwar_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 200, 100), self.headwar_rect, 3, border_radius=12)
        hw_text = self.font_medium.render("HEAD WAR", True, (255, 240, 200))
        screen.blit(hw_text, hw_text.get_rect(center=self.headwar_rect.center))
        
        # Drop Faces button
        hover2 = self.faces_rect.collidepoint(mouse_pos)
        btn2_color = (185, 145, 65) if hover2 else (148, 108, 42)
        pygame.draw.rect(screen, btn2_color, self.faces_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 220, 150), self.faces_rect, 2, border_radius=12)
        faces_text = self.font_medium.render("Drop Faces", True, (255, 255, 240))
        screen.blit(faces_text, faces_text.get_rect(center=self.faces_rect.center))


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


class DropFacesMenu:
    """Modal for selecting custom face images for P1 and P2."""
    
    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Panel dimensions
        pw, ph = 620, 420
        self.panel_rect = pygame.Rect(SCREEN_W//2 - pw//2, SCREEN_H//2 - ph//2, pw, ph)
        px, py = self.panel_rect.x, self.panel_rect.y
        
        # Face box size
        box_size = 100
        box_y = py + 110
        gap = 40  # gap between the two zones
        
        # P1 zone (left half)
        p1_cx = px + pw//4
        self.p1_box = pygame.Rect(p1_cx - box_size//2, box_y, box_size, box_size)
        self.p1_remove = pygame.Rect(p1_cx - 40, box_y + box_size + 12, 80, 30)
        # Size +/- buttons for P1 (below remove)
        btn_w, btn_h = 28, 28
        size_y = box_y + box_size + 48
        self.p1_minus = pygame.Rect(p1_cx - 48, size_y, btn_w, btn_h)
        self.p1_plus = pygame.Rect(p1_cx + 20, size_y, btn_w, btn_h)
        
        # P2 zone (right half)
        p2_cx = px + 3*pw//4
        self.p2_box = pygame.Rect(p2_cx - box_size//2, box_y, box_size, box_size)
        self.p2_remove = pygame.Rect(p2_cx - 40, box_y + box_size + 12, 80, 30)
        # Size +/- buttons for P2
        self.p2_minus = pygame.Rect(p2_cx - 48, size_y, btn_w, btn_h)
        self.p2_plus = pygame.Rect(p2_cx + 20, size_y, btn_w, btn_h)
        
        # Confirm button
        self.btn_go = pygame.Rect(SCREEN_W//2 - 90, py + ph - 62, 180, 50)
        
        # Stored faces (pygame.Surface or None)
        self.p1_face = None
        self.p2_face = None
        
        # Per-player head base scale
        self.p1_head_base = 1.0
        self.p2_head_base = 1.0
        
        # Pre-cache overlay
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 180))
        
        # Font for + icon
        self._font_plus = pygame.font.Font(None, 72)
        self._font_small = pygame.font.Font(None, 22)
        self._font_btn = pygame.font.Font(None, 28)
    
    def _open_file_dialog(self):
        """Open a native file dialog to select a PNG image. Returns a pygame.Surface or None."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            path = filedialog.askopenfilename(
                title="Select Face Image",
                filetypes=[("PNG Images", "*.png"), ("All Images", "*.png;*.jpg;*.jpeg;*.bmp")]
            )
            root.destroy()
            if path and os.path.isfile(path):
                img = pygame.image.load(path).convert_alpha()
                # Scale to fit bobblehead size (max 48x48) preserving aspect ratio
                w, h = img.get_size()
                scale = min(48 / w, 48 / h)
                new_w, new_h = int(w * scale), int(h * scale)
                return pygame.transform.smoothscale(img, (max(1, new_w), max(1, new_h)))
        except Exception:
            pass
        return None
    
    def handle_event(self, event) -> str:
        """Returns 'done' when confirmed, else None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # P1 face box
            if self.p1_box.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                face = self._open_file_dialog()
                if face is not None:
                    self.p1_face = face
                return None
            
            # P2 face box
            if self.p2_box.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                face = self._open_file_dialog()
                if face is not None:
                    self.p2_face = face
                return None
            
            # P1 remove
            if self.p1_remove.collidepoint(event.pos) and self.p1_face is not None:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                self.p1_face = None
                return None
            
            # P2 remove
            if self.p2_remove.collidepoint(event.pos) and self.p2_face is not None:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                self.p2_face = None
                return None
            
            # Size +/- buttons
            if self.p1_minus.collidepoint(event.pos):
                self.p1_head_base = max(0.5, round(self.p1_head_base - 0.1, 1))
                return None
            if self.p1_plus.collidepoint(event.pos):
                self.p1_head_base = min(2.0, round(self.p1_head_base + 0.1, 1))
                return None
            if self.p2_minus.collidepoint(event.pos):
                self.p2_head_base = max(0.5, round(self.p2_head_base - 0.1, 1))
                return None
            if self.p2_plus.collidepoint(event.pos):
                self.p2_head_base = min(2.0, round(self.p2_head_base + 0.1, 1))
                return None
            
            # Let's Go!! button
            if self.btn_go.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "done"
        
        # Escape to go back
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "done"
        
        return None
    
    def draw(self, screen, bg_image):
        """Draw the Drop Faces modal."""
        # Background
        screen.blit(bg_image, (0, 0))
        screen.blit(self._overlay, (0, 0))
        
        # Panel
        pygame.draw.rect(screen, (35, 30, 25), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (180, 140, 60), self.panel_rect, 3, border_radius=16)
        
        # Title
        title = self.font_large.render("DROP FACES", True, (255, 210, 80))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 20))
        
        # Subtitle
        sub = self._font_small.render("Click a box to select a custom face image", True, (180, 170, 150))
        screen.blit(sub, sub.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 78))
        
        mouse = pygame.mouse.get_pos()
        
        # Draw P1 and P2 zones
        for label, box, face, remove_rect, color in [
            ("P1", self.p1_box, self.p1_face, self.p1_remove, (60, 120, 220)),
            ("P2", self.p2_box, self.p2_face, self.p2_remove, (220, 60, 60)),
        ]:
            # Label above box
            lbl = self.font_medium.render(label, True, color)
            screen.blit(lbl, lbl.get_rect(centerx=box.centerx, bottom=box.y - 8))
            
            # Box background
            hover_box = box.collidepoint(mouse)
            box_bg = (60, 55, 45) if not hover_box else (80, 75, 55)
            pygame.draw.rect(screen, box_bg, box, border_radius=10)
            pygame.draw.rect(screen, color, box, 2, border_radius=10)
            
            if face is not None:
                # Draw preview centered in box
                fw, fh = face.get_size()
                # Scale preview to fit box (with padding)
                pmax = box.width - 16
                pscale = min(pmax / fw, pmax / fh)
                pw2, ph2 = int(fw * pscale), int(fh * pscale)
                preview = pygame.transform.smoothscale(face, (max(1, pw2), max(1, ph2)))
                screen.blit(preview, preview.get_rect(center=box.center))
            else:
                # Draw + icon
                plus = self._font_plus.render("+", True, (120, 110, 90))
                screen.blit(plus, plus.get_rect(center=box.center))
            
            # Remove button (only if face is set)
            if face is not None:
                hover_rm = remove_rect.collidepoint(mouse)
                rm_color = (180, 60, 60) if hover_rm else (120, 50, 50)
                pygame.draw.rect(screen, rm_color, remove_rect, border_radius=6)
                pygame.draw.rect(screen, (200, 150, 150), remove_rect, 1, border_radius=6)
                rm_text = self._font_small.render("Remove", True, (255, 220, 220))
                screen.blit(rm_text, rm_text.get_rect(center=remove_rect.center))
        
        # Draw size +/- controls for each player
        for minus_r, plus_r, scale_val in [
            (self.p1_minus, self.p1_plus, self.p1_head_base),
            (self.p2_minus, self.p2_plus, self.p2_head_base),
        ]:
            # "-" button
            hover_m = minus_r.collidepoint(mouse)
            c_m = (100, 80, 60) if hover_m else (70, 55, 40)
            pygame.draw.rect(screen, c_m, minus_r, border_radius=6)
            pygame.draw.rect(screen, (160, 130, 80), minus_r, 1, border_radius=6)
            mt = self._font_btn.render("-", True, (255, 230, 180))
            screen.blit(mt, mt.get_rect(center=minus_r.center))
            # "+" button
            hover_p = plus_r.collidepoint(mouse)
            c_p = (100, 80, 60) if hover_p else (70, 55, 40)
            pygame.draw.rect(screen, c_p, plus_r, border_radius=6)
            pygame.draw.rect(screen, (160, 130, 80), plus_r, 1, border_radius=6)
            pt = self._font_btn.render("+", True, (255, 230, 180))
            screen.blit(pt, pt.get_rect(center=plus_r.center))
            # Scale label between buttons
            sv = self._font_small.render(f"{scale_val:.1f}x", True, (200, 180, 140))
            sx = (minus_r.right + plus_r.left) // 2
            sy = minus_r.centery
            screen.blit(sv, sv.get_rect(center=(sx, sy)))
        
        # "Let's Go!!" button
        hover_go = self.btn_go.collidepoint(mouse)
        go_color = (80, 200, 80) if hover_go else (50, 150, 50)
        pygame.draw.rect(screen, go_color, self.btn_go, border_radius=12)
        pygame.draw.rect(screen, (200, 255, 200), self.btn_go, 2, border_radius=12)
        go_text = self.font_medium.render("Let's Go!!", True, (255, 255, 255))
        screen.blit(go_text, go_text.get_rect(center=self.btn_go.center))

