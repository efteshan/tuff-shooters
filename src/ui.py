# src/ui.py

import pygame
from src.constants import SCREEN_W, SCREEN_H, KO_DISPLAY_DURATION
from src.particles import GifPlayer


class HUD:
    """
    Pixel art HUD.
    - Health: heart icon + color-changing bar
    - Ammo:   bullet icon + color-changing bar
    - Pause:  swappable image button
    """

    # ── ASSET PATHS ────────────────────────────────
    # To change pause/resume button images:
    # Drop your images into assets/ui/ and name them:
    #   pause_btn.png   — shown while game is RUNNING
    #   resume_btn.png  — shown while game is PAUSED
    # Any size — auto scaled to 40x40
    PAUSE_BTN_PATH  = "assets/ui/pause_btn.png"
    RESUME_BTN_PATH = "assets/ui/resume_btn.png"

    def __init__(self, font):
        self.font_num = pygame.font.Font(None, 20)

        # Build pixel art icons
        self.heart_icon  = self._make_heart_icon()
        self.bullet_icon = self._make_bullet_icon()

        # Load pause/resume button images
        # Falls back to generated wooden buttons
        # if image files are not found
        self.btn_pause  = self._load_btn(
            self.PAUSE_BTN_PATH,  "pause")
        self.btn_resume = self._load_btn(
            self.RESUME_BTN_PATH, "play")

        self.is_paused = False

    # ══════════════════════════════════════════════
    # BUTTON LOADER — image file or fallback
    # ══════════════════════════════════════════════

    def _load_btn(self, path, fallback_type):
        import os
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(path)

            # Load at full original resolution
            img = pygame.image.load(path).convert_alpha()
            orig_w, orig_h = img.get_size()

            # Scale to 72px tall preserving aspect ratio
            # Larger size = sharper detail on screen
            target_h = 44
            target_w = int(orig_w * (target_h / orig_h))

            # Use smoothscale for clean anti-aliased edges
            # when downscaling from the high-res source PNG
            scaled = pygame.transform.smoothscale(
                img, (target_w, target_h))

            print(f"[HUD] Loaded {path} "
                  f"{orig_w}x{orig_h} -> "
                  f"{target_w}x{target_h}")
            return scaled

        except Exception as e:
            print(f"[HUD] Not found: {path} -> fallback")
            return self._make_wood_btn(fallback_type)

    # ══════════════════════════════════════════════
    # PIXEL ART CREATORS
    # ══════════════════════════════════════════════

    def _make_heart_icon(self):
        """
        Pixel art heart icon — 20x18px, 2px pixel size.
        Red with highlight and shadow. Matches reference.
        """
        s  = pygame.Surface((20, 18), pygame.SRCALPHA)
        c  = (215,  35,  35)   # main red
        lt = (255, 110, 110)   # highlight
        dk = (130,  15,  15)   # shadow
        o  = ( 20,   5,   5)   # outline

        # 10x9 pixel grid — each pixel is 2x2
        grid = [
            [0,0,1,1,0, 0,1,1,0,0],
            [0,1,1,1,1, 1,1,1,1,0],
            [1,1,1,1,1, 1,1,1,1,1],
            [1,1,1,1,1, 1,1,1,1,1],
            [1,1,1,1,1, 1,1,1,1,1],
            [0,1,1,1,1, 1,1,1,1,0],
            [0,0,1,1,1, 1,1,1,0,0],
            [0,0,0,1,1, 1,1,0,0,0],
            [0,0,0,0,1, 1,0,0,0,0],
        ]
        pw = 2
        for ry, row in enumerate(grid):
            for rx, cell in enumerate(row):
                if not cell:
                    continue
                px = rx * pw
                py = ry * pw
                # Highlight top-left bump
                if ry <= 1 and rx in [2, 3, 6, 7]:
                    col = lt
                # Shadow right side and bottom
                elif rx >= 7 or ry >= 6:
                    col = dk
                else:
                    col = c
                pygame.draw.rect(s, col, (px, py, pw, pw))
        return s

    def _make_bullet_icon(self):
        """
        Upright pixel art bullet — 14x22px, 2px pixels.
        Gold tip, orange brass body. Matches reference.
        """
        s = pygame.Surface((14, 22), pygame.SRCALPHA)

        # Colors
        tip_lt  = (255, 230,  60)   # tip highlight
        tip_md  = (220, 170,  20)   # tip mid
        tip_dk  = (160, 100,  10)   # tip shadow
        body_lt = (255, 175,  40)   # body highlight
        body_md = (210, 130,  20)   # body main
        body_dk = (150,  80,  10)   # body shadow
        base_c  = ( 90,  50,  10)   # base rim
        outline = ( 30,  15,   5)   # outline

        # Tip — top 8 rows, tapered
        tip_rows = [
            (5, 4),   # row 0 — 4px wide centered
            (4, 6),   # row 1
            (3, 8),   # row 2
            (2, 10),  # row 3
            (2, 10),  # row 4
            (1, 12),  # row 5
            (1, 12),  # row 6
            (1, 12),  # row 7
        ]
        for ry, (lx, w) in enumerate(tip_rows):
            py = ry * 1
            for rx in range(lx, lx + w):
                px = rx
                if rx == lx or rx == lx + w - 1:
                    col = tip_dk
                elif rx == lx + 1:
                    col = tip_lt
                else:
                    col = tip_md
                s.set_at((px, py), col)

        # Body — rows 8 to 18
        for ry in range(8, 19):
            py = ry
            for rx in range(1, 13):
                if rx == 1 or rx == 12:
                    col = outline
                elif rx == 2:
                    col = body_lt
                elif rx >= 10:
                    col = body_dk
                else:
                    col = body_md
                s.set_at((rx, py), col)

        # Base rim — rows 19-21
        for ry in range(19, 22):
            py = ry
            for rx in range(2, 12):
                if rx == 2 or rx == 11:
                    col = outline
                else:
                    col = base_c
                s.set_at((rx, py), col)

        # Scale up 2x for crisp pixel look
        big = pygame.transform.scale(s, (28, 44))
        # Scale back down to 14x22 — keeps sharp edges
        return pygame.transform.scale(big, (14, 22))

    def _make_wood_btn(self, icon_type):
        """Fallback wooden button if no image file found."""
        import math
        size = 40
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        wood_dk  = ( 55, 35, 15)
        wood_md  = ( 95, 62, 25)
        wood_lt  = (145, 95, 40)
        wood_hi  = (175,125, 55)
        outline  = ( 30, 18,  8)
        icon_c   = (215,175, 90)
        icon_hi  = (240,210,130)
        icon_sh  = (100, 65, 20)
        pygame.draw.circle(s, wood_dk, (20,20), 20)
        pygame.draw.circle(s, wood_md, (20,20), 18)
        pygame.draw.circle(s, wood_lt, (20,20), 14, 2)
        pygame.draw.circle(s, wood_dk, (20,20), 10, 1)
        pygame.draw.circle(s, wood_lt, (19,18),  6, 1)
        pygame.draw.arc(s, wood_hi,
            (5,5,20,18),
            math.radians(200), math.radians(320), 3)
        pygame.draw.circle(s, outline, (20,20), 19, 2)
        if icon_type == "pause":
            for bx in [13, 21]:
                pygame.draw.rect(s, icon_sh,
                    (bx+1,13,6,15), border_radius=2)
                pygame.draw.rect(s, icon_c,
                    (bx,  12,6,15), border_radius=2)
                pygame.draw.rect(s, icon_hi,
                    (bx+1,13,2, 6), border_radius=1)
        else:
            pygame.draw.polygon(s, icon_sh,
                [(15,11),(15,30),(30,21)])
            pygame.draw.polygon(s, icon_c,
                [(14,10),(14,29),(29,20)])
            pygame.draw.polygon(s, icon_hi,
                [(14,10),(14,18),(22,14)])
        return s

    # ══════════════════════════════════════════════
    # BAR DRAWING
    # ══════════════════════════════════════════════

    def _bar_color(self, fraction):
        """
        Returns bar fill color based on fraction 0.0-1.0.
        Matches reference image color progression:
        Green → Orange → Red
        """
        if fraction > 0.6:
            return ( 55, 200,  70)   # green
        if fraction > 0.3:
            return (230, 140,  20)   # orange
        return (210,  35,  35)       # red

    def _draw_bar(self, screen, icon, ix, iy,
                  bar_x, bar_y, bar_w, bar_h,
                  fraction, flipped=False):
        """
        Draw icon + health/ammo bar exactly like reference.
        Clean white outline, colored fill, dark track.
        """
        # ── ICON ──────────────────────────────────
        icon_y = bar_y + bar_h // 2 - icon.get_height() // 2
        screen.blit(icon, (ix, icon_y))

        # ── BAR OUTLINE ───────────────────────────
        # White outer border — 2px
        pygame.draw.rect(screen, (240, 240, 240),
            (bar_x - 2, bar_y - 2,
             bar_w + 4, bar_h + 4),
            border_radius=6)

        # Dark track background
        pygame.draw.rect(screen, (30, 20, 20),
            (bar_x, bar_y, bar_w, bar_h),
            border_radius=5)

        # Colored fill
        fill_w = max(0, int(fraction * bar_w))
        if fill_w > 4:
            fill_c = self._bar_color(fraction)
            if not flipped:
                pygame.draw.rect(screen, fill_c,
                    (bar_x, bar_y, fill_w, bar_h),
                    border_radius=5)
                # Shine stripe — top 3px white semi-transparent
                shine = pygame.Surface(
                    (fill_w - 4, max(1, bar_h // 3)),
                    pygame.SRCALPHA)
                shine.fill((255, 255, 255, 70))
                screen.blit(shine, (bar_x + 2, bar_y + 2))
            else:
                rx = bar_x + bar_w - fill_w
                pygame.draw.rect(screen, fill_c,
                    (rx, bar_y, fill_w, bar_h),
                    border_radius=5)
                shine = pygame.Surface(
                    (fill_w - 4, max(1, bar_h // 3)),
                    pygame.SRCALPHA)
                shine.fill((255, 255, 255, 70))
                screen.blit(shine, (rx + 2, bar_y + 2))

    # ══════════════════════════════════════════════
    # MAIN DRAW
    # ══════════════════════════════════════════════

    def draw(self, screen, p1, p2):
        bar_w  = 200
        bar_h  = 16
        icon_gap = 6    # gap between icon and bar

        heart_w  = self.heart_icon.get_width()    # 20
        bullet_w = self.bullet_icon.get_width()   # 14

        # Row Y positions
        row1_y = 14    # health bar row
        row2_y = 38    # ammo bar row

        # ── P1 LEFT ────────────────────────────────
        p1_icon_x  = 12
        p1_bar_x   = p1_icon_x + heart_w + icon_gap

        # Health
        self._draw_bar(screen,
            self.heart_icon,
            p1_icon_x, row1_y,
            p1_bar_x,  row1_y,
            bar_w, bar_h,
            p1.health / 100.0)

        # Ammo
        p1_ammo_icon_x = 12
        p1_ammo_bar_x  = p1_ammo_icon_x + bullet_w + icon_gap
        self._draw_bar(screen,
            self.bullet_icon,
            p1_ammo_icon_x, row2_y,
            p1_ammo_bar_x,  row2_y,
            bar_w, bar_h,
            p1.ammo / 67.0)

        # ── P2 RIGHT ───────────────────────────────
        # P2 — mirrored from right edge
        # Icon sits to the RIGHT of the bar
        # but everything stays inside screen
        p2_heart_icon_x  = SCREEN_W - 12 - \
                           self.heart_icon.get_width()
        p2_bar_x         = p2_heart_icon_x - icon_gap - bar_w

        p2_bullet_icon_x = SCREEN_W - 12 - \
                           self.bullet_icon.get_width()
        p2_ammo_bar_x    = p2_bullet_icon_x - icon_gap - bar_w

        # Health bar P2
        self._draw_bar(screen,
            self.heart_icon,
            p2_heart_icon_x, row1_y,
            p2_bar_x, row1_y,
            bar_w, bar_h,
            p2.health / 100.0,
            flipped=True)

        # Ammo bar P2
        self._draw_bar(screen,
            self.bullet_icon,
            p2_bullet_icon_x, row2_y,
            p2_ammo_bar_x, row2_y,
            bar_w, bar_h,
            p2.ammo / 67.0,
            flipped=True)

        # Game is RUNNING → show PAUSE button (so player can pause)
        # Game is PAUSED  → show RESUME button (so player can resume)
        btn = self.btn_pause \
              if not self.is_paused else self.btn_resume
        bw = btn.get_width()
        bh = btn.get_height()
        screen.blit(btn,
            (SCREEN_W // 2 - bw // 2,
             bh // 2 - bh // 2 + 4))


class KOScreen:
    """K.O. screen overlay with animation."""
    
    def __init__(self, ko_strip_path, ko_frames):
        self.gif = GifPlayer(ko_strip_path, ko_frames, fps=15)
        self.timer = 0.0
        self.duration = KO_DISPLAY_DURATION
        self.done = False
        
        # Pulse scaling effect
        self.scale = 1.0
        self.scale_dir = 1
    
    def reset(self):
        """Reset K.O. screen for new display."""
        self.gif.timer = 0.0
        self.gif.current = 0
        self.timer = 0.0
        self.done = False
        self.scale = 1.0
        self.scale_dir = 1
    
    def update(self, dt):
        """Update K.O. animation."""
        self.gif.update(dt)
        self.timer += dt
        
        # Pulse: grow then shrink on loop
        self.scale += self.scale_dir * 0.8 * dt
        if self.scale > 1.25:
            self.scale_dir = -1
        elif self.scale < 0.9:
            self.scale_dir = 1
        
        if self.timer >= self.duration:
            self.done = True
    
    def draw(self, screen):
        """Draw K.O. animation on screen."""
        frame = self.gif.get_frame()
        size = int(400 * self.scale)
        scaled = pygame.transform.smoothscale(frame, (size, size))
        x = SCREEN_W // 2 - size // 2
        y = SCREEN_H // 2 - size // 2
        screen.blit(scaled, (x, y))
