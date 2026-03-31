# src/menu.py — All menu screens: main menu, pause menu, game over menu, and face customization.

import pygame
import os
from src.constants import SCREEN_W, SCREEN_H


class MainMenu:
    """Title screen with Play, Head War, and Drop Faces buttons."""
    
    def __init__(self, bg_image, font_large, font_medium):
        self.bg = bg_image
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Button positions — stacked vertically in the center of screen
        self.play_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 - 100, 200, 60)
        self.headwar_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 - 28, 200, 60)
        self.faces_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 + 44, 200, 48)
    
    def handle_event(self, event) -> str:
        """Check if a menu button was clicked. Returns the button name or None."""
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
        screen.blit(self.bg, (0, 0))
        
        # Game title text
        title = self.font_large.render("tuff shooters", True, (255, 220, 50))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=180))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Each button lights up on hover
        hover = self.play_rect.collidepoint(mouse_pos)
        btn_color = (80, 200, 80) if hover else (50, 150, 50)
        pygame.draw.rect(screen, btn_color, self.play_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.play_rect, 3, border_radius=12)
        play_text = self.font_medium.render("PLAY", True, (255, 255, 255))
        screen.blit(play_text, play_text.get_rect(center=self.play_rect.center))
        
        hover_hw = self.headwar_rect.collidepoint(mouse_pos)
        hw_color = (220, 90, 40) if hover_hw else (180, 60, 25)
        pygame.draw.rect(screen, hw_color, self.headwar_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 200, 100), self.headwar_rect, 3, border_radius=12)
        hw_text = self.font_medium.render("HEAD WAR", True, (255, 240, 200))
        screen.blit(hw_text, hw_text.get_rect(center=self.headwar_rect.center))
        
        hover2 = self.faces_rect.collidepoint(mouse_pos)
        btn2_color = (185, 145, 65) if hover2 else (148, 108, 42)
        pygame.draw.rect(screen, btn2_color, self.faces_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 220, 150), self.faces_rect, 2, border_radius=12)
        faces_text = self.font_medium.render("Drop Faces", True, (255, 255, 240))
        screen.blit(faces_text, faces_text.get_rect(center=self.faces_rect.center))


