# src/menu.py — All menu screens: main menu, pause menu, game over menu, and settings.
# Supports both mouse and gamepad (D-Pad navigation, A/X/Y button actions).

import pygame
import os
from src.constants import (
    SCREEN_W, SCREEN_H,
    JOY_BTN_A, JOY_BTN_B, JOY_BTN_X, JOY_BTN_Y,
    JOY_BTN_L1, JOY_BTN_R1, JOY_AXIS_L2, JOY_AXIS_R2,
    JOY_TRIGGER_THRESHOLD
)
class MainMenu:
    """Title screen with Play, Head War, Online, Settings, and Exit buttons.
    Background is a video frame passed in each draw call instead of a static image.
    Buttons use custom PNG images with normal/hover states for an animated feel."""
    
    def __init__(self, bg_image, font_large, font_medium):
        self.bg = bg_image  # fallback static image when video is unavailable
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Controller navigation state
        self.selected_index = -1  # -1 = no controller selection active
        self._button_names = ["play", "head_war", "online", "settings", "exit"]
        self._button_count = 5
        self._last_hover_index = -1  # tracks last hovered button for hover sound
        
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
        """Check if a menu button was clicked or selected via controller. Returns the button name or None."""
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.selected_index = -1  # reset controller highlight on mouse click
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
        
        # Controller D-Pad navigation
        if event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            old_index = self.selected_index
            if hat_y == -1:  # D-Pad Down
                if self.selected_index < 0:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index + 1) % self._button_count
            elif hat_y == 1:  # D-Pad Up
                if self.selected_index < 0:
                    self.selected_index = self._button_count - 1
                else:
                    self.selected_index = (self.selected_index - 1) % self._button_count
            # Play hover sound when controller selection changes
            if self.selected_index != old_index and self.selected_index >= 0:
                self._last_hover_index = self.selected_index
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_hover")
        
        # Controller A button — confirm selection
        if event.type == pygame.JOYBUTTONDOWN and event.button == JOY_BTN_A:
            if self.selected_index >= 0:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return self._button_names[self.selected_index]
        
        return None
    
    def draw(self, screen, video_frame=None):
        # Draw the video frame if available, otherwise fall back to the static bg image
        if video_frame is not None:
            screen.blit(video_frame, (0, 0))
        else:
            screen.blit(self.bg, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Build button list for index-based controller highlighting
        all_buttons = [
            (self.play_rect, self.play_imgs, self.play_scale_normal, self.play_scale_hover,
             "PLAY", (80, 200, 80), (50, 150, 50), (255, 255, 255), 3),
            (self.headwar_rect, self.headwar_imgs, self.headwar_scale_normal, self.headwar_scale_hover,
             "HEAD WAR", (220, 90, 40), (180, 60, 25), (255, 200, 100), 3),
            (self.online_rect, self.online_imgs, self.online_scale_normal, self.online_scale_hover,
             "ONLINE", (60, 120, 220), (40, 80, 170), (150, 200, 255), 3),
            (self.settings_rect, self.settings_imgs, self.settings_scale_normal, self.settings_scale_hover,
             "SETTINGS", (185, 145, 65), (148, 108, 42), (255, 220, 150), 2),
            (self.exit_rect, self.exit_imgs, self.exit_scale_normal, self.exit_scale_hover,
             "EXIT", (180, 50, 50), (140, 35, 35), (255, 150, 150), 2),
        ]
        
        # Detect mouse hover changes and play hover sound once per focus change
        current_mouse_hover = -1
        for i, (rect, *_rest) in enumerate(all_buttons):
            if rect.collidepoint(mouse_pos):
                current_mouse_hover = i
                break
        if current_mouse_hover != self._last_hover_index and current_mouse_hover >= 0:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_hover")
        self._last_hover_index = current_mouse_hover if current_mouse_hover >= 0 else self._last_hover_index
        
        for i, (rect, imgs, sn, sh, fb, hc, nc, bc, bw) in enumerate(all_buttons):
            ctrl_hover = (i == self.selected_index)
            self._draw_button(screen, mouse_pos, rect, imgs, sn, sh, fb, hc, nc, bc, bw, ctrl_hover)
    
    def _draw_button(self, screen, mouse_pos, rect, imgs, scale_normal, scale_hover,
                     fallback_text, hover_color, normal_color, border_color, border_width,
                     controller_hover=False):
        """Draw a single menu button. Uses custom images if available, falls back to colored rect.
        Images are scaled from the RAW original and drawn CENTER-ANCHORED to the rect.
        controller_hover=True forces the hover state (for D-Pad selection)."""
        hovering = rect.collidepoint(mouse_pos) or controller_hover
        
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
    """Overlay that appears when the game is paused. Has Continue, Start New, and Exit buttons.
    Supports custom background image and custom button images with hover states.
    All elements support manual X/Y offset and scale multipliers."""
    
    def __init__(self, font):
        self.font = font
        self.audio_manager = None
        
        # Controller navigation state
        self.selected_index = -1  # -1 = no controller selection active
        self._button_names = ["continue", "new", "exit"]
        self._button_count = 3
        self._last_hover_index = -1  # tracks last hovered button for hover sound
        
        # ================================================================
        # POSITION OFFSETS — shift elements from their default positions.
        # Positive X = right, Negative X = left.
        # Positive Y = down,  Negative Y = up.
        # ================================================================
        self.bg_offset_x         = 0
        self.bg_offset_y         = 0
        self.continue_offset_x   = 0
        self.continue_offset_y   = -38
        self.new_offset_x        = 0
        self.new_offset_y        = -15
        self.pause_exit_offset_x = 0
        self.pause_exit_offset_y = 4
        # ================================================================
        
        # ================================================================
        # SIZE MULTIPLIERS — scale images up/down from raw full-res.
        # 1.0 = default size. Quality is always crisp.
        # ================================================================
        self.bg_scale               = 1.4
        self.continue_scale_normal  = 1.34
        self.continue_scale_hover   = 1.29
        self.new_scale_normal       = 1.5
        self.new_scale_normal       = 1.4
        self.new_scale_hover        = 1.35
        self.pause_exit_scale_normal = 1.21
        self.pause_exit_scale_hover  = 1.16
        # ================================================================
        
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
        
        # Pre-build dark overlay
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 160))
        
        # ── Load custom images (raw full-res for crisp scaling) ──
        self._raw_bg = self._try_load_raw("assets/ui/pause_bg.png")
        self._raw_continue = self._try_load_raw("assets/ui/buttons/continue.png")
        self._raw_continue_hover = self._try_load_raw("assets/ui/buttons/continue_hover.png")
        self._raw_new = self._try_load_raw("assets/ui/buttons/start_new.png")
        self._raw_new_hover = self._try_load_raw("assets/ui/buttons/start_new_hover.png")
        self._raw_exit = self._try_load_raw("assets/ui/buttons/pause_exit.png")
        self._raw_exit_hover = self._try_load_raw("assets/ui/buttons/pause_exit_hover.png")
    
    def _try_load_raw(self, path):
        """Load an image at full resolution. Returns None if file is missing."""
        try:
            if os.path.isfile(path):
                return pygame.image.load(path).convert_alpha()
        except Exception:
            pass
        return None
    
    def _scale_raw(self, raw_surface, target_w, target_h, multiplier):
        """Scale a raw full-res image to (target_w * multiplier, target_h * multiplier).
        Always scales from the ORIGINAL for maximum quality."""
        final_w = max(1, int(target_w * multiplier))
        final_h = max(1, int(target_h * multiplier))
        return pygame.transform.smoothscale(raw_surface, (final_w, final_h))
    
    def handle_event(self, event) -> str:
        """Returns which button was clicked, or None. Escape also counts as 'continue'."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.selected_index = -1
            # Check with offsets applied
            cont_rect = self.btn_continue.move(self.continue_offset_x, self.continue_offset_y)
            new_rect = self.btn_new.move(self.new_offset_x, self.new_offset_y)
            exit_rect = self.btn_exit.move(self.pause_exit_offset_x, self.pause_exit_offset_y)
            
            if cont_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "continue"
            if new_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "new"
            if exit_rect.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "exit"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_click")
            return "continue"
        
        # Controller D-Pad navigation
        if event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            old_index = self.selected_index
            if hat_y == -1:  # D-Pad Down
                if self.selected_index < 0:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index + 1) % self._button_count
            elif hat_y == 1:  # D-Pad Up
                if self.selected_index < 0:
                    self.selected_index = self._button_count - 1
                else:
                    self.selected_index = (self.selected_index - 1) % self._button_count
            # Play hover sound when controller selection changes
            if self.selected_index != old_index and self.selected_index >= 0:
                self._last_hover_index = self.selected_index
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_hover")
        
        # Controller A button — confirm selection
        if event.type == pygame.JOYBUTTONDOWN and event.button == JOY_BTN_A:
            if self.selected_index >= 0:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return self._button_names[self.selected_index]
        
        return None
    
    def _draw_custom_button(self, screen, mouse, rect, raw_normal, raw_hover,
                            scale_normal, scale_hover, ox, oy, fallback_label,
                            controller_hover=False):
        """Draw a single pause menu button with custom images or colored fallback.
        controller_hover=True forces the hover state for D-Pad selection."""
        shifted = rect.move(ox, oy)
        hovering = shifted.collidepoint(mouse) or controller_hover
        
        if raw_normal is not None and raw_hover is not None:
            raw = raw_hover if hovering else raw_normal
            scale = scale_hover if hovering else scale_normal
            surf = self._scale_raw(raw, rect.width, rect.height, scale)
            screen.blit(surf, surf.get_rect(center=shifted.center))
        else:
            color = (70, 130, 200) if hovering else (45, 90, 150)
            pygame.draw.rect(screen, color, shifted, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 220), shifted, 2, border_radius=10)
            text = self.font.render(fallback_label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=shifted.center))
    
    def draw(self, screen):
        # Dark semi-transparent backdrop
        screen.blit(self._overlay, (0, 0))
        
        mouse = pygame.mouse.get_pos()
        
        # Mouse hover sound for pause menu buttons
        pause_btn_rects = [
            self.btn_continue.move(self.continue_offset_x, self.continue_offset_y),
            self.btn_new.move(self.new_offset_x, self.new_offset_y),
            self.btn_exit.move(self.pause_exit_offset_x, self.pause_exit_offset_y),
        ]
        current_mouse_hover = -1
        for i, r in enumerate(pause_btn_rects):
            if r.collidepoint(mouse):
                current_mouse_hover = i
                break
        if current_mouse_hover != self._last_hover_index and current_mouse_hover >= 0:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_hover")
        self._last_hover_index = current_mouse_hover if current_mouse_hover >= 0 else self._last_hover_index
        
        # ── Custom background image or fallback panel ──
        if self._raw_bg is not None:
            bg_surf = self._scale_raw(self._raw_bg, self.panel_rect.width, self.panel_rect.height, self.bg_scale)
            bg_draw = bg_surf.get_rect(center=(
                self.panel_rect.centerx + self.bg_offset_x,
                self.panel_rect.centery + self.bg_offset_y
            ))
            screen.blit(bg_surf, bg_draw)
        else:
            pygame.draw.rect(screen, (30, 30, 40), self.panel_rect, border_radius=16)
            pygame.draw.rect(screen, (100, 100, 120), self.panel_rect, 3, border_radius=16)
            title = self.font.render("PAUSED", True, (255, 220, 60))
            screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=self.panel_rect.y + 24))
        
        # ── Buttons (with controller highlight support) ──
        self._draw_custom_button(screen, mouse, self.btn_continue,
                                 self._raw_continue, self._raw_continue_hover,
                                 self.continue_scale_normal, self.continue_scale_hover,
                                 self.continue_offset_x, self.continue_offset_y, "Continue",
                                 controller_hover=(self.selected_index == 0))
        self._draw_custom_button(screen, mouse, self.btn_new,
                                 self._raw_new, self._raw_new_hover,
                                 self.new_scale_normal, self.new_scale_hover,
                                 self.new_offset_x, self.new_offset_y, "Start New",
                                 controller_hover=(self.selected_index == 1))
        self._draw_custom_button(screen, mouse, self.btn_exit,
                                 self._raw_exit, self._raw_exit_hover,
                                 self.pause_exit_scale_normal, self.pause_exit_scale_hover,
                                 self.pause_exit_offset_x, self.pause_exit_offset_y, "Exit",
                                 controller_hover=(self.selected_index == 2))


class GameOverMenu:
    """Shows custom game over screen with configurable images for background,
    Play Again, and Main Menu buttons. All elements support manual positioning and scaling."""

    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # Controller navigation state
        self.selected_index = -1  # -1 = no controller selection active
        self._button_names = ["new", "exit"]
        self._button_count = 2
        self._last_hover_index = -1  # tracks last hovered button for hover sound
        
        # ================================================================
        # ██  GAME OVER — MASTER CONFIGURATION HUB  ██
        # ================================================================
        
        # ── POSITION OFFSETS ──
        self.bg_offset_x           = 0
        self.bg_offset_y           = 0
        self.btn_new_offset_x      = 0     # Play Again button
        self.btn_new_offset_y      = -40
        self.btn_exit_offset_x     = 0     # Main Menu button
        self.btn_exit_offset_y     = -20
        
        # ── SIZE MULTIPLIERS ──
        self.bg_scale              = 0.1
        self.btn_new_scale_normal  = 0.17
        self.btn_new_scale_hover   = 0.16
        self.btn_exit_scale_normal = 0.17
        self.btn_exit_scale_hover  = 0.16
        
        # ================================================================
        # ██  END OF CONFIGURATION HUB  ██
        # ================================================================
        
        w, h = 400, 380
        self.panel_rect = pygame.Rect(SCREEN_W//2 - w//2, SCREEN_H//2 - h//2, w, h)

        bw, bh = 280, 60
        cx = SCREEN_W // 2 - bw // 2
        base_y = self.panel_rect.y + 150
        gap = 72
        self.btn_new = pygame.Rect(cx, base_y, bw, bh)
        self.btn_exit = pygame.Rect(cx, base_y + gap, bw, bh)
        self._base_btn_w = bw
        self._base_btn_h = bh
        
        # Pre-build the dark overlay
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 180))
        
        # ── Load custom images (raw full-res for crisp scaling) ──
        self._raw_bg = self._try_load_raw("assets/ui/game_over_bg.png")
        self._raw_btn_new = self._try_load_raw("assets/ui/buttons/btn_play_again.png")
        self._raw_btn_new_hover = self._try_load_raw("assets/ui/buttons/btn_play_again_hover.png")
        self._raw_btn_exit = self._try_load_raw("assets/ui/buttons/btn_main_menu.png")
        self._raw_btn_exit_hover = self._try_load_raw("assets/ui/buttons/btn_main_menu_hover.png")
    
    def _try_load_raw(self, path):
        """Load an image at full resolution. Returns None if file is missing."""
        try:
            if os.path.isfile(path):
                return pygame.image.load(path).convert_alpha()
        except Exception:
            pass
        return None
    
    def _scale_raw(self, raw_surface, target_w, target_h, multiplier):
        """Scale a raw full-res image to (target_w * multiplier, target_h * multiplier).
        Always scales from the ORIGINAL for maximum quality."""
        final_w = max(1, int(target_w * multiplier))
        final_h = max(1, int(target_h * multiplier))
        return pygame.transform.smoothscale(raw_surface, (final_w, final_h))
    
    def _get_btn_rect(self, base_rect, scale, ox, oy, raw_img=None):
        """Return a scaled + offset button rect centered on the original.
        If raw_img is provided, uses its actual dimensions for pixel-perfect hitboxes."""
        if raw_img is not None:
            rw, rh = raw_img.get_size()
            sw = max(1, int(rw * scale))
            sh = max(1, int(rh * scale))
        else:
            sw = max(1, int(self._base_btn_w * scale))
            sh = max(1, int(self._base_btn_h * scale))
        cx = base_rect.centerx + ox
        cy = base_rect.centery + oy
        return pygame.Rect(cx - sw//2, cy - sh//2, sw, sh)

    def handle_event(self, event) -> str:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.selected_index = -1
            mouse = pygame.mouse.get_pos()
            # Use actual image dimensions for hit detection
            hit_new = self._get_btn_rect(self.btn_new, self.btn_new_scale_normal,
                                          self.btn_new_offset_x, self.btn_new_offset_y,
                                          raw_img=self._raw_btn_new)
            if hit_new.collidepoint(mouse):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "new"
            hit_exit = self._get_btn_rect(self.btn_exit, self.btn_exit_scale_normal,
                                           self.btn_exit_offset_x, self.btn_exit_offset_y,
                                           raw_img=self._raw_btn_exit)
            if hit_exit.collidepoint(mouse):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "exit"
        
        # Controller D-Pad navigation
        if event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            old_index = self.selected_index
            if hat_y == -1:  # D-Pad Down
                if self.selected_index < 0:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index + 1) % self._button_count
            elif hat_y == 1:  # D-Pad Up
                if self.selected_index < 0:
                    self.selected_index = self._button_count - 1
                else:
                    self.selected_index = (self.selected_index - 1) % self._button_count
            # Play hover sound when controller selection changes
            if self.selected_index != old_index and self.selected_index >= 0:
                self._last_hover_index = self.selected_index
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_hover")
        
        # Controller A button — confirm selection
        if event.type == pygame.JOYBUTTONDOWN and event.button == JOY_BTN_A:
            if self.selected_index >= 0:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return self._button_names[self.selected_index]
        
        return None

    def draw(self, screen, winner_name):
        mouse = pygame.mouse.get_pos()
        
        # Mouse hover sound for game over buttons
        go_btn_rects = [
            self._get_btn_rect(self.btn_new, self.btn_new_scale_normal,
                               self.btn_new_offset_x, self.btn_new_offset_y,
                               raw_img=self._raw_btn_new),
            self._get_btn_rect(self.btn_exit, self.btn_exit_scale_normal,
                               self.btn_exit_offset_x, self.btn_exit_offset_y,
                               raw_img=self._raw_btn_exit),
        ]
        current_mouse_hover = -1
        for i, r in enumerate(go_btn_rects):
            if r.collidepoint(mouse):
                current_mouse_hover = i
                break
        if current_mouse_hover != self._last_hover_index and current_mouse_hover >= 0:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_hover")
        self._last_hover_index = current_mouse_hover if current_mouse_hover >= 0 else self._last_hover_index
        
        # Dark backdrop
        screen.blit(self._overlay, (0, 0))
        
        # Background — custom image or fallback panel
        if self._raw_bg is not None:
            raw_w, raw_h = self._raw_bg.get_size()
            bg_surf = self._scale_raw(self._raw_bg, raw_w, raw_h, self.bg_scale)
            bg_cx = SCREEN_W // 2 + self.bg_offset_x
            bg_cy = SCREEN_H // 2 + self.bg_offset_y
            screen.blit(bg_surf, bg_surf.get_rect(center=(bg_cx, bg_cy)))
        else:
            pygame.draw.rect(screen, (40, 30, 30), self.panel_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 100, 100), self.panel_rect, 3, border_radius=16)
        
        # Buttons — custom images or fallback drawn rectangles
        for base_rect, raw_normal, raw_hover, label, scale_n, scale_h, ox, oy in [
            (self.btn_new, self._raw_btn_new, self._raw_btn_new_hover, "Play Again",
             self.btn_new_scale_normal, self.btn_new_scale_hover,
             self.btn_new_offset_x, self.btn_new_offset_y),
            (self.btn_exit, self._raw_btn_exit, self._raw_btn_exit_hover, "Main Menu",
             self.btn_exit_scale_normal, self.btn_exit_scale_hover,
             self.btn_exit_offset_x, self.btn_exit_offset_y),
        ]:
            # Hitbox uses actual image dimensions when custom PNG exists
            hit_rect = self._get_btn_rect(base_rect, scale_n, ox, oy, raw_img=raw_normal)
            btn_idx = 0 if base_rect is self.btn_new else 1
            is_hover = hit_rect.collidepoint(mouse) or (btn_idx == self.selected_index)
            
            if raw_normal is not None:
                raw_img = raw_hover if (is_hover and raw_hover is not None) else raw_normal
                scale = scale_h if is_hover else scale_n
                rw, rh = raw_img.get_size()
                btn_surf = self._scale_raw(raw_img, rw, rh, scale)
                btn_cx = base_rect.centerx + ox
                btn_cy = base_rect.centery + oy
                screen.blit(btn_surf, btn_surf.get_rect(center=(btn_cx, btn_cy)))
            else:
                draw_rect = self._get_btn_rect(base_rect, scale_h if is_hover else scale_n, ox, oy)
                color = (200, 70, 70) if is_hover else (150, 45, 45)
                pygame.draw.rect(screen, color, draw_rect, border_radius=10)
                pygame.draw.rect(screen, (220, 200, 200), draw_rect, 2, border_radius=10)
                text = self.font_medium.render(label, True, (255, 255, 255))
                screen.blit(text, text.get_rect(center=draw_rect.center))


class SettingsMenu:
    """Settings popup that overlays the menu. Contains:
    1. A custom background image (or fallback panel)
    2. A custom close (X) button with hover image
    3. A Music volume slider (light brown)
    4. An SFX volume slider (light brown)
    5. The Drop Faces interface (face upload boxes + head size controls)
    All elements support manual X/Y offset and scale multipliers."""
    
    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # ================================================================
        # ██  SETTINGS MENU — MASTER CONFIGURATION HUB  ██
        # All positioning and sizing controls in ONE place.
        # ================================================================
        
        # ── POSITION OFFSETS ──
        # Shift elements from their default positions.
        # Positive X = right, Negative X = left.
        # Positive Y = down,  Negative Y = up.
        self.bg_offset_x           = 0
        self.bg_offset_y           = 0
        self.close_offset_x        = -25
        self.close_offset_y        = 21
        self.music_bar_offset_x    = 17
        self.music_bar_offset_y    = 40
        self.sfx_bar_offset_x      = 17
        self.sfx_bar_offset_y      = 40
        self.p1_faces_offset_x     = 55
        self.p1_faces_offset_y     = 60
        self.p2_faces_offset_x     = -55
        self.p2_faces_offset_y     = 60
        self.p1_controls_offset_x  = -3    # The [- 1.0x +] below LEFT face box
        self.p1_controls_offset_y  = -20
        self.p2_controls_offset_x  = 0    # The [- 1.0x +] below RIGHT face box
        self.p2_controls_offset_y  = -20
        self.mute_music_offset_x   = 40    # Mute button left of music bar
        self.mute_music_offset_y   = 0
        self.mute_sfx_offset_x     = 40    # Mute button left of SFX bar
        self.mute_sfx_offset_y     = 0
        self.face_board_offset_x   = 0    # Drop Faces image board
        self.face_board_offset_y   = 25
        self.left_right_txt_offset_x = 1  # "LEFT"/"RIGHT" labels
        self.left_right_txt_offset_y = 0
        self.math_txt_offset_x     = -0.4    # The -, 1.0x, + text symbols
        self.math_txt_offset_y     = -2.5
        self.plus_icon_offset_x    = -1    # Big "+" inside empty face slots
        self.plus_icon_offset_y    = -4
        self.face_remove_offset_x  = 0
        self.face_remove_offset_y  = 0
        
        # ── SIZE MULTIPLIERS ──
        # Scale elements up/down. 1.0 = default size.
        # Images are always scaled from the raw full-res original (never blurry).
        self.bg_scale              = 1.0
        self.close_scale_normal    = 0.95
        self.close_scale_hover     = 0.89
        self.music_bar_scale       = 0.8  # Scales the slider track width/height + knob
        self.sfx_bar_scale         = 0.8  # Scales the slider track width/height + knob
        self.p1_box_scale          = 1.3  # Scales the LEFT drop-face box
        self.p2_box_scale          = 1.3  # Scales the RIGHT drop-face box
        self.p1_controls_scale     = 1.0  # Scales the [- 1.0x +] buttons for LEFT
        self.p2_controls_scale     = 1.0  # Scales the [- 1.0x +] buttons for RIGHT
        self.mute_music_scale      = 1.0  # Mute music button size
        self.mute_sfx_scale        = 1.0  # Mute SFX button size
        self.face_board_scale      = 0.07  # Drop Faces image board size
        self.left_right_txt_scale  = 0.7  # "LEFT"/"RIGHT" text size
        self.math_txt_scale        = 1.0  # -, 1.0x, + text size
        self.plus_icon_scale       = 1.0  # Big "+" inside empty face slots
        self.face_remove_scale_normal = 0.8
        self.face_remove_scale_hover  = 0.75
        self.p1_custom_face_base_scale = 2.5  # Default base size of P1 custom face PNG
        self.p2_custom_face_base_scale = 2.5  # Default base size of P2 custom face PNG
        
        # ================================================================
        # ██  END OF CONFIGURATION HUB  ██
        # ================================================================
        
        # Main panel centered on screen — taller to fit settings, SFX bar, and drop faces
        pw, ph = 620, 560
        self.panel_rect = pygame.Rect(SCREEN_W//2 - pw//2, SCREEN_H//2 - ph//2, pw, ph)
        px, py = self.panel_rect.x, self.panel_rect.y
        
        # Close (X) button — top right corner of panel
        close_size = 32
        self.close_rect = pygame.Rect(px + pw - close_size - 10, py + 10, close_size, close_size)
        
        # ── Base slider dimensions (will be multiplied by scale at draw time) ──
        self._base_slider_w = 360
        self._base_slider_h = 8
        self._base_knob_radius = 10
        music_slider_y = py + 80
        self.music_slider_track = pygame.Rect(SCREEN_W//2 - self._base_slider_w//2, music_slider_y, self._base_slider_w, self._base_slider_h)
        self.music_volume = 1.0
        self.dragging_music = False
        
        sfx_slider_y = music_slider_y + 70
        self.sfx_slider_track = pygame.Rect(SCREEN_W//2 - self._base_slider_w//2, sfx_slider_y, self._base_slider_w, self._base_slider_h)
        self.sfx_volume = 1.0
        self.dragging_sfx = False
        
        # ── Mute toggle state ──
        self._music_muted = False
        self._music_vol_before_mute = 1.0
        self._sfx_muted = False
        self._sfx_vol_before_mute = 1.0
        self._base_mute_size = 28  # Base clickable size for mute buttons
        self.mute_music_rect = pygame.Rect(self.music_slider_track.x - 40, music_slider_y - 10, self._base_mute_size, self._base_mute_size)
        self.mute_sfx_rect = pygame.Rect(self.sfx_slider_track.x - 40, sfx_slider_y - 10, self._base_mute_size, self._base_mute_size)
        
        # ── Base Drop Faces dimensions (will be multiplied by scale at draw time) ──
        faces_top = sfx_slider_y + 60
        self._base_box_size = 100
        box_y = faces_top + 50
        
        p1_cx = px + pw//4
        self.p1_box = pygame.Rect(p1_cx - self._base_box_size//2, box_y, self._base_box_size, self._base_box_size)
        
        # Base head size +/- button dimensions
        self._base_ctrl_w, self._base_ctrl_h = 28, 28
        size_y = box_y + self._base_box_size + 48
        self.p1_minus = pygame.Rect(p1_cx - 48, size_y, self._base_ctrl_w, self._base_ctrl_h)
        self.p1_plus = pygame.Rect(p1_cx + 20, size_y, self._base_ctrl_w, self._base_ctrl_h)
        
        p2_cx = px + 3*pw//4
        self.p2_box = pygame.Rect(p2_cx - self._base_box_size//2, box_y, self._base_box_size, self._base_box_size)
        self.p2_minus = pygame.Rect(p2_cx - 48, size_y, self._base_ctrl_w, self._base_ctrl_h)
        self.p2_plus = pygame.Rect(p2_cx + 20, size_y, self._base_ctrl_w, self._base_ctrl_h)
        
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
        
        # ── Load custom images (raw full-res for crisp scaling) ──
        self._raw_bg = self._try_load_raw("assets/ui/settings_bg.png")
        self._raw_close = self._try_load_raw("assets/ui/close.png")
        self._raw_close_hover = self._try_load_raw("assets/ui/close_hover.png")
        self._raw_mute_music = self._try_load_raw("assets/ui/buttons/mute_music.png")
        self._raw_mute_music_muted = self._try_load_raw("assets/ui/buttons/mute_music_muted.png")
        self._raw_mute_sfx = self._try_load_raw("assets/ui/buttons/mute_sfx.png")
        self._raw_mute_sfx_muted = self._try_load_raw("assets/ui/buttons/mute_sfx_muted.png")
        self._raw_face_board = self._try_load_raw("assets/ui/drop_faces_board.png")
        
        # ── Controller hold-button state tracking ──
        # These track whether specific buttons are currently HELD (for combo actions)
        self._joy_a_held  = False  # Hold A  + D-Pad = adjust SFX volume
        self._joy_y_held  = False  # Hold Y  + D-Pad = adjust Music volume
        self._joy_l1_held = False  # Hold L1 + D-Pad = adjust left face size (if face imported)
        self._joy_r1_held = False  # Hold R1 + D-Pad = adjust right face size (if face imported)
        self._vol_step    = 0.05   # volume change per D-Pad press
    
    def _try_load_raw(self, path):
        """Load an image at full resolution. Returns None if file is missing."""
        try:
            if os.path.isfile(path):
                return pygame.image.load(path).convert_alpha()
        except Exception:
            pass
        return None
    
    def _scale_raw(self, raw_surface, target_w, target_h, multiplier):
        """Scale a raw full-res image to (target_w * multiplier, target_h * multiplier).
        Always scales from the ORIGINAL for maximum quality."""
        final_w = max(1, int(target_w * multiplier))
        final_h = max(1, int(target_h * multiplier))
        return pygame.transform.smoothscale(raw_surface, (final_w, final_h))
    
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
                # Return the raw full-resolution image — all scaling
                # happens at draw time for maximum quality.
                return img
        except Exception:
            pass
        return None
    
    def _get_scaled_slider(self, track, scale, ox, oy):
        """Return a scaled + offset slider track rect and knob radius."""
        sw = max(1, int(self._base_slider_w * scale))
        sh = max(1, int(self._base_slider_h * scale))
        kr = max(3, int(self._base_knob_radius * scale))
        cx = track.centerx + ox
        cy = track.centery + oy
        r = pygame.Rect(cx - sw//2, cy - sh//2, sw, sh)
        return r, kr
    
    def _get_scaled_box(self, box, scale, ox, oy):
        """Return a scaled + offset face box rect, centered on the original position."""
        sz = max(1, int(self._base_box_size * scale))
        cx = box.centerx + ox
        cy = box.centery + oy
        return pygame.Rect(cx - sz//2, cy - sz//2, sz, sz)
    
    def _get_scaled_ctrl(self, minus_r, plus_r, ctrl_scale, ox, oy):
        """Return scaled + offset minus/plus button rects."""
        cw = max(1, int(self._base_ctrl_w * ctrl_scale))
        ch = max(1, int(self._base_ctrl_h * ctrl_scale))
        m_cx = minus_r.centerx + ox
        m_cy = minus_r.centery + oy
        p_cx = plus_r.centerx + ox
        p_cy = plus_r.centery + oy
        sm = pygame.Rect(m_cx - cw//2, m_cy - ch//2, cw, ch)
        sp = pygame.Rect(p_cx - cw//2, p_cy - ch//2, cw, ch)
        return sm, sp
    
    def _get_scaled_mute(self, mute_rect, scale, ox, oy):
        """Return a scaled + offset mute button rect."""
        sz = max(1, int(self._base_mute_size * scale))
        cx = mute_rect.centerx + ox
        cy = mute_rect.centery + oy
        return pygame.Rect(cx - sz//2, cy - sz//2, sz, sz)
    
    def _get_scaled_face_close(self, scaled_box):
        """Return the dynamic close button rect positioned at the top-right of a face box."""
        sz = max(1, int(32 * self.face_remove_scale_normal))
        cx = scaled_box.right + self.face_remove_offset_x
        cy = scaled_box.top + self.face_remove_offset_y
        return pygame.Rect(cx - sz//2, cy - sz//2, sz, sz)
    
    def handle_event(self, event) -> str:
        """Handle clicks on close button, volume sliders, face boxes, remove/size buttons.
        Returns 'done' when the player closes the panel, otherwise None."""
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Close button (with offset)
            close_hit = self.close_rect.move(self.close_offset_x, self.close_offset_y)
            if close_hit.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "done"
            
            # Mute music toggle
            mm_rect = self._get_scaled_mute(self.mute_music_rect, self.mute_music_scale,
                                             self.music_bar_offset_x + self.mute_music_offset_x,
                                             self.music_bar_offset_y + self.mute_music_offset_y)
            if mm_rect.collidepoint(event.pos):
                if self._music_muted:
                    self._music_muted = False
                    self.music_volume = self._music_vol_before_mute
                else:
                    self._music_vol_before_mute = self.music_volume
                    self._music_muted = True
                    self.music_volume = 0.0
                if self.audio_manager:
                    self.audio_manager.set_music_volume(self.music_volume)
                return None
            
            # Mute SFX toggle
            ms_rect = self._get_scaled_mute(self.mute_sfx_rect, self.mute_sfx_scale,
                                             self.sfx_bar_offset_x + self.mute_sfx_offset_x,
                                             self.sfx_bar_offset_y + self.mute_sfx_offset_y)
            if ms_rect.collidepoint(event.pos):
                if self._sfx_muted:
                    self._sfx_muted = False
                    self.sfx_volume = self._sfx_vol_before_mute
                else:
                    self._sfx_vol_before_mute = self.sfx_volume
                    self._sfx_muted = True
                    self.sfx_volume = 0.0
                if self.audio_manager:
                    self.audio_manager.set_sfx_volume(self.sfx_volume)
                return None
            
            # Music slider — use scaled track for hit detection
            m_track, m_kr = self._get_scaled_slider(self.music_slider_track, self.music_bar_scale,
                                                     self.music_bar_offset_x, self.music_bar_offset_y)
            m_knob_x = m_track.x + int(self.music_volume * m_track.width)
            m_knob_rect = pygame.Rect(m_knob_x - m_kr, m_track.centery - m_kr, m_kr*2, m_kr*2)
            if m_knob_rect.collidepoint(event.pos) or m_track.collidepoint(event.pos):
                self.dragging_music = True
                self._update_music_from_mouse(event.pos[0], m_track)
                return None
            
            # SFX slider — use scaled track for hit detection
            s_track, s_kr = self._get_scaled_slider(self.sfx_slider_track, self.sfx_bar_scale,
                                                     self.sfx_bar_offset_x, self.sfx_bar_offset_y)
            s_knob_x = s_track.x + int(self.sfx_volume * s_track.width)
            s_knob_rect = pygame.Rect(s_knob_x - s_kr, s_track.centery - s_kr, s_kr*2, s_kr*2)
            if s_knob_rect.collidepoint(event.pos) or s_track.collidepoint(event.pos):
                self.dragging_sfx = True
                self._update_sfx_from_mouse(event.pos[0], s_track)
                return None
            
            # Face upload boxes (scaled)
            p1_sbox = self._get_scaled_box(self.p1_box, self.p1_box_scale,
                                            self.p1_faces_offset_x, self.p1_faces_offset_y)
            if p1_sbox.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                face = self._open_file_dialog()
                if face is not None:
                    self.p1_face = face
                return None
            
            p2_sbox = self._get_scaled_box(self.p2_box, self.p2_box_scale,
                                            self.p2_faces_offset_x, self.p2_faces_offset_y)
            if p2_sbox.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                face = self._open_file_dialog()
                if face is not None:
                    self.p2_face = face
                return None
            
            # Remove custom faces buttons (top right of the boxes)
            p1_rm = self._get_scaled_face_close(p1_sbox)
            if p1_rm.collidepoint(event.pos) and self.p1_face is not None:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                self.p1_face = None
                return None
            
            p2_rm = self._get_scaled_face_close(p2_sbox)
            if p2_rm.collidepoint(event.pos) and self.p2_face is not None:
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                self.p2_face = None
                return None
            
            # Head size controls (scaled + offset)
            p1_sm, p1_sp = self._get_scaled_ctrl(self.p1_minus, self.p1_plus, self.p1_controls_scale,
                                                  self.p1_faces_offset_x + self.p1_controls_offset_x,
                                                  self.p1_faces_offset_y + self.p1_controls_offset_y)
            if p1_sm.collidepoint(event.pos):
                self.p1_head_base = max(0.5, round(self.p1_head_base - 0.1, 1))
                return None
            if p1_sp.collidepoint(event.pos):
                self.p1_head_base = min(6.0, round(self.p1_head_base + 0.1, 1))
                return None
            
            p2_sm, p2_sp = self._get_scaled_ctrl(self.p2_minus, self.p2_plus, self.p2_controls_scale,
                                                  self.p2_faces_offset_x + self.p2_controls_offset_x,
                                                  self.p2_faces_offset_y + self.p2_controls_offset_y)
            if p2_sm.collidepoint(event.pos):
                self.p2_head_base = max(0.5, round(self.p2_head_base - 0.1, 1))
                return None
            if p2_sp.collidepoint(event.pos):
                self.p2_head_base = min(6.0, round(self.p2_head_base + 0.1, 1))
                return None
        
        # Dragging sliders (use scaled tracks for accurate mapping)
        if event.type == pygame.MOUSEMOTION:
            if self.dragging_music:
                m_track, _ = self._get_scaled_slider(self.music_slider_track, self.music_bar_scale,
                                                     self.music_bar_offset_x, self.music_bar_offset_y)
                self._update_music_from_mouse(event.pos[0], m_track)
                return None
            if self.dragging_sfx:
                s_track, _ = self._get_scaled_slider(self.sfx_slider_track, self.sfx_bar_scale,
                                                     self.sfx_bar_offset_x, self.sfx_bar_offset_y)
                self._update_sfx_from_mouse(event.pos[0], s_track)
                return None
        
        # Release slider knobs
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_music:
                self.dragging_music = False
                return None
            if self.dragging_sfx:
                self.dragging_sfx = False
                return None
        
        # Escape key closes the settings
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "done"
        
        # ── CONTROLLER: X button closes settings ──
        if event.type == pygame.JOYBUTTONDOWN and event.button == JOY_BTN_X:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_click")
            return "done"
        
        # ── CONTROLLER: Track held buttons ──
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == JOY_BTN_A:
                self._joy_a_held = True
            elif event.button == JOY_BTN_Y:
                self._joy_y_held = True
            elif event.button == JOY_BTN_L1:
                self._joy_l1_held = True
                # Tap L1 to import left face (only if no face currently loaded)
                if self.p1_face is None:
                    if self.audio_manager:
                        self.audio_manager.play_sound("menu_click")
                    face = self._open_file_dialog()
                    if face is not None:
                        self.p1_face = face
            elif event.button == JOY_BTN_R1:
                self._joy_r1_held = True
                # Tap R1 to import right face (only if no face currently loaded)
                if self.p2_face is None:
                    if self.audio_manager:
                        self.audio_manager.play_sound("menu_click")
                    face = self._open_file_dialog()
                    if face is not None:
                        self.p2_face = face
        
        if event.type == pygame.JOYBUTTONUP:
            if event.button == JOY_BTN_A:
                self._joy_a_held = False
            elif event.button == JOY_BTN_Y:
                self._joy_y_held = False
            elif event.button == JOY_BTN_L1:
                self._joy_l1_held = False
            elif event.button == JOY_BTN_R1:
                self._joy_r1_held = False
        
        # ── CONTROLLER: L2/R2 triggers to remove faces ──
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == JOY_AXIS_L2 and event.value > JOY_TRIGGER_THRESHOLD:
                if self.p1_face is not None:
                    if self.audio_manager:
                        self.audio_manager.play_sound("menu_click")
                    self.p1_face = None
            elif event.axis == JOY_AXIS_R2 and event.value > JOY_TRIGGER_THRESHOLD:
                if self.p2_face is not None:
                    if self.audio_manager:
                        self.audio_manager.play_sound("menu_click")
                    self.p2_face = None
        
        # ── CONTROLLER: D-Pad combos while holding A/Y/L1/R1 ──
        if event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            
            # Hold A + D-Pad = adjust SFX volume / quick-mute
            if self._joy_a_held:
                if hat_x == 1:   # Right = increase SFX
                    self.sfx_volume = min(1.0, self.sfx_volume + self._vol_step)
                    self._sfx_muted = False
                    if self.audio_manager:
                        self.audio_manager.set_sfx_volume(self.sfx_volume)
                elif hat_x == -1:  # Left = decrease SFX
                    self.sfx_volume = max(0.0, self.sfx_volume - self._vol_step)
                    if self.sfx_volume <= 0:
                        self._sfx_muted = True
                    if self.audio_manager:
                        self.audio_manager.set_sfx_volume(self.sfx_volume)
                elif hat_y == -1:  # Down = quick-mute SFX
                    if self._sfx_muted:
                        self._sfx_muted = False
                        self.sfx_volume = self._sfx_vol_before_mute
                    else:
                        self._sfx_vol_before_mute = self.sfx_volume
                        self._sfx_muted = True
                        self.sfx_volume = 0.0
                    if self.audio_manager:
                        self.audio_manager.set_sfx_volume(self.sfx_volume)
                return None
            
            # Hold Y + D-Pad = adjust Music volume / quick-mute
            if self._joy_y_held:
                if hat_x == 1:   # Right = increase Music
                    self.music_volume = min(1.0, self.music_volume + self._vol_step)
                    self._music_muted = False
                    if self.audio_manager:
                        self.audio_manager.set_music_volume(self.music_volume)
                elif hat_x == -1:  # Left = decrease Music
                    self.music_volume = max(0.0, self.music_volume - self._vol_step)
                    if self.music_volume <= 0:
                        self._music_muted = True
                    if self.audio_manager:
                        self.audio_manager.set_music_volume(self.music_volume)
                elif hat_y == 1:  # Up = quick-mute Music
                    if self._music_muted:
                        self._music_muted = False
                        self.music_volume = self._music_vol_before_mute
                    else:
                        self._music_vol_before_mute = self.music_volume
                        self._music_muted = True
                        self.music_volume = 0.0
                    if self.audio_manager:
                        self.audio_manager.set_music_volume(self.music_volume)
                return None
            
            # Hold L1 + D-Pad Left/Right = adjust left face size (only when face is imported)
            if self._joy_l1_held and self.p1_face is not None:
                if hat_x == 1:   # Right = increase
                    self.p1_head_base = min(6.0, round(self.p1_head_base + 0.1, 1))
                elif hat_x == -1:  # Left = decrease
                    self.p1_head_base = max(0.5, round(self.p1_head_base - 0.1, 1))
                return None
            
            # Hold R1 + D-Pad Left/Right = adjust right face size (only when face is imported)
            if self._joy_r1_held and self.p2_face is not None:
                if hat_x == 1:   # Right = increase
                    self.p2_head_base = min(6.0, round(self.p2_head_base + 0.1, 1))
                elif hat_x == -1:  # Left = decrease
                    self.p2_head_base = max(0.5, round(self.p2_head_base - 0.1, 1))
                return None
        
        return None
    
    def _update_music_from_mouse(self, mouse_x, scaled_track):
        """Recalculate music volume from mouse X position on the scaled slider track."""
        rel = mouse_x - scaled_track.x
        self.music_volume = max(0.0, min(1.0, rel / max(1, scaled_track.width)))
        if self.audio_manager:
            self.audio_manager.set_music_volume(self.music_volume)
    
    def _update_sfx_from_mouse(self, mouse_x, scaled_track):
        """Recalculate SFX volume from mouse X position on the scaled slider track."""
        rel = mouse_x - scaled_track.x
        self.sfx_volume = max(0.0, min(1.0, rel / max(1, scaled_track.width)))
        if self.audio_manager:
            self.audio_manager.set_sfx_volume(self.sfx_volume)
    
    def _draw_slider(self, screen, track, volume, dragging, scale, ox, oy):
        """Draw a single light brown slider (no label, no percentage text)."""
        st, kr = self._get_scaled_slider(track, scale, ox, oy)
        
        # Track background (dark brown)
        pygame.draw.rect(screen, (80, 65, 45), st, border_radius=4)
        # Filled portion (light brown)
        filled_w = int(volume * st.width)
        if filled_w > 0:
            filled_rect = pygame.Rect(st.x, st.y, filled_w, st.height)
            pygame.draw.rect(screen, (195, 155, 95), filled_rect, border_radius=4)
        # Knob
        kx = st.x + int(volume * st.width)
        ky = st.centery
        knob_color = (230, 195, 130) if dragging else (195, 155, 95)
        pygame.draw.circle(screen, knob_color, (kx, ky), kr)
        pygame.draw.circle(screen, (240, 220, 180), (kx, ky), kr, 2)
    
    def draw(self, screen, video_frame=None, bg_image=None):
        """Draw the settings popup over the darkened background."""
        
        # Draw the background (video or static)
        if video_frame is not None:
            screen.blit(video_frame, (0, 0))
        elif bg_image is not None:
            screen.blit(bg_image, (0, 0))
        
        # Dark overlay to dim the background
        screen.blit(self._overlay, (0, 0))
        
        mouse = pygame.mouse.get_pos()
        
        # ── Custom background image or fallback panel ──
        if self._raw_bg is not None:
            bg_surf = self._scale_raw(self._raw_bg, self.panel_rect.width, self.panel_rect.height, self.bg_scale)
            bg_draw = bg_surf.get_rect(center=(
                self.panel_rect.centerx + self.bg_offset_x,
                self.panel_rect.centery + self.bg_offset_y
            ))
            screen.blit(bg_surf, bg_draw)
        else:
            pygame.draw.rect(screen, (35, 30, 25), self.panel_rect, border_radius=16)
            pygame.draw.rect(screen, (180, 140, 60), self.panel_rect, 3, border_radius=16)
        
        # (No "SETTINGS" title — removed per user request)
        
        # ── Close (X) button — custom image or fallback ──
        close_cx = self.close_rect.centerx + self.close_offset_x
        close_cy = self.close_rect.centery + self.close_offset_y
        hover_close = self.close_rect.move(self.close_offset_x, self.close_offset_y).collidepoint(mouse)
        
        if self._raw_close is not None and self._raw_close_hover is not None:
            raw = self._raw_close_hover if hover_close else self._raw_close
            scale = self.close_scale_hover if hover_close else self.close_scale_normal
            close_surf = self._scale_raw(raw, self.close_rect.width, self.close_rect.height, scale)
            screen.blit(close_surf, close_surf.get_rect(center=(close_cx, close_cy)))
        else:
            shifted_close = self.close_rect.move(self.close_offset_x, self.close_offset_y)
            close_color = (200, 60, 60) if hover_close else (120, 50, 50)
            pygame.draw.rect(screen, close_color, shifted_close, border_radius=6)
            pygame.draw.rect(screen, (220, 180, 180), shifted_close, 2, border_radius=6)
            x_text = self._font_btn.render("X", True, (255, 255, 255))
            screen.blit(x_text, x_text.get_rect(center=shifted_close.center))
        
        # ── Music Volume Slider (light brown, no label, no percentage) ──
        self._draw_slider(screen, self.music_slider_track, self.music_volume,
                          self.dragging_music, self.music_bar_scale,
                          self.music_bar_offset_x, self.music_bar_offset_y)
        
        # ── Mute Music button (left of music bar) ──
        mm_draw = self._get_scaled_mute(self.mute_music_rect, self.mute_music_scale,
                                         self.music_bar_offset_x + self.mute_music_offset_x,
                                         self.music_bar_offset_y + self.mute_music_offset_y)
        raw_mm = self._raw_mute_music_muted if self._music_muted else self._raw_mute_music
        if raw_mm is not None:
            mm_surf = self._scale_raw(raw_mm, self._base_mute_size, self._base_mute_size, self.mute_music_scale)
            screen.blit(mm_surf, mm_surf.get_rect(center=mm_draw.center))
        else:
            mm_c = (180, 60, 60) if self._music_muted else (100, 80, 60)
            pygame.draw.rect(screen, mm_c, mm_draw, border_radius=6)
            mm_t = self._font_small.render("M", True, (255, 230, 180))
            screen.blit(mm_t, mm_t.get_rect(center=mm_draw.center))
        
        # ── SFX Volume Slider (light brown, no label, no percentage) ──
        self._draw_slider(screen, self.sfx_slider_track, self.sfx_volume,
                          self.dragging_sfx, self.sfx_bar_scale,
                          self.sfx_bar_offset_x, self.sfx_bar_offset_y)
        
        # ── Mute SFX button (left of SFX bar) ──
        ms_draw = self._get_scaled_mute(self.mute_sfx_rect, self.mute_sfx_scale,
                                         self.sfx_bar_offset_x + self.mute_sfx_offset_x,
                                         self.sfx_bar_offset_y + self.mute_sfx_offset_y)
        raw_ms = self._raw_mute_sfx_muted if self._sfx_muted else self._raw_mute_sfx
        if raw_ms is not None:
            ms_surf = self._scale_raw(raw_ms, self._base_mute_size, self._base_mute_size, self.mute_sfx_scale)
            screen.blit(ms_surf, ms_surf.get_rect(center=ms_draw.center))
        else:
            ms_c = (180, 60, 60) if self._sfx_muted else (100, 80, 60)
            pygame.draw.rect(screen, ms_c, ms_draw, border_radius=6)
            ms_t = self._font_small.render("S", True, (255, 230, 180))
            screen.blit(ms_t, ms_t.get_rect(center=ms_draw.center))
        
        # ── Drop Faces image board (replaces old text title) ──
        faces_title_y = self.sfx_slider_track.y + self.sfx_bar_offset_y + 40
        if self._raw_face_board is not None:
            raw_w, raw_h = self._raw_face_board.get_size()
            fb_surf = self._scale_raw(self._raw_face_board, raw_w, raw_h, self.face_board_scale)
            fb_cx = SCREEN_W//2 + self.face_board_offset_x
            fb_cy = faces_title_y + self.face_board_offset_y
            screen.blit(fb_surf, fb_surf.get_rect(center=(fb_cx, fb_cy)))
        
        # ── Player face zones ──
        border_color = (220, 200, 160)
        for label_text, box, face, box_scale, ox, oy in [
            ("LEFT", self.p1_box, self.p1_face, self.p1_box_scale,
             self.p1_faces_offset_x, self.p1_faces_offset_y),
            ("RIGHT", self.p2_box, self.p2_face, self.p2_box_scale,
             self.p2_faces_offset_x, self.p2_faces_offset_y),
        ]:
            scaled_box = self._get_scaled_box(box, box_scale, ox, oy)
            
            # Label above box ("LEFT" / "RIGHT") — scaled + offset
            lbl = self.font_medium.render(label_text, True, border_color)
            if self.left_right_txt_scale != 1.0:
                lw, lh = lbl.get_size()
                lbl = pygame.transform.smoothscale(lbl, (max(1, int(lw * self.left_right_txt_scale)),
                                                          max(1, int(lh * self.left_right_txt_scale))))
            lbl_cx = scaled_box.centerx + self.left_right_txt_offset_x
            lbl_by = scaled_box.y - 8 + self.left_right_txt_offset_y
            screen.blit(lbl, lbl.get_rect(centerx=lbl_cx, bottom=lbl_by))
            
            # Drop zone box — highlights on hover
            hover_box = scaled_box.collidepoint(mouse)
            box_bg = (60, 55, 45) if not hover_box else (80, 75, 55)
            pygame.draw.rect(screen, box_bg, scaled_box, border_radius=10)
            pygame.draw.rect(screen, border_color, scaled_box, 2, border_radius=10)
            
            if face is not None:
                fw, fh = face.get_size()
                pmax = scaled_box.width - 16
                pscale = min(pmax / fw, pmax / fh)
                pw2, ph2 = int(fw * pscale), int(fh * pscale)
                preview = pygame.transform.smoothscale(face, (max(1, pw2), max(1, ph2)))
                screen.blit(preview, preview.get_rect(center=scaled_box.center))
            else:
                # Big "+" inside empty slot — scaled + offset
                plus = self._font_plus.render("+", True, (120, 110, 90))
                if self.plus_icon_scale != 1.0:
                    pw3, ph3 = plus.get_size()
                    plus = pygame.transform.smoothscale(plus, (max(1, int(pw3 * self.plus_icon_scale)),
                                                               max(1, int(ph3 * self.plus_icon_scale))))
                plus_cx = scaled_box.centerx + self.plus_icon_offset_x
                plus_cy = scaled_box.centery + self.plus_icon_offset_y
                screen.blit(plus, plus.get_rect(center=(plus_cx, plus_cy)))
            
            # Close/Remove custom image (only shown top-right when a face is selected)
            if face is not None:
                rm_rect = self._get_scaled_face_close(scaled_box)
                hover_rm = rm_rect.collidepoint(mouse)
                if self._raw_close is not None and self._raw_close_hover is not None:
                    raw_c = self._raw_close_hover if hover_rm else self._raw_close
                    c_scale = self.face_remove_scale_hover if hover_rm else self.face_remove_scale_normal
                    c_surf = self._scale_raw(raw_c, 32, 32, c_scale)
                    screen.blit(c_surf, c_surf.get_rect(center=rm_rect.center))
                else:
                    rm_color = (180, 60, 60) if hover_rm else (120, 50, 50)
                    pygame.draw.rect(screen, rm_color, rm_rect, border_radius=6)
                    pygame.draw.rect(screen, (200, 150, 150), rm_rect, 1, border_radius=6)
                    rm_text = self._font_small.render("X", True, (255, 220, 220))
                    screen.blit(rm_text, rm_text.get_rect(center=rm_rect.center))
        
        # ── Head size +/- controls (independently scaled and positioned) ──
        for minus_r, plus_r, scale_val, ctrl_scale, fox, foy, cox, coy in [
            (self.p1_minus, self.p1_plus, self.p1_head_base, self.p1_controls_scale,
             self.p1_faces_offset_x, self.p1_faces_offset_y,
             self.p1_controls_offset_x, self.p1_controls_offset_y),
            (self.p2_minus, self.p2_plus, self.p2_head_base, self.p2_controls_scale,
             self.p2_faces_offset_x, self.p2_faces_offset_y,
             self.p2_controls_offset_x, self.p2_controls_offset_y),
        ]:
            sm, sp = self._get_scaled_ctrl(minus_r, plus_r, ctrl_scale, fox + cox, foy + coy)
            
            hover_m = sm.collidepoint(mouse)
            c_m = (100, 80, 60) if hover_m else (70, 55, 40)
            pygame.draw.rect(screen, c_m, sm, border_radius=6)
            pygame.draw.rect(screen, (160, 130, 80), sm, 1, border_radius=6)
            mt = self._font_btn.render("-", True, (255, 230, 180))
            if self.math_txt_scale != 1.0:
                mw, mh = mt.get_size()
                mt = pygame.transform.smoothscale(mt, (max(1, int(mw * self.math_txt_scale)),
                                                        max(1, int(mh * self.math_txt_scale))))
            screen.blit(mt, mt.get_rect(center=(sm.centerx + self.math_txt_offset_x,
                                                 sm.centery + self.math_txt_offset_y)))
            
            hover_p = sp.collidepoint(mouse)
            c_p = (100, 80, 60) if hover_p else (70, 55, 40)
            pygame.draw.rect(screen, c_p, sp, border_radius=6)
            pygame.draw.rect(screen, (160, 130, 80), sp, 1, border_radius=6)
            pt = self._font_btn.render("+", True, (255, 230, 180))
            if self.math_txt_scale != 1.0:
                tw, th = pt.get_size()
                pt = pygame.transform.smoothscale(pt, (max(1, int(tw * self.math_txt_scale)),
                                                        max(1, int(th * self.math_txt_scale))))
            screen.blit(pt, pt.get_rect(center=(sp.centerx + self.math_txt_offset_x,
                                                 sp.centery + self.math_txt_offset_y)))
            
            # Current scale value displayed between the buttons — scaled + offset
            sv = self._font_small.render(f"{scale_val:.1f}x", True, (200, 180, 140))
            if self.math_txt_scale != 1.0:
                sw2, sh2 = sv.get_size()
                sv = pygame.transform.smoothscale(sv, (max(1, int(sw2 * self.math_txt_scale)),
                                                        max(1, int(sh2 * self.math_txt_scale))))
            sx = (sm.right + sp.left) // 2 + self.math_txt_offset_x
            sy = sm.centery + self.math_txt_offset_y
            screen.blit(sv, sv.get_rect(center=(sx, sy)))






class OnlineMenu:
    """Popup overlay that shows a custom message when the player clicks Online.
    Supports custom background image, custom close button, and configurable text."""
    
    def __init__(self, font_large, font_medium):
        self.font_large = font_large
        self.font_medium = font_medium
        self.audio_manager = None
        
        # ================================================================
        # ██  ONLINE MENU — MASTER CONFIGURATION HUB  ██
        # All positioning and sizing controls in ONE place.
        # ================================================================
        
        # ── POSITION OFFSETS ──
        self.bg_offset_x           = 0
        self.bg_offset_y           = 0
        self.close_offset_x        = 0
        self.close_offset_y        = 0
        self.text_offset_x         = 0
        self.text_offset_y         = 0
        
        # ── SIZE MULTIPLIERS ──
        self.bg_scale              = 1.0
        self.close_scale_normal    = 1.0
        self.close_scale_hover     = 1.0
        self.text_scale            = 1.0
        
        # ── TEXT CUSTOMIZATION ──
        self.text_color            = (220, 200, 160)  # #dcc8a0
        self.text_message          = "We are working on it"
        
        # ================================================================
        # ██  END OF CONFIGURATION HUB  ██
        # ================================================================
        
        # Centered panel
        pw, ph = 500, 260
        self.panel_rect = pygame.Rect(SCREEN_W//2 - pw//2, SCREEN_H//2 - ph//2, pw, ph)
        px, py = self.panel_rect.x, self.panel_rect.y
        
        # Close (X) button — top right corner
        close_size = 20
        self.close_rect = pygame.Rect(px + pw - close_size - 28, py + 18, close_size, close_size)
        
        # Pre-build the dark overlay
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 180))
        
        self._font_btn = pygame.font.Font(None, 28)
        self._font_msg = pygame.font.Font(None, 38)
        
        # ── Load custom images (raw full-res for crisp scaling) ──
        self._raw_bg = self._try_load_raw("assets/ui/online_bg.png")
        self._raw_close = self._try_load_raw("assets/ui/close.png")
        self._raw_close_hover = self._try_load_raw("assets/ui/close_hover.png")
    
    def _try_load_raw(self, path):
        """Load an image at full resolution. Returns None if file is missing."""
        try:
            if os.path.isfile(path):
                return pygame.image.load(path).convert_alpha()
        except Exception:
            pass
        return None
    
    def _scale_raw(self, raw_surface, target_w, target_h, multiplier):
        """Scale a raw full-res image. Always from ORIGINAL for max quality."""
        final_w = max(1, int(target_w * multiplier))
        final_h = max(1, int(target_h * multiplier))
        return pygame.transform.smoothscale(raw_surface, (final_w, final_h))
    
    def handle_event(self, event) -> str:
        """Returns 'done' when close is clicked, otherwise None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_hit = self.close_rect.move(self.close_offset_x, self.close_offset_y)
            if close_hit.collidepoint(event.pos):
                if self.audio_manager:
                    self.audio_manager.play_sound("menu_click")
                return "done"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "done"
        # Controller X button closes the online popup
        if event.type == pygame.JOYBUTTONDOWN and event.button == JOY_BTN_X:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_click")
            return "done"
        # Controller A button also closes (since it opens the popup)
        if event.type == pygame.JOYBUTTONDOWN and event.button == JOY_BTN_A:
            if self.audio_manager:
                self.audio_manager.play_sound("menu_click")
            return "done"
        return None
    
    def draw(self, screen, video_frame=None, bg_image=None):
        """Draw the Online popup over the darkened background."""
        if video_frame is not None:
            screen.blit(video_frame, (0, 0))
        elif bg_image is not None:
            screen.blit(bg_image, (0, 0))
        
        screen.blit(self._overlay, (0, 0))
        mouse = pygame.mouse.get_pos()
        
        # ── Custom background image or fallback panel ──
        if self._raw_bg is not None:
            bg_surf = self._scale_raw(self._raw_bg, self.panel_rect.width, self.panel_rect.height, self.bg_scale)
            bg_draw = bg_surf.get_rect(center=(
                self.panel_rect.centerx + self.bg_offset_x,
                self.panel_rect.centery + self.bg_offset_y
            ))
            screen.blit(bg_surf, bg_draw)
        else:
            pygame.draw.rect(screen, (30, 30, 45), self.panel_rect, border_radius=16)
            pygame.draw.rect(screen, (80, 120, 200), self.panel_rect, 3, border_radius=16)
        
        # ── Close (X) button — custom image or fallback ──
        close_cx = self.close_rect.centerx + self.close_offset_x
        close_cy = self.close_rect.centery + self.close_offset_y
        hover_close = self.close_rect.move(self.close_offset_x, self.close_offset_y).collidepoint(mouse)
        
        if self._raw_close is not None and self._raw_close_hover is not None:
            raw = self._raw_close_hover if hover_close else self._raw_close
            scale = self.close_scale_hover if hover_close else self.close_scale_normal
            close_surf = self._scale_raw(raw, self.close_rect.width, self.close_rect.height, scale)
            screen.blit(close_surf, close_surf.get_rect(center=(close_cx, close_cy)))
        else:
            shifted_close = self.close_rect.move(self.close_offset_x, self.close_offset_y)
            close_color = (200, 60, 60) if hover_close else (120, 50, 50)
            pygame.draw.rect(screen, close_color, shifted_close, border_radius=6)
            pygame.draw.rect(screen, (220, 180, 180), shifted_close, 2, border_radius=6)
            x_text = self._font_btn.render("X", True, (255, 255, 255))
            screen.blit(x_text, x_text.get_rect(center=shifted_close.center))
        
        # ── Description text — #dcc8a0, scaled + offset ──
        msg = self._font_msg.render(self.text_message, True, self.text_color)
        if self.text_scale != 1.0:
            mw, mh = msg.get_size()
            msg = pygame.transform.smoothscale(msg, (max(1, int(mw * self.text_scale)),
                                                      max(1, int(mh * self.text_scale))))
        msg_cx = self.panel_rect.centerx + self.text_offset_x
        msg_cy = self.panel_rect.centery + self.text_offset_y
        screen.blit(msg, msg.get_rect(center=(msg_cx, msg_cy)))


# Legacy alias so existing imports don't break
DropFacesMenu = SettingsMenu
