# src/menu.py — All menu screens: main menu, pause menu, game over menu, and settings.

import pygame
import os
from src.constants import SCREEN_W, SCREEN_H
class MainMenu:
    """Title screen with Play, Head War, Online, Settings, and Exit buttons.
    Background is a video frame passed in each draw call instead of a static image.
    Buttons use custom PNG images with normal/hover states for an animated feel."""
    
    def __init__(self, bg_image, font_large, font_medium):
        self.bg = bg_image  # fallback static image when video is unavailable
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # ================================================================
        # BUTTON SIZE CONFIGURATION
        # Change these values to manually scale each button image.
        # 1.0 = default size, 1.2 = 20% bigger, 0.8 = 20% smaller, etc.
        # "normal" = when mouse is NOT hovering, "hover" = when mouse IS hovering.
        # Images are always scaled from the ORIGINAL high-res file, so
        # quality stays crisp at any size.
        # ================================================================
        self.play_scale_normal     = 1.4
        self.play_scale_hover      = 1.35
        self.headwar_scale_normal  = 1.3
        self.headwar_scale_hover   = 1.25
        self.online_scale_normal   = 1.2
        self.online_scale_hover    = 1.15
        self.settings_scale_normal = 1.1
        self.settings_scale_hover  = 1.05
        self.exit_scale_normal     = 1.0
        self.exit_scale_hover      = 0.95
        # ================================================================
        
        # ================================================================
        # BUTTON POSITION OFFSETS
        # Shift each button from its default grid position (in pixels).
        # Positive X = move right, Negative X = move left.
        # Positive Y = move down,  Negative Y = move up.
        # ================================================================
        self.play_offset_x     = -32
        self.play_offset_y     = -2
        self.headwar_offset_x  = 66
        self.headwar_offset_y  = 14
        self.online_offset_x   = -34
        self.online_offset_y   = 26
        self.settings_offset_x = 62
        self.settings_offset_y = 28
        self.exit_offset_x     = -15
        self.exit_offset_y     = 27
        # ================================================================
        
        # Button layout — 5 buttons stacked vertically, base size (230x70)
        btn_w, btn_h = 230, 70
        gap = 12  # vertical gap between buttons
        total_h = 5 * btn_h + 4 * gap
        start_y = SCREEN_H // 2 - total_h // 2
        cx = SCREEN_W // 2 - btn_w // 2
        
        self.play_rect = pygame.Rect(cx, start_y, btn_w, btn_h)
        self.headwar_rect = pygame.Rect(cx, start_y + (btn_h + gap), btn_w, btn_h)
        self.online_rect = pygame.Rect(cx, start_y + 2 * (btn_h + gap), btn_w, btn_h)
        self.settings_rect = pygame.Rect(cx, start_y + 3 * (btn_h + gap), btn_w, btn_h)
        self.exit_rect = pygame.Rect(cx, start_y + 4 * (btn_h + gap), btn_w, btn_h)
        
        # Load custom button images — stores (raw_normal, raw_hover, base_w, base_h)
        # Raw images are kept at FULL RESOLUTION so scaling is always crisp.
        self.play_imgs = self._load_button_pair(
            "assets/ui/buttons/play.png",
            "assets/ui/buttons/play_hover.png",
            self.play_rect
        )
        self.headwar_imgs = self._load_button_pair(
            "assets/ui/buttons/headwar.png",
            "assets/ui/buttons/headwar_hover.png",
            self.headwar_rect
        )
        self.online_imgs = self._load_button_pair(
            "assets/ui/buttons/online.png",
            "assets/ui/buttons/online_hover.png",
            self.online_rect
        )
        self.settings_imgs = self._load_button_pair(
            "assets/ui/buttons/settings.png",
            "assets/ui/buttons/settings_hover.png",
            self.settings_rect
        )
        self.exit_imgs = self._load_button_pair(
            "assets/ui/buttons/exit.png",
            "assets/ui/buttons/exit_hover.png",
            self.exit_rect
        )
        
        # Apply position offsets to collision rects (moves both visual + hitbox together)
        self.play_rect.x += self.play_offset_x
        self.play_rect.y += self.play_offset_y
        self.headwar_rect.x += self.headwar_offset_x
        self.headwar_rect.y += self.headwar_offset_y
        self.online_rect.x += self.online_offset_x
        self.online_rect.y += self.online_offset_y
        self.settings_rect.x += self.settings_offset_x
        self.settings_rect.y += self.settings_offset_y
        self.exit_rect.x += self.exit_offset_x
        self.exit_rect.y += self.exit_offset_y
    
    def _load_button_pair(self, normal_path, hover_path, target_rect):
        """Load a normal + hover image pair. Keeps the RAW full-resolution originals
        and records the base target size so scaling is always done from the originals.
        Returns (raw_normal, raw_hover, base_w, base_h) or None if files are missing."""
        try:
            if not os.path.isfile(normal_path) or not os.path.isfile(hover_path):
                return None
            
            # Load at FULL resolution — never downscale these stored copies
            raw_normal = pygame.image.load(normal_path).convert_alpha()
            raw_hover = pygame.image.load(hover_path).convert_alpha()
            
            # Calculate the base target size (what 1.0 scale means) from the rect
            base_w, base_h = self._calc_fit_size(
                raw_normal.get_size(), target_rect.width, target_rect.height
            )
            
            # Update the button rect to match the base image dimensions
            old_centery = target_rect.centery
            target_rect.width = base_w
            target_rect.height = base_h
            target_rect.centerx = SCREEN_W // 2
            target_rect.centery = old_centery
            
            return (raw_normal, raw_hover, base_w, base_h)
        except Exception:
            return None
    
    def _calc_fit_size(self, img_size, max_w, max_h):
        """Calculate the target pixel size to fit within max_w x max_h, preserving aspect ratio."""
        w, h = img_size
        scale = min(max_w / w, max_h / h)
        return max(1, int(w * scale)), max(1, int(h * scale))
    
    def _scale_from_raw(self, raw_surface, base_w, base_h, multiplier):
        """Scale a raw full-res image directly to (base_w * multiplier, base_h * multiplier).
        Always scales from the ORIGINAL high-res source in a single pass for maximum quality."""
        final_w = max(1, int(base_w * multiplier))
        final_h = max(1, int(base_h * multiplier))
        return pygame.transform.smoothscale(raw_surface, (final_w, final_h))
    
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
            if self.online_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "online"
            if self.settings_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "settings"
            if self.exit_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "exit"
        return None
    
    def draw(self, screen, video_frame=None):
        # Draw the video frame if available, otherwise fall back to the static bg image
        if video_frame is not None:
            screen.blit(video_frame, (0, 0))
        else:
            screen.blit(self.bg, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw each button — custom image if loaded, fallback to colored rect if not
        self._draw_button(screen, mouse_pos, self.play_rect, self.play_imgs,
                          self.play_scale_normal, self.play_scale_hover,
                          "PLAY", (80, 200, 80), (50, 150, 50), (255, 255, 255), 3)
        self._draw_button(screen, mouse_pos, self.headwar_rect, self.headwar_imgs,
                          self.headwar_scale_normal, self.headwar_scale_hover,
                          "HEAD WAR", (220, 90, 40), (180, 60, 25), (255, 200, 100), 3)
        self._draw_button(screen, mouse_pos, self.online_rect, self.online_imgs,
                          self.online_scale_normal, self.online_scale_hover,
                          "ONLINE", (60, 120, 220), (40, 80, 170), (150, 200, 255), 3)
        self._draw_button(screen, mouse_pos, self.settings_rect, self.settings_imgs,
                          self.settings_scale_normal, self.settings_scale_hover,
                          "SETTINGS", (185, 145, 65), (148, 108, 42), (255, 220, 150), 2)
        self._draw_button(screen, mouse_pos, self.exit_rect, self.exit_imgs,
                          self.exit_scale_normal, self.exit_scale_hover,
                          "EXIT", (180, 50, 50), (140, 35, 35), (255, 150, 150), 2)
    
    def _draw_button(self, screen, mouse_pos, rect, imgs, scale_normal, scale_hover,
                     fallback_text, hover_color, normal_color, border_color, border_width):
        """Draw a single menu button. Uses custom images if available, falls back to colored rect.
        Images are scaled from the RAW original and drawn CENTER-ANCHORED to the rect."""
        hovering = rect.collidepoint(mouse_pos)
        
        if imgs is not None:
            raw_normal, raw_hover, base_w, base_h = imgs
            if hovering:
                surf = self._scale_from_raw(raw_hover, base_w, base_h, scale_hover)
            else:
                surf = self._scale_from_raw(raw_normal, base_w, base_h, scale_normal)
            # Center-anchor: draw from center of rect, not top-left
            draw_rect = surf.get_rect(center=rect.center)
            screen.blit(surf, draw_rect)
        else:
            # Fallback: draw the old colored rectangle + text
            btn_color = hover_color if hovering else normal_color
            pygame.draw.rect(screen, btn_color, rect, border_radius=12)
            pygame.draw.rect(screen, border_color, rect, border_width, border_radius=12)
            text = self.font_medium.render(fallback_text, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))


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


