# src/ui.py — In-game HUD (health bars, ammo bars, pause button) and K.O. screen overlay.

import pygame
from src.constants import SCREEN_W, SCREEN_H, KO_DISPLAY_DURATION
from src.particles import GifPlayer


class HUD:
    """Draws the health bars, ammo bars, and pause/resume button during gameplay.
    P1's bars are top-left, P2's bars are top-right (mirrored).
    Bar color changes green → orange → red as values drop."""

    # Custom button images. Drop your own PNGs here and they'll be auto-scaled.
    PAUSE_BTN_PATH  = "assets/ui/pause_btn.png"
    RESUME_BTN_PATH = "assets/ui/resume_btn.png"

    def __init__(self, font):
        self.font_num = pygame.font.Font(None, 20)

        # Pre-build the tiny pixel art icons that sit next to each bar
        self.heart_icon  = self._make_heart_icon()
        self.bullet_icon = self._make_bullet_icon()

        # Try to load custom pause/resume button images, fall back to procedural wood buttons
        self.btn_pause  = self._load_btn(self.PAUSE_BTN_PATH,  "pause")
        self.btn_resume = self._load_btn(self.RESUME_BTN_PATH, "play")

        self.is_paused = False

    def _load_btn(self, path, fallback_type):
        """Load a button image from disk, scale to 44px tall. If missing, generate a wood-style button."""
        import os
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(path)

            img = pygame.image.load(path).convert_alpha()
            orig_w, orig_h = img.get_size()

            # Scale to 44px tall, keep aspect ratio
            target_h = 44
            target_w = int(orig_w * (target_h / orig_h))
            scaled = pygame.transform.smoothscale(img, (target_w, target_h))

            print(f"[HUD] Loaded {path} "
                  f"{orig_w}x{orig_h} -> "
                  f"{target_w}x{target_h}")
            return scaled

        except Exception as e:
            print(f"[HUD] Not found: {path} -> fallback")
            return self._make_wood_btn(fallback_type)

    # ── PIXEL ART ICON GENERATORS ───────────────────────────────

    def _make_heart_icon(self):
        """20x18px heart icon with highlight and shadow, drawn on a 10x9 pixel grid at 2x scale."""
        s  = pygame.Surface((20, 18), pygame.SRCALPHA)
        c  = (215,  35,  35)   # Main red
        lt = (255, 110, 110)   # Top-left highlight
        dk = (130,  15,  15)   # Bottom-right shadow
        o  = ( 20,   5,   5)   # Outline (unused but kept for reference)

        # Each 1 in this grid = a 2x2 red pixel in the final icon
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
                if ry <= 1 and rx in [2, 3, 6, 7]:
                    col = lt  # Bright spots on the top bumps
                elif rx >= 7 or ry >= 6:
                    col = dk  # Darker right side and bottom
                else:
                    col = c
                pygame.draw.rect(s, col, (px, py, pw, pw))
        return s

    def _make_bullet_icon(self):
        """14x22px upright bullet with gold tip and brass body, drawn pixel by pixel."""
        s = pygame.Surface((14, 22), pygame.SRCALPHA)

        tip_lt  = (255, 230,  60)
        tip_md  = (220, 170,  20)
        tip_dk  = (160, 100,  10)
        body_lt = (255, 175,  40)
        body_md = (210, 130,  20)
        body_dk = (150,  80,  10)
        base_c  = ( 90,  50,  10)
        outline = ( 30,  15,   5)

        # Tapered tip (rows 0-7), gets wider toward the body
        tip_rows = [
            (5, 4), (4, 6), (3, 8), (2, 10),
            (2, 10), (1, 12), (1, 12), (1, 12),
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

        # Brass body (rows 8-18)
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

        # Base rim (rows 19-21)
        for ry in range(19, 22):
            py = ry
            for rx in range(2, 12):
                if rx == 2 or rx == 11:
                    col = outline
                else:
                    col = base_c
                s.set_at((rx, py), col)

        # Scale up then back down for crisp pixel edges
        big = pygame.transform.scale(s, (28, 44))
        return pygame.transform.scale(big, (14, 22))

    def _make_wood_btn(self, icon_type):
        """Procedural wooden circle button with pause bars or play triangle icon."""
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
        # Wood circle with ring grain pattern
        pygame.draw.circle(s, wood_dk, (20,20), 20)
        pygame.draw.circle(s, wood_md, (20,20), 18)
        pygame.draw.circle(s, wood_lt, (20,20), 14, 2)
        pygame.draw.circle(s, wood_dk, (20,20), 10, 1)
        pygame.draw.circle(s, wood_lt, (19,18),  6, 1)
        pygame.draw.arc(s, wood_hi, (5,5,20,18),
            math.radians(200), math.radians(320), 3)
        pygame.draw.circle(s, outline, (20,20), 19, 2)
        if icon_type == "pause":
            # Two vertical bars
            for bx in [13, 21]:
                pygame.draw.rect(s, icon_sh, (bx+1,13,6,15), border_radius=2)
                pygame.draw.rect(s, icon_c,  (bx,  12,6,15), border_radius=2)
                pygame.draw.rect(s, icon_hi, (bx+1,13,2, 6), border_radius=1)
        else:
            # Play triangle
            pygame.draw.polygon(s, icon_sh, [(15,11),(15,30),(30,21)])
            pygame.draw.polygon(s, icon_c,  [(14,10),(14,29),(29,20)])
            pygame.draw.polygon(s, icon_hi, [(14,10),(14,18),(22,14)])
        return s

    # ── BAR DRAWING ─────────────────────────────────────────────

    def _bar_color(self, fraction):
        """Pick bar fill color: green when healthy, orange when mid, red when critical."""
        if fraction > 0.6:
            return ( 55, 200,  70)
        if fraction > 0.3:
            return (230, 140,  20)
        return (210,  35,  35)

    def _draw_bar(self, screen, icon, ix, iy,
                  bar_x, bar_y, bar_w, bar_h,
                  fraction, flipped=False):
        """Draw one bar: icon on the side, white-outlined track, colored fill with shine effect.
        flipped=True fills the bar from right to left (used for P2's mirrored layout)."""
        # Icon centered vertically with the bar
        icon_y = bar_y + bar_h // 2 - icon.get_height() // 2
        screen.blit(icon, (ix, icon_y))

        # White border around the bar
        pygame.draw.rect(screen, (240, 240, 240),
            (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4),
            border_radius=6)
        # Dark empty track behind the fill
        pygame.draw.rect(screen, (30, 20, 20),
            (bar_x, bar_y, bar_w, bar_h),
            border_radius=5)

        # Colored fill portion
        fill_w = max(0, int(fraction * bar_w))
        if fill_w > 4:
            fill_c = self._bar_color(fraction)
            if not flipped:
                pygame.draw.rect(screen, fill_c,
                    (bar_x, bar_y, fill_w, bar_h), border_radius=5)
                # Glossy shine stripe along the top of the fill
                shine = pygame.Surface(
                    (fill_w - 4, max(1, bar_h // 3)), pygame.SRCALPHA)
                shine.fill((255, 255, 255, 70))
                screen.blit(shine, (bar_x + 2, bar_y + 2))
            else:
                # P2's bar fills from right to left
                rx = bar_x + bar_w - fill_w
                pygame.draw.rect(screen, fill_c,
                    (rx, bar_y, fill_w, bar_h), border_radius=5)
                shine = pygame.Surface(
                    (fill_w - 4, max(1, bar_h // 3)), pygame.SRCALPHA)
                shine.fill((255, 255, 255, 70))
                screen.blit(shine, (rx + 2, bar_y + 2))

    # ── MAIN DRAW ───────────────────────────────────────────────

    def draw(self, screen, p1, p2):
        """Draw all HUD elements for both players."""
        bar_w  = 200
        bar_h  = 16
        icon_gap = 6

        heart_w  = self.heart_icon.get_width()
        bullet_w = self.bullet_icon.get_width()

        row1_y = 14   # Health bar row
        row2_y = 38   # Ammo bar row

        # P1 bars (top-left corner)
        p1_icon_x  = 12
        p1_bar_x   = p1_icon_x + heart_w + icon_gap

        self._draw_bar(screen, self.heart_icon,
            p1_icon_x, row1_y, p1_bar_x, row1_y,
            bar_w, bar_h, p1.health / 100.0)

        # P1 ammo — fraction depends on which weapon is equipped
        p1_ammo_icon_x = 12
        p1_ammo_bar_x  = p1_ammo_icon_x + bullet_w + icon_gap
        if p1.has_bazooka:
            from src.constants import BAZOOKA_AMMO
            p1_ammo_frac = p1.bazooka_ammo / max(1, BAZOOKA_AMMO)
        elif p1.has_shotgun:
            from src.constants import SHOTGUN_AMMO
            p1_ammo_frac = p1.shotgun_ammo / max(1, SHOTGUN_AMMO)
        else:
            p1_ammo_frac = p1.ammo / max(1, p1.max_ammo)
        self._draw_bar(screen, self.bullet_icon,
            p1_ammo_icon_x, row2_y, p1_ammo_bar_x, row2_y,
            bar_w, bar_h, p1_ammo_frac)

        # P2 bars (top-right corner, mirrored)
        p2_heart_icon_x  = SCREEN_W - 12 - self.heart_icon.get_width()
        p2_bar_x         = p2_heart_icon_x - icon_gap - bar_w
        p2_bullet_icon_x = SCREEN_W - 12 - self.bullet_icon.get_width()
        p2_ammo_bar_x    = p2_bullet_icon_x - icon_gap - bar_w

        self._draw_bar(screen, self.heart_icon,
            p2_heart_icon_x, row1_y, p2_bar_x, row1_y,
            bar_w, bar_h, p2.health / 100.0, flipped=True)

        if p2.has_bazooka:
            from src.constants import BAZOOKA_AMMO
            p2_ammo_frac = p2.bazooka_ammo / max(1, BAZOOKA_AMMO)
        elif p2.has_shotgun:
            from src.constants import SHOTGUN_AMMO
            p2_ammo_frac = p2.shotgun_ammo / max(1, SHOTGUN_AMMO)
        else:
            p2_ammo_frac = p2.ammo / max(1, p2.max_ammo)
        self._draw_bar(screen, self.bullet_icon,
            p2_bullet_icon_x, row2_y, p2_ammo_bar_x, row2_y,
            bar_w, bar_h, p2_ammo_frac, flipped=True)

        # Pause/Resume button centered at the top of screen
        btn = self.btn_pause if not self.is_paused else self.btn_resume
        bw = btn.get_width()
        bh = btn.get_height()
        screen.blit(btn, (SCREEN_W // 2 - bw // 2, bh // 2 - bh // 2 + 4))


class KOScreen:
    """The big K.O. text/animation that shows when a player dies.
    Pulses in size while displaying, then auto-dismisses after KO_DISPLAY_DURATION seconds."""
    
    def __init__(self, ko_strip_path, ko_frames):
        self.gif = GifPlayer(ko_strip_path, ko_frames, fps=15)
        self.timer = 0.0
        self.duration = KO_DISPLAY_DURATION
        self.done = False
        self.scale = 1.0
        self.scale_dir = 1
    
    def reset(self):
        """Restart the K.O. animation from the beginning."""
        self.gif.timer = 0.0
        self.gif.current = 0
        self.timer = 0.0
        self.done = False
        self.scale = 1.0
        self.scale_dir = 1
    
    def update(self, dt):
        self.gif.update(dt)
        self.timer += dt
        # Pulsing scale effect: grows to 1.25x then shrinks to 0.9x, repeating
        self.scale += self.scale_dir * 0.8 * dt
        if self.scale > 1.25:
            self.scale_dir = -1
        elif self.scale < 0.9:
            self.scale_dir = 1
        if self.timer >= self.duration:
            self.done = True
    
    def draw(self, screen):
        frame = self.gif.get_frame()
        size = int(400 * self.scale)
        scaled = pygame.transform.smoothscale(frame, (size, size))
        x = SCREEN_W // 2 - size // 2
        y = SCREEN_H // 2 - size // 2
        screen.blit(scaled, (x, y))