class PauseMenu:
    """Overlay that appears when the game is paused. Has Continue, Start New, and Exit buttons."""
    
    def __init__(self, font):
        self.font = font
        self.audio_manager = None
        w, h = 340, 320
        self.panel_rect = pygame.Rect(SCREEN_W//2 - w//2, SCREEN_H//2 - h//2, w, h)
        
        # Three buttons stacked inside the panel
        bw, bh = 240, 56
        cx = SCREEN_W // 2 - bw // 2
        base_y = self.panel_rect.y + 80
        gap = 68
        self.btn_continue = pygame.Rect(cx, base_y, bw, bh)
        self.btn_new = pygame.Rect(cx, base_y + gap, bw, bh)
        self.btn_exit = pygame.Rect(cx, base_y + gap * 2, bw, bh)
    
    def handle_event(self, event) -> str:
        """Returns which button was clicked, or None. Escape also counts as 'continue'."""
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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_click")
            return "continue"
        return None
    
    def draw(self, screen):
        # Dark semi-transparent backdrop
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # Panel card
        pygame.draw.rect(screen, (30, 30, 40), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (100, 100, 120), self.panel_rect, 3, border_radius=16)
        
        title = self.font.render("PAUSED", True, (255, 220, 60))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 24))
        
        # Render each button with hover highlight
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
    """Shows the winner and offers Play Again or Main Menu buttons."""

    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        w, h = 400, 380
        self.panel_rect = pygame.Rect(SCREEN_W//2 - w//2, SCREEN_H//2 - h//2, w, h)

        bw, bh = 280, 60
        cx = SCREEN_W // 2 - bw // 2
        base_y = self.panel_rect.y + 150
        gap = 72
        self.btn_new = pygame.Rect(cx, base_y, bw, bh)
        self.btn_exit = pygame.Rect(cx, base_y + gap, bw, bh)

    def handle_event(self, event) -> str:
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
        # Dark backdrop
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Red-tinted panel
        pygame.draw.rect(screen, (40, 30, 30), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (120, 100, 100), self.panel_rect, 3, border_radius=16)

        title = self.font_large.render("GAME OVER", True, (255, 80, 80))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 30))

        winner_text = self.font_medium.render(f"{winner_name} WINS!", True, (255, 255, 100))
        screen.blit(winner_text, winner_text.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 100))

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
    """Lets players pick custom face images from their computer.
    Each player gets a drop zone — click to open a file picker, and the selected
    image becomes that player's head in-game. Also has +/- buttons to resize heads."""
    
    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Main panel centered on screen
        pw, ph = 620, 420
        self.panel_rect = pygame.Rect(SCREEN_W//2 - pw//2, SCREEN_H//2 - ph//2, pw, ph)
        px, py = self.panel_rect.x, self.panel_rect.y
        
        # Face preview boxes (P1 left, P2 right)
        box_size = 100
        box_y = py + 110
        
        p1_cx = px + pw//4
        self.p1_box = pygame.Rect(p1_cx - box_size//2, box_y, box_size, box_size)
        self.p1_remove = pygame.Rect(p1_cx - 40, box_y + box_size + 12, 80, 30)
        
        # Head size +/- buttons below each face box
        btn_w, btn_h = 28, 28
        size_y = box_y + box_size + 48
        self.p1_minus = pygame.Rect(p1_cx - 48, size_y, btn_w, btn_h)
        self.p1_plus = pygame.Rect(p1_cx + 20, size_y, btn_w, btn_h)
        
        p2_cx = px + 3*pw//4
        self.p2_box = pygame.Rect(p2_cx - box_size//2, box_y, box_size, box_size)
        self.p2_remove = pygame.Rect(p2_cx - 40, box_y + box_size + 12, 80, 30)
        self.p2_minus = pygame.Rect(p2_cx - 48, size_y, btn_w, btn_h)
        self.p2_plus = pygame.Rect(p2_cx + 20, size_y, btn_w, btn_h)
        
        # Confirm button at the bottom
        self.btn_go = pygame.Rect(SCREEN_W//2 - 90, py + ph - 62, 180, 50)
        
        # The actual face images (None = no custom face selected)
        self.p1_face = None
        self.p2_face = None
        
        # Head scale multiplier (adjustable with +/- buttons)
        self.p1_head_base = 1.0
        self.p2_head_base = 1.0
        
        # Pre-build the dark overlay so we don't recreate it every frame
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 180))
        
        self._font_plus = pygame.font.Font(None, 72)
        self._font_small = pygame.font.Font(None, 22)
        self._font_btn = pygame.font.Font(None, 28)
    
    def _open_file_dialog(self):
        """Open a native Windows file picker. Returns a scaled pygame Surface or None."""
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
                # Scale to fit 48x48 max while keeping aspect ratio
                w, h = img.get_size()
                scale = min(48 / w, 48 / h)
                new_w, new_h = int(w * scale), int(h * scale)
                return pygame.transform.smoothscale(img, (max(1, new_w), max(1, new_h)))
        except Exception:
            pass
        return None
    
    def handle_event(self, event) -> str:
        """Handle clicks on face boxes, remove buttons, size buttons, and confirm.
        Returns 'done' when the player confirms, otherwise None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.p1_box.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                face = self._open_file_dialog()
                if face is not None:
                    self.p1_face = face
                return None
            
            if self.p2_box.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                face = self._open_file_dialog()
                if face is not None:
                    self.p2_face = face
                return None
            
            if self.p1_remove.collidepoint(event.pos) and self.p1_face is not None:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                self.p1_face = None
                return None
            
            if self.p2_remove.collidepoint(event.pos) and self.p2_face is not None:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                self.p2_face = None
                return None
            
            # Head size adjustment (clamp between 0.5x and 2.0x)
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
            
            if self.btn_go.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "done"
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "done"
        
        return None
    
    def draw(self, screen, bg_image):
        screen.blit(bg_image, (0, 0))
        screen.blit(self._overlay, (0, 0))
        
        # Panel card
        pygame.draw.rect(screen, (35, 30, 25), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (180, 140, 60), self.panel_rect, 3, border_radius=16)
        
        title = self.font_large.render("DROP FACES", True, (255, 210, 80))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 20))
        
        sub = self._font_small.render("Click a box to select a custom face image", True, (180, 170, 150))
        screen.blit(sub, sub.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 78))
        
        mouse = pygame.mouse.get_pos()
        
        # Draw both player face zones (P1 = blue, P2 = red)
        for label, box, face, remove_rect, color in [
            ("P1", self.p1_box, self.p1_face, self.p1_remove, (60, 120, 220)),
            ("P2", self.p2_box, self.p2_face, self.p2_remove, (220, 60, 60)),
        ]:
            # Player label
            lbl = self.font_medium.render(label, True, color)
            screen.blit(lbl, lbl.get_rect(centerx=box.centerx, bottom=box.y - 8))
            
            # Drop zone box — highlights on hover
            hover_box = box.collidepoint(mouse)
            box_bg = (60, 55, 45) if not hover_box else (80, 75, 55)
            pygame.draw.rect(screen, box_bg, box, border_radius=10)
            pygame.draw.rect(screen, color, box, 2, border_radius=10)
            
            if face is not None:
                # Show preview of the selected face image
                fw, fh = face.get_size()
                pmax = box.width - 16
                pscale = min(pmax / fw, pmax / fh)
                pw2, ph2 = int(fw * pscale), int(fh * pscale)
                preview = pygame.transform.smoothscale(face, (max(1, pw2), max(1, ph2)))
                screen.blit(preview, preview.get_rect(center=box.center))
            else:
                # Big "+" icon when no face is selected yet
                plus = self._font_plus.render("+", True, (120, 110, 90))
                screen.blit(plus, plus.get_rect(center=box.center))
            
            # Remove button (only shown when a face is selected)
            if face is not None:
                hover_rm = remove_rect.collidepoint(mouse)
                rm_color = (180, 60, 60) if hover_rm else (120, 50, 50)
                pygame.draw.rect(screen, rm_color, remove_rect, border_radius=6)
                pygame.draw.rect(screen, (200, 150, 150), remove_rect, 1, border_radius=6)
                rm_text = self._font_small.render("Remove", True, (255, 220, 220))
                screen.blit(rm_text, rm_text.get_rect(center=remove_rect.center))
        
        # Head size +/- controls for each player
        for minus_r, plus_r, scale_val in [
            (self.p1_minus, self.p1_plus, self.p1_head_base),
            (self.p2_minus, self.p2_plus, self.p2_head_base),
        ]:
            hover_m = minus_r.collidepoint(mouse)
            c_m = (100, 80, 60) if hover_m else (70, 55, 40)
            pygame.draw.rect(screen, c_m, minus_r, border_radius=6)
            pygame.draw.rect(screen, (160, 130, 80), minus_r, 1, border_radius=6)
            mt = self._font_btn.render("-", True, (255, 230, 180))
            screen.blit(mt, mt.get_rect(center=minus_r.center))
            
            hover_p = plus_r.collidepoint(mouse)
            c_p = (100, 80, 60) if hover_p else (70, 55, 40)
            pygame.draw.rect(screen, c_p, plus_r, border_radius=6)
            pygame.draw.rect(screen, (160, 130, 80), plus_r, 1, border_radius=6)
            pt = self._font_btn.render("+", True, (255, 230, 180))
            screen.blit(pt, pt.get_rect(center=plus_r.center))
            
            # Current scale value displayed between the buttons
            sv = self._font_small.render(f"{scale_val:.1f}x", True, (200, 180, 140))
            sx = (minus_r.right + plus_r.left) // 2
            sy = minus_r.centery
            screen.blit(sv, sv.get_rect(center=(sx, sy)))
        
        # Confirm button
        hover_go = self.btn_go.collidepoint(mouse)
        go_color = (80, 200, 80) if hover_go else (50, 150, 50)
        pygame.draw.rect(screen, go_color, self.btn_go, border_radius=12)
        pygame.draw.rect(screen, (200, 255, 200), self.btn_go, 2, border_radius=12)
        go_text = self.font_medium.render("Let's Go!!", True, (255, 255, 255))
        screen.blit(go_text, go_text.get_rect(center=self.btn_go.center))