class SettingsMenu:
    """Settings popup that overlays the menu. Contains:
    1. A close (X) button at the top right
    2. A background music volume slider
    3. The Drop Faces interface (face upload boxes + head size controls)"""
    
    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Main panel centered on screen — taller to fit both settings and drop faces
        pw, ph = 620, 520
        self.panel_rect = pygame.Rect(SCREEN_W//2 - pw//2, SCREEN_H//2 - ph//2, pw, ph)
        px, py = self.panel_rect.x, self.panel_rect.y
        
        # Close (X) button — top right corner of panel
        close_size = 32
        self.close_rect = pygame.Rect(px + pw - close_size - 10, py + 10, close_size, close_size)
        
        # ── Volume slider ──
        slider_w = 360
        slider_h = 8
        slider_y = py + 80
        self.slider_track = pygame.Rect(SCREEN_W//2 - slider_w//2, slider_y, slider_w, slider_h)
        self.volume = 1.0  # 0.0 – 1.0
        self.slider_knob_radius = 10
        self.dragging_slider = False
        
        # ── Drop Faces section ──
        faces_top = slider_y + 60  # start below the slider
        
        # Face preview boxes (P1 left, P2 right)
        box_size = 100
        box_y = faces_top + 50
        
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
        self._font_section = pygame.font.Font(None, 32)
    
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
    
    def _get_knob_x(self):
        """Calculate the X position of the volume slider knob."""
        return self.slider_track.x + int(self.volume * self.slider_track.width)
    
    def _knob_rect(self):
        """Get the clickable rectangle for the slider knob."""
        kx = self._get_knob_x()
        ky = self.slider_track.centery
        r = self.slider_knob_radius
        return pygame.Rect(kx - r, ky - r, r * 2, r * 2)
    
    def handle_event(self, event) -> str:
        """Handle clicks on close button, volume slider, face boxes, remove/size buttons.
        Returns 'done' when the player closes the panel, otherwise None."""
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Close button
            if self.close_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "done"
            
            # Volume slider — start dragging if clicked on knob or track
            knob = self._knob_rect()
            if knob.collidepoint(event.pos) or self.slider_track.collidepoint(event.pos):
                self.dragging_slider = True
                self._update_slider_from_mouse(event.pos[0])
                return None
            
            # Face upload boxes
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
            
            # Remove buttons
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
        
        # Dragging the slider knob
        if event.type == pygame.MOUSEMOTION and self.dragging_slider:
            self._update_slider_from_mouse(event.pos[0])
            return None
        
        # Release the slider knob
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_slider:
                self.dragging_slider = False
                return None
        
        # Escape key closes the settings
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "done"
        
        return None
    
    def _update_slider_from_mouse(self, mouse_x):
        """Recalculate volume from mouse X position on the slider track."""
        rel = mouse_x - self.slider_track.x
        self.volume = max(0.0, min(1.0, rel / self.slider_track.width))
        # Apply volume immediately
        if self.audio_manager:
            self.audio_manager.set_music_volume(self.volume)
    
    def draw(self, screen, video_frame=None, bg_image=None):
        """Draw the settings popup over the darkened background.
        video_frame: the current looping video frame (preferred).
        bg_image: static fallback background."""
        
        # Draw the background (video or static)
        if video_frame is not None:
            screen.blit(video_frame, (0, 0))
        elif bg_image is not None:
            screen.blit(bg_image, (0, 0))
        
        # Dark overlay to dim the background
        screen.blit(self._overlay, (0, 0))
        
        # Panel card
        pygame.draw.rect(screen, (35, 30, 25), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (180, 140, 60), self.panel_rect, 3, border_radius=16)
        
        # Title
        title = self.font_large.render("SETTINGS", True, (255, 210, 80))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 16))
        
        mouse = pygame.mouse.get_pos()
        
        # ── Close (X) button ──
        hover_close = self.close_rect.collidepoint(mouse)
        close_color = (200, 60, 60) if hover_close else (120, 50, 50)
        pygame.draw.rect(screen, close_color, self.close_rect, border_radius=6)
        pygame.draw.rect(screen, (220, 180, 180), self.close_rect, 2, border_radius=6)
        x_text = self._font_btn.render("X", True, (255, 255, 255))
        screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))
        
        # ── Volume Slider ──
        vol_label = self._font_section.render("Background Volume", True, (220, 200, 160))
        screen.blit(vol_label, vol_label.get_rect(centerx=SCREEN_W//2, bottom=self.slider_track.y - 8))
        
        # Track background (dark bar)
        pygame.draw.rect(screen, (60, 55, 45), self.slider_track, border_radius=4)
        # Filled portion (golden)
        filled_w = int(self.volume * self.slider_track.width)
        if filled_w > 0:
            filled_rect = pygame.Rect(self.slider_track.x, self.slider_track.y, filled_w, self.slider_track.height)
            pygame.draw.rect(screen, (220, 180, 60), filled_rect, border_radius=4)
        # Knob
        kx = self._get_knob_x()
        ky = self.slider_track.centery
        knob_color = (255, 220, 100) if self.dragging_slider else (200, 170, 80)
        pygame.draw.circle(screen, knob_color, (kx, ky), self.slider_knob_radius)
        pygame.draw.circle(screen, (255, 240, 180), (kx, ky), self.slider_knob_radius, 2)
        
        # Volume percentage text
        vol_pct = self._font_small.render(f"{int(self.volume * 100)}%", True, (180, 170, 150))
        screen.blit(vol_pct, vol_pct.get_rect(centerx=SCREEN_W//2, top=self.slider_track.bottom + 6))
        
        # ── Drop Faces section title ──
        faces_title_y = self.slider_track.bottom + 32
        df_title = self._font_section.render("Drop Faces", True, (255, 210, 80))
        screen.blit(df_title, df_title.get_rect(centerx=SCREEN_W//2, y=faces_title_y))
        
        sub = self._font_small.render("Click a box to select a custom face image", True, (180, 170, 150))
        screen.blit(sub, sub.get_rect(centerx=SCREEN_W//2, y=faces_title_y + 28))
        
        # ── Player face zones ──
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
        
        # ── Head size +/- controls ──
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


class OnlineMenu:
    """Popup overlay that shows a 'coming soon' message when the player clicks Online.
    Has a dark background overlay and a close (X) button to return to the main menu."""
    
    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Centered panel
        pw, ph = 500, 260
        self.panel_rect = pygame.Rect(SCREEN_W//2 - pw//2, SCREEN_H//2 - ph//2, pw, ph)
        px, py = self.panel_rect.x, self.panel_rect.y
        
        # Close (X) button — top right corner
        close_size = 32
        self.close_rect = pygame.Rect(px + pw - close_size - 10, py + 10, close_size, close_size)
        
        # Pre-build the dark overlay
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 180))
        
        self._font_btn = pygame.font.Font(None, 28)
        self._font_msg = pygame.font.Font(None, 38)
        
        # ============================================================
        # CHANGE THIS TEXT to update the Online popup description.
        # Just edit the string below to whatever you want it to say.
        # ============================================================
        self.message = "the online is coming soon"
    
    def handle_event(self, event) -> str:
        """Returns 'done' when close is clicked, otherwise None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "done"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "done"
        return None
    
    def draw(self, screen, video_frame=None, bg_image=None):
        """Draw the Online popup over the darkened background."""
        # Draw the background (video or static)
        if video_frame is not None:
            screen.blit(video_frame, (0, 0))
        elif bg_image is not None:
            screen.blit(bg_image, (0, 0))
        
        # Dark overlay
        screen.blit(self._overlay, (0, 0))
        
        # Panel card
        pygame.draw.rect(screen, (30, 30, 45), self.panel_rect, border_radius=16)
        pygame.draw.rect(screen, (80, 120, 200), self.panel_rect, 3, border_radius=16)
        
        # Title
        title = self.font_large.render("ONLINE", True, (100, 180, 255))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 20))
        
        mouse = pygame.mouse.get_pos()
        
        # Close (X) button
        hover_close = self.close_rect.collidepoint(mouse)
        close_color = (200, 60, 60) if hover_close else (120, 50, 50)
        pygame.draw.rect(screen, close_color, self.close_rect, border_radius=6)
        pygame.draw.rect(screen, (220, 180, 180), self.close_rect, 2, border_radius=6)
        x_text = self._font_btn.render("X", True, (255, 255, 255))
        screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))
        
        # Message text — centered in the panel
        msg = self._font_msg.render(self.message, True, (220, 220, 240))
        screen.blit(msg, msg.get_rect(center=self.panel_rect.center))


# Legacy alias so existing imports don't break
DropFacesMenu = SettingsMenu
