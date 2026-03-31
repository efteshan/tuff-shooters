# src/arena.py — The game world: ground, platforms, barrel, destructible box, clouds.
# Loads custom images from assets/ folders when available, falls back to procedural art.

import pygame
from src.constants import (
    GROUND_Y, VIRTUAL_W, VIRTUAL_H, GROUND_COLOR, load_or_placeholder,
    GROUND_IMG_SCALE, GROUND_IMG_X_OFFSET, GROUND_IMG_Y_OFFSET, GROUND_SURFACE_FRACTION
)


def _detect_solid_bounds(image, alpha_threshold=30, edge_inset=6,
                         min_solid_fraction=0.25):
    """Scan a PNG image to find where the actual visible content is.
    Used to figure out the real collision area of custom platform/cloud images
    that might have transparent padding around them.
    Returns (y_offset_to_solid, left_edge_col, right_edge_col)."""
    w, h = image.get_size()
    if w == 0 or h == 0:
        return 0, 0, w

    min_solid_px = max(3, int(w * min_solid_fraction))

    # Step 1: Find first row with enough solid pixels
    surface_y_offset = 0
    for row in range(h):
        solid = 0
        for col in range(0, w, max(1, w // 40)):
            try:
                if image.get_at((col, row))[3] > alpha_threshold:
                    solid += 1
            except Exception:
                pass
        if solid * (w // max(1, w // 40)) >= min_solid_px:
            surface_y_offset = row
            break

    # Step 2: Find leftmost solid column near the surface
    scan_top = surface_y_offset
    scan_bot = min(surface_y_offset + 40, h)
    col_left = 0
    for col in range(0, w, 2):
        found = False
        for row in range(scan_top, scan_bot):
            try:
                if image.get_at((col, row))[3] > alpha_threshold:
                    found = True
                    break
            except Exception:
                pass
        if found:
            col_left = col
            break

    # Step 3: Find rightmost solid column near the surface
    col_right = w
    for col in range(w - 1, 0, -2):
        found = False
        for row in range(scan_top, scan_bot):
            try:
                if image.get_at((col, row))[3] > alpha_threshold:
                    found = True
                    break
            except Exception:
                pass
        if found:
            col_right = col + 1
            break

    # Apply inset to avoid hovering at very edge pixels
    col_left  = min(col_left  + edge_inset, w // 2)
    col_right = max(col_right - edge_inset, w // 2 + 1)

    return surface_y_offset, col_left, col_right

def create_cloud_surface(vibrant=False, shape_id=0):
    """Generate a procedural cartoon cloud sprite. 7 unique shapes available.
    vibrant=True makes it bright white (used for trampoline clouds players can bounce on).
    vibrant=False makes it grey-blue (background decoration only)."""
    import math
    w, h = 120, 52
    s = pygame.Surface((w, h), pygame.SRCALPHA)

    # ── 7 UNIQUE CLOUD SHAPES ─────────────────────
    shapes = {
        0: {  # wide flat cumulus
            'w': 140, 'h': 50,
            'bumps': [
                (18,36,14),(38,38,16),(60,38,18),(82,38,16),(104,38,16),(124,36,13),
                (28,26,13),(50,22,15),(72,24,14),(96,26,13),(114,28,11),
                (42,14,11),(62,10,12),(82,14,10),
            ],
            'base': (16,30,112,18), 'bottom': ((14,46),(128,46)),
            'arcs': [(35,32,11,8),(58,33,10,7),(82,32,11,8),(108,33,9,7)],
            'hi': [(40,12,5),(62,8,6),(80,13,4),(50,20,4)],
        },
        1: {  # tall puffy
            'w': 100, 'h': 70,
            'bumps': [
                (16,56,14),(34,58,16),(52,58,18),(70,58,16),(86,56,13),
                (24,44,14),(44,40,16),(64,42,14),(80,46,12),
                (34,30,13),(54,26,15),(72,32,12),
                (44,18,12),(60,12,13),(74,20,10),(52,6,10),
            ],
            'base': (12,48,80,20), 'bottom': ((10,66),(92,66)),
            'arcs': [(30,50,12,8),(55,48,10,7),(40,36,11,8),(62,34,9,7)],
            'hi': [(44,16,5),(60,10,6),(52,4,4),(34,28,4)],
        },
        2: {  # small round puff
            'w': 70, 'h': 42,
            'bumps': [
                (14,30,12),(30,32,14),(46,32,14),(60,30,11),
                (22,20,12),(38,16,13),(52,20,11),(36,8,10),
            ],
            'base': (10,26,52,14), 'bottom': ((8,38),(64,38)),
            'arcs': [(28,28,9,6),(48,27,8,6)],
            'hi': [(36,6,4),(22,18,3),(50,18,3)],
        },
        3: {  # elongated wispy
            'w': 160, 'h': 44,
            'bumps': [
                (16,32,13),(34,34,15),(54,34,16),(74,34,16),(94,34,16),
                (114,34,15),(134,34,14),(148,32,11),
                (26,22,12),(46,18,14),(66,20,13),(86,18,14),(106,20,13),(126,22,11),
                (56,10,11),(76,8,12),(96,10,11),
            ],
            'base': (14,28,138,14), 'bottom': ((12,40),(152,40)),
            'arcs': [(32,30,10,7),(56,28,9,6),(80,28,10,7),(106,30,9,6),(130,30,8,6)],
            'hi': [(46,16,5),(76,6,5),(96,8,4),(56,8,4)],
        },
        4: {  # medium bumpy
            'w': 110, 'h': 52,
            'bumps': [
                (16,40,14),(34,42,16),(54,42,17),(74,42,16),(92,40,13),
                (26,30,13),(46,26,15),(66,28,14),(84,30,12),
                (38,18,12),(56,14,13),(72,18,11),
            ],
            'base': (14,34,82,16), 'bottom': ((12,48),(98,48)),
            'arcs': [(32,36,10,7),(56,34,11,8),(78,36,9,7)],
            'hi': [(38,16,5),(56,12,5),(72,16,4),(28,28,3)],
        },
        5: {  # compact fluffy
            'w': 100, 'h': 48,
            'bumps': [
                (16,36,14),(34,38,15),(52,38,16),(70,38,15),(86,36,13),
                (26,26,13),(44,22,14),(62,24,13),(78,28,11),
                (36,14,11),(52,10,12),(66,16,10),
            ],
            'base': (14,30,76,16), 'bottom': ((12,44),(90,44)),
            'arcs': [(30,32,10,7),(54,30,10,7),(74,32,8,6)],
            'hi': [(36,12,4),(52,8,5),(66,14,3),(26,24,3)],
        },
        6: {  # chunky tower
            'w': 90, 'h': 56,
            'bumps': [
                (14,44,12),(30,46,14),(48,46,16),(66,46,14),(80,44,11),
                (22,34,13),(40,30,14),(58,32,13),(72,36,11),
                (32,22,12),(48,18,13),(62,24,10),
                (40,10,10),(54,8,11),
            ],
            'base': (12,38,72,16), 'bottom': ((10,52),(82,52)),
            'arcs': [(28,40,10,7),(50,38,10,7),(36,28,9,6),(56,26,8,6)],
            'hi': [(40,8,4),(54,6,5),(32,20,3),(48,16,4)],
        },
    }

    sid = shape_id % len(shapes)
    sh = shapes[sid]
    w, h = sh['w'], sh['h']
    s = pygame.Surface((w, h), pygame.SRCALPHA)

    # ── COLOUR PALETTE ────────────────────────────
    if vibrant:
        c_fill    = (240, 248, 255)
        c_inner   = (210, 232, 252)
        c_shadow  = (160, 200, 240)
        c_outline = ( 60, 110, 170)
        c_white   = (255, 255, 255)
    else:
        c_fill    = (225, 235, 248)
        c_inner   = (200, 215, 235)
        c_shadow  = (155, 175, 200)
        c_outline = ( 75, 100, 140)
        c_white   = (245, 250, 255)

    bumps = sh['bumps']

    # 1. Fill all bump circles
    for bx, by, br in bumps:
        pygame.draw.circle(s, c_fill, (bx, by), br)

    # 2. Fill base rect to close gaps
    bx2, by2, bw2, bh2 = sh['base']
    pygame.draw.rect(s, c_fill, (bx2, by2, bw2, bh2))

    # 3. Inner shadow on large bumps
    for bx, by, br in bumps:
        if br >= 12:
            pygame.draw.circle(s, c_inner, (bx+2, by+3), br-4)

    # 4. Bottom shadow strip
    bl = sh['bottom']
    sy = bl[0][1] - 5
    sx1, sx2 = bl[0][0] + 4, bl[1][0] - 4
    pygame.draw.rect(s, c_shadow,
        (sx1, sy, sx2 - sx1, 5), border_radius=3)

    # 5. White highlights on top bumps
    for hx, hy, hr in sh['hi']:
        pygame.draw.circle(s, c_white, (hx, hy), hr)

    # 6. Dark outline on each bump — cartoon style
    for bx, by, br in bumps:
        pygame.draw.circle(s, c_outline, (bx, by), br, 2)

    # 7. Flat bottom line
    pygame.draw.line(s, c_outline, sh['bottom'][0], sh['bottom'][1], 2)

    # 8. Inner decorative curve arcs
    for cx2, cy2, cw2, ch2 in sh['arcs']:
        pygame.draw.arc(s, c_outline,
            (cx2 - cw2//2, cy2 - ch2//2, cw2, ch2),
            math.radians(200), math.radians(340), 2)

    # 9. Edge puff lines
    for ebx, eby, ebr in [bumps[0], bumps[-1]]:
        pygame.draw.arc(s, c_outline,
            (ebx - ebr - 4, eby - 4, 10, 8),
            math.radians(180), math.radians(300), 1)

    # 10. Trampoline bounce arrow
    if vibrant:
        mid = w // 2
        bot = h - 2
        pygame.draw.line(s, c_outline,
            (mid - 8, bot), (mid, bot - 8), 2)
        pygame.draw.line(s, c_outline,
            (mid, bot - 8), (mid + 8, bot), 2)

    return s


def load_cloud_images(prefix):
    """Load custom cloud images from assets/ui/clouds/ matching a naming pattern.
    e.g. prefix='cloud_bg' loads cloud_bg_1.png, cloud_bg_2.png, etc.
    Returns a list of (path, Surface) tuples."""
    import os, re
    cloud_dir = "assets/ui/clouds"
    os.makedirs(cloud_dir, exist_ok=True)
    pattern = re.compile(
        rf"^{re.escape(prefix)}_(\d+)\.(png|jpg|jpeg)$",
        re.IGNORECASE)
    found = []
    try:
        for fname in sorted(os.listdir(cloud_dir)):
            if pattern.match(fname):
                path = os.path.join(cloud_dir, fname)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    found.append((path, img))
                except Exception:
                    pass
    except Exception:
        pass
    label = "background" if "bg" in prefix else "trampoline"
    print(f"[CLOUD] Found {len(found)} {label} cloud images")
    return found


def load_platform_images():
    """Load custom platform images from assets/ui/platforms/.
    Name them platform_1.png, platform_2.png, etc. They cycle across platforms.
    If no files found, procedural platforms are used instead."""
    import os, re
    plat_dir = "assets/ui/platforms"
    os.makedirs(plat_dir, exist_ok=True)
    pattern = re.compile(
        r"^platform_(\d+)\.(png|jpg|jpeg)$",
        re.IGNORECASE)
    found = []
    try:
        for fname in sorted(os.listdir(plat_dir)):
            if pattern.match(fname):
                path = os.path.join(plat_dir, fname)
                try:
                    img = pygame.image.load(
                        path).convert_alpha()
                    found.append(img)
                    print(f"[PLATFORM] Loaded: {path}")
                except Exception:
                    pass
    except Exception:
        pass
    print(f"[PLATFORM] Found {len(found)} custom images")
    return found


def load_obstacle_images():
    """Load custom barrel/box sprites from assets/obstacles/.
    Expects: barrel.png, box.png, and optionally box_cracked.png.
    Returns a dict with the loaded surfaces (or None if file missing)."""
    import os
    obs_dir = "assets/obstacles"
    os.makedirs(obs_dir, exist_ok=True)
    result = {'barrel': None, 'box': None, 'box_cracked': None}
    for key, fname in [('barrel', 'barrel.png'),
                        ('box', 'box.png'),
                        ('box_cracked', 'box_cracked.png')]:
        path = os.path.join(obs_dir, fname)
        try:
            img = pygame.image.load(path).convert_alpha()
            result[key] = img
            print(f"[OBSTACLE] Loaded: {path}")
        except Exception:
            result[key] = None
    return result


class Cloud(pygame.sprite.Sprite):
    """A cloud in the sky. Two types:
    - Background clouds (trampoline=False): just decoration, no collision
    - Trampoline clouds (trampoline=True): players bounce upward when landing on them
    Custom images go in assets/ui/clouds/ (cloud_bg_*.png or cloud_bounce_*.png)."""

    _cloud_index = 0  # class-level counter for cycling

    def __init__(self, x, y, trampoline=False,
                 shape_id=0, image_list=None):
        super().__init__()
        self.trampoline  = trampoline
        self.bounce_force = 820

        # Generate fallback surface (also sets target size)
        generated = create_cloud_surface(
            vibrant=trampoline, shape_id=shape_id)
        tw = generated.get_width()
        th = generated.get_height()

        if image_list and len(image_list) > 0:
            idx = Cloud._cloud_index % len(image_list)
            Cloud._cloud_index += 1
            path, raw_img = image_list[idx]
            ow, oh = raw_img.get_size()

            # Never force a fixed size — preserve natural shape
            # Target height only — width scales proportionally
            target_h = 60
            target_w = int(ow * (target_h / oh))

            # ── STRIP BLACK BACKGROUND ────────────────
            # Cloud PNGs may have solid black backgrounds (alpha=255)
            # instead of proper transparency. Strip them before scaling
            # so shape detection and rendering work correctly.

            # Only strip before scale if image is reasonably sized
            # Large images are stripped after scaling instead
            STRIP_BEFORE_SCALE = (ow * oh) < 500000  # ~700x700

            if STRIP_BEFORE_SCALE:
                try:
                    clean_surf = pygame.Surface(
                        (ow, oh), pygame.SRCALPHA)
                    clean_surf.blit(raw_img, (0, 0))

                    # Lock and scan for near-black pixels
                    clean_surf.lock()
                    for cy in range(oh):
                        for cx in range(ow):
                            r, g, b, a = clean_surf.get_at((cx, cy))
                            if r < 40 and g < 40 and b < 40:
                                clean_surf.set_at((cx, cy),
                                    (0, 0, 0, 0))
                    clean_surf.unlock()
                    raw_img = clean_surf
                    print(f"[CLOUD] Black bg stripped: {path}")
                except Exception as e:
                    print(f"[CLOUD] Strip failed ({e}), using original")

            # Scale after stripping
            self.image = pygame.transform.smoothscale(
                raw_img, (target_w, target_h))

            # For large images, strip after scaling (much faster)
            if not STRIP_BEFORE_SCALE:
                sw, sh = self.image.get_size()
                self.image.lock()
                for cy in range(sh):
                    for cx in range(sw):
                        r, g, b, a = self.image.get_at((cx, cy))
                        if r < 40 and g < 40 and b < 40:
                            self.image.set_at((cx, cy), (0, 0, 0, 0))
                self.image.unlock()
                print(f"[CLOUD] Black bg stripped post-scale: {path}")

            print(f"[CLOUD] Using {path} for cloud at ({x},{y})")
        else:
            self.image = generated

        self.rect = self.image.get_rect(topleft=(x, y))

        # For trampoline clouds with custom images — detect
        # actual solid top surface so bounce triggers correctly
        self.solid_x_offset = 0
        self.solid_w        = self.rect.width
        self.solid_y_offset = 0

        if trampoline and image_list and len(image_list) > 0:
            sy_off, cl, cr = _detect_solid_bounds(
                self.image,
                edge_inset=4,
                min_solid_fraction=0.2)
            self.solid_x_offset = cl
            self.solid_w        = max(16, cr - cl)
            self.solid_y_offset = sy_off
            print(f"[CLOUD] trampoline solid bounds: "
                  f"sy_off={sy_off} cl={cl} cr={cr}")

    def draw(self, surface, camera=None):
        surface.blit(self.image, self.rect)


class Ground:
    """Renders the ground, sky background, clouds, and the ground image.
    Loads custom images from assets/ui/ if available."""
    
    def __init__(self, tile_image):
        self.tile = tile_image
        self.rect = pygame.Rect(
            0, GROUND_Y, VIRTUAL_W, VIRTUAL_H - GROUND_Y)

        # ── BACKGROUND IMAGE SUPPORT ─────────────────
        self.bg_image = None
        bg_path = "assets/ui/background.jpg"
        try:
            from PIL import Image
            pil_img = Image.open(bg_path).convert("RGB")
            orig_w, orig_h = pil_img.size

            # Scale to fill screen preserving aspect ratio (cover mode)
            scale = max(VIRTUAL_W / orig_w, VIRTUAL_H / orig_h)
            scaled_w = int(orig_w * scale)
            scaled_h = int(orig_h * scale)

            # LANCZOS resampling — highest quality
            pil_img = pil_img.resize((scaled_w, scaled_h), Image.LANCZOS)

            # Center-crop to exact screen size
            cx = (scaled_w - VIRTUAL_W) // 2
            cy = (scaled_h - VIRTUAL_H) // 2
            pil_img = pil_img.crop((cx, cy, cx + VIRTUAL_W, cy + VIRTUAL_H))

            # Convert PIL → pygame
            self.bg_image = pygame.image.fromstring(
                pil_img.tobytes(), (VIRTUAL_W, VIRTUAL_H), "RGB").convert()

            print(f"[BG] Loaded (LANCZOS): {orig_w}x{orig_h} -> 1280x720")
        except FileNotFoundError:
            self.bg_image = None
            print("[BG] No background.jpg found — using sky color.")

        self.clouds = []

        # ── GROUND IMAGE SUPPORT ─────────────────────
        self.ground_image = None
        self.ground_image_rect = None
        ground_img_path = "assets/ui/ground.png"
        try:
            raw = pygame.image.load(ground_img_path).convert_alpha()
            orig_w, orig_h = raw.get_size()

            # Find the first row that has non-transparent pixels
            # (skip the empty/transparent space at the top of the image)
            first_content_y = 0
            for row_y in range(orig_h):
                for col_x in range(0, orig_w, orig_w // 20):  # sample 20 columns
                    if raw.get_at((col_x, row_y))[3] > 10:  # alpha > 10
                        first_content_y = row_y
                        break
                else:
                    continue
                break

            # Crop out the transparent top
            content_h = orig_h - first_content_y
            if content_h < 10:
                content_h = orig_h
                first_content_y = 0
            cropped = raw.subsurface(pygame.Rect(
                0, first_content_y, orig_w, content_h))

            # ── SIZE from constants.py ──
            target_w = int(VIRTUAL_W * GROUND_IMG_SCALE)
            target_h = int(content_h * (target_w / orig_w))

            # Ensure minimum height so the ground looks substantial
            min_h = 120
            if target_h < min_h:
                target_h = min_h

            self.ground_image = pygame.transform.smoothscale(
                cropped, (target_w, target_h))

            # ── POSITION from constants.py ──
            img_x = (VIRTUAL_W - target_w) // 2 + GROUND_IMG_X_OFFSET
            img_y = int(GROUND_Y - target_h * GROUND_SURFACE_FRACTION) + GROUND_IMG_Y_OFFSET
            self.ground_image_rect = pygame.Rect(img_x, img_y, target_w, target_h)

            print(f"[GROUND] img {target_w}x{target_h} placed at ({img_x},{img_y}) | "
                  f"walkable line at GROUND_Y={GROUND_Y}")
        except Exception as e:
            self.ground_image = None
            self.ground_image_rect = None
            print(f"[GROUND] No ground.png -- using default tiles. ({e})")
    
    def draw(self, surface, camera=None):
        """Draw background then ground tiles."""
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            from src.constants import SKY_COLOR
            surface.fill(SKY_COLOR)

        # Draw ground tiles at bottom
        if self.ground_image and self.ground_image_rect:
            surface.blit(self.ground_image, self.ground_image_rect)
        else:
            tile_w = self.tile.get_width()
            for x in range(0, VIRTUAL_W, tile_w):
                surface.blit(self.tile, (x, GROUND_Y))


        # Draw clouds on top of background
        for cloud in self.clouds:
            surface.blit(cloud['surf'],
                (cloud['x'], cloud['y']))
class Platform(pygame.sprite.Sprite):
    """A floating platform players can jump through from below and land on top of.
    If a custom image is provided, the collision zone is auto-detected from the pixels."""
    
    def __init__(self, x, y, width, height, image, custom_image=None):
        super().__init__()
        self.collision_height = height  # 20px — physics thickness

        if custom_image is not None:
            orig_w, orig_h = custom_image.get_size()

            # Scale to platform width, preserve aspect ratio
            visual_h = int(orig_h * (width / orig_w))
            visual_h = max(visual_h, height)
            scaled = pygame.transform.smoothscale(
                custom_image, (width, visual_h))
            self.image = scaled

            # ── AUTO-DETECT TRUE SURFACE ──────────────
            # Sample the scaled image to find:
            #   surface_y_offset — how many px from top until real rock
            #   col_left, col_right — actual solid pixel horizontal bounds
            #
            # We sample every 4px for speed (accurate enough)

            surface_y_offset = 0
            ALPHA_THRESHOLD = 30  # pixels below this alpha = transparent

            # Step 1: Find first row from top that has solid pixels
            # across at least 30% of the width — avoids single grass tips
            min_solid_px = max(4, width // 3)
            for row in range(visual_h):
                solid_count = 0
                for col in range(0, width, 4):
                    try:
                        if scaled.get_at((col, row))[3] > ALPHA_THRESHOLD:
                            solid_count += 1
                    except Exception:
                        pass
                if solid_count * 4 >= min_solid_px:
                    surface_y_offset = row
                    break

            # Step 2: Find leftmost solid column
            col_left = 0
            for col in range(0, width, 2):
                found = False
                for row in range(surface_y_offset,
                                 min(surface_y_offset + 30, visual_h)):
                    try:
                        if scaled.get_at((col, row))[3] > ALPHA_THRESHOLD:
                            found = True
                            break
                    except Exception:
                        pass
                if found:
                    col_left = col
                    break

            # Step 3: Find rightmost solid column
            col_right = width
            for col in range(width - 1, 0, -2):
                found = False
                for row in range(surface_y_offset,
                                 min(surface_y_offset + 30, visual_h)):
                    try:
                        if scaled.get_at((col, row))[3] > ALPHA_THRESHOLD:
                            found = True
                            break
                    except Exception:
                        pass
                if found:
                    col_right = col + 1
                    break

            # Add a small inset margin to avoid edge hovering
            EDGE_INSET = 8
            col_left  = min(col_left  + EDGE_INSET, width // 2)
            col_right = max(col_right - EDGE_INSET, width // 2 + 1)
            solid_w   = max(20, col_right - col_left)

            # collision rect: inset horizontally, at true surface Y
            self.rect = pygame.Rect(
                x + col_left,
                y + surface_y_offset,
                solid_w,
                self.collision_height)

            # visual rect: full image from platform anchor point
            # Simpler: visual starts at x,y and draws full image
            self.visual_rect = pygame.Rect(x, y, width, visual_h)

            print(f"[PLATFORM] surface_y_offset={surface_y_offset} "
                  f"col_left={col_left} col_right={col_right} "
                  f"solid_w={solid_w} "
                  f"collision_rect={self.rect}")

        else:
            # Default fallback — no custom image, simple rect
            self.image = pygame.transform.smoothscale(
                image, (width, height))
            self.rect = pygame.Rect(x, y, width, self.collision_height)
            self.visual_rect = pygame.Rect(x, y, width, height)
    
    def draw(self, surface, camera):
        # Draw at visual_rect not self.rect
        # so the full image shows, not just the 20px collision slice
        surface.blit(self.image, self.visual_rect)


class Barrel(pygame.sprite.Sprite):
    """An indestructible barrel that sits on the ground. Players can stand on top of it.
    Uses custom image from assets/obstacles/barrel.png if available."""
    
    def __init__(self, x, y, custom_image=None):
        super().__init__()
        from src.constants import (
            BARREL_WIDTH, BARREL_HEIGHT, GROUND_Y, create_barrel_art,
            BARREL_Y_OFFSET)
        self.width  = BARREL_WIDTH
        self.height = BARREL_HEIGHT

        if custom_image is not None:
            orig_w, orig_h = custom_image.get_size()
            target_h = BARREL_HEIGHT
            target_w = int(orig_w * (target_h / orig_h))
            scaled = pygame.transform.smoothscale(
                custom_image, (target_w, target_h))
            self.image = scaled
            self.width = target_w

            # Detect actual solid bounds from custom image
            sy_off, cl, cr = _detect_solid_bounds(
                scaled, edge_inset=6, min_solid_fraction=0.3)
            solid_w = max(16, cr - cl)

            # Full visual rect — image bottom sits at GROUND_Y + offset
            self.rect = pygame.Rect(
                x, GROUND_Y - target_h + BARREL_Y_OFFSET, target_w, target_h)

            # Narrowed top collision zone — used by check_barrel_collision
            # x offset is relative to self.rect.x
            self.solid_x_offset = cl
            self.solid_w        = solid_w
            self.solid_y_offset = sy_off

            print(f"[BARREL] sy_off={sy_off} cl={cl} cr={cr} "
                  f"solid_w={solid_w}")
        else:
            self.image = create_barrel_art(self.width, self.height)
            self.rect  = pygame.Rect(
                x, GROUND_Y - self.height + BARREL_Y_OFFSET, self.width, self.height)
            # Default: standard inset (matches old hardcoded +8 logic)
            self.solid_x_offset = 8
            self.solid_w        = self.width - 16
            self.solid_y_offset = 0

        self.platform_rect = pygame.Rect(
            self.rect.x + self.solid_x_offset,
            self.rect.y  + self.solid_y_offset,
            self.solid_w,
            4)
    
    def draw(self, surface, camera):
        """Draw barrel."""
        surface.blit(self.image, self.rect)


class DestructibleBox(pygame.sprite.Sprite):
    """A wooden crate that takes damage from bullets and melee attacks.
    When destroyed (HP reaches 0), it drops a weapon pickup and respawns after a timer.
    Shows a cracked texture at half HP as visual feedback."""

    def __init__(self, x, y, custom_image=None, custom_cracked=None):
        super().__init__()
        from src.constants import (
            BOX_WIDTH, BOX_HEIGHT, GROUND_Y,
            BOX_MAX_HP, BOX_RESPAWN_TIME, BOX_Y_OFFSET
        )
        self.base_x = x
        self.base_y = GROUND_Y - BOX_HEIGHT + BOX_Y_OFFSET
        self.max_hp = BOX_MAX_HP
        self.hp = BOX_MAX_HP
        self.respawn_timer = 0.0
        self.BOX_RESPAWN_TIME = BOX_RESPAWN_TIME
        self.destroyed = False
        self.shotgun_spawned = False

        # Build intact image
        if custom_image is not None:
            orig_w, orig_h = custom_image.get_size()
            target_h = BOX_HEIGHT
            target_w = int(orig_w * (target_h / orig_h))
            self.image_intact = pygame.transform.smoothscale(
                custom_image, (target_w, target_h))
        else:
            self.image_intact = self._make_box_art(
                BOX_WIDTH, BOX_HEIGHT, cracked=False)

        # Build cracked image (damage stage 2)
        if custom_cracked is not None:
            orig_w, orig_h = custom_cracked.get_size()
            target_h = BOX_HEIGHT
            target_w = int(orig_w * (target_h / orig_h))
            self.image_cracked = pygame.transform.smoothscale(
                custom_cracked, (target_w, target_h))
        else:
            self.image_cracked = self._make_box_art(
                BOX_WIDTH, BOX_HEIGHT, cracked=True)

        self.image = self.image_intact

        # Detect solid bounds from custom image if available
        # fallback uses standard box inset
        if custom_image is not None:
            sy_off, cl, cr = _detect_solid_bounds(
                self.image_intact, edge_inset=5, min_solid_fraction=0.3)
            self.solid_x_offset = cl
            self.solid_w        = max(16, cr - cl)
            self.solid_y_offset = sy_off
        else:
            self.solid_x_offset = 6
            self.solid_w        = BOX_WIDTH - 12
            self.solid_y_offset = 0

        self.rect = pygame.Rect(
            self.base_x,
            self.base_y,
            self.image.get_width(),
            BOX_HEIGHT)

    def _make_box_art(self, w, h, cracked=False):
        """Draw a procedural wooden crate. cracked=True adds red crack lines."""
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        body   = (180, 130, 70)
        dark   = (120,  80, 35)
        light  = (220, 170, 100)
        outline= ( 60,  35, 10)
        plank  = (150, 105, 55)

        pygame.draw.rect(s, body,    (2, 4, w-4, h-6), border_radius=3)
        pygame.draw.rect(s, outline, (2, 4, w-4, h-6), 2, border_radius=3)

        # Top face
        pygame.draw.rect(s, light, (4, 4, w-8, 10), border_radius=2)
        pygame.draw.line(s, outline, (4, 14), (w-4, 14), 1)

        # Plank lines
        for px in [w//3, 2*w//3]:
            pygame.draw.line(s, plank, (px, 4), (px, h-4), 1)
        # Cross tape
        pygame.draw.line(s, dark, (4, 16), (w-4, h-4), 2)
        pygame.draw.line(s, dark, (w-4, 16), (4, h-4), 2)

        if cracked:
            crack = (200, 40, 40, 180)
            crack_s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.line(crack_s, crack, (w//2-4, 10), (w//2+6, h-8), 3)
            pygame.draw.line(crack_s, crack, (w//4, h//2), (3*w//4, h//2+8), 2)
            pygame.draw.line(crack_s, crack, (w//2+4, 10), (w//2-2, h//3), 2)
            s.blit(crack_s, (0, 0))
        return s

    def take_damage(self, amount):
        """Apply damage. Returns 'destroyed', 'cracked', 'hit', or 'none'."""
        if self.destroyed:
            return 'none'
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.destroyed = True
            self.shotgun_spawned = False
            return 'destroyed'
        elif self.hp <= self.max_hp // 2:
            self.image = self.image_cracked
            return 'cracked'
        return 'hit'

    def update(self, dt):
        """Tick respawn timer when destroyed."""
        if self.destroyed:
            self.respawn_timer += dt
            if self.respawn_timer >= self.BOX_RESPAWN_TIME:
                self._respawn()

    def _respawn(self):
        """Reset box to full HP at original position."""
        self.hp = self.max_hp
        self.destroyed = False
        self.shotgun_spawned = False
        self.respawn_timer = 0.0
        self.image = self.image_intact
        from src.constants import BOX_HEIGHT
        self.rect = pygame.Rect(
            self.base_x, self.base_y,
            self.image.get_width(), BOX_HEIGHT)

    def draw(self, surface, camera):
        if self.destroyed:
            return

        # Draw the box image
        surface.blit(self.image, self.rect)

        # Only draw HP bar if box has taken damage
        if self.hp >= self.max_hp:
            return

        # ── BOX HP BAR ────────────────────────────
        # Bar sits 8px above the box, centered on it
        bar_w    = self.rect.width + 4
        bar_h    = 5
        bar_x    = self.rect.centerx - bar_w // 2
        bar_y    = self.rect.top - bar_h - 7

        fraction = self.hp / self.max_hp

        # Bar color: green → orange → red (matches player HUD)
        if fraction > 0.6:
            fill_color = (55, 200, 70)
        elif fraction > 0.3:
            fill_color = (230, 140, 20)
        else:
            fill_color = (210, 35, 35)

        # Thin white outer border — 1px only
        pygame.draw.rect(surface, (220, 220, 220),
            (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2),
            border_radius=3)

        # Dark track background
        pygame.draw.rect(surface, (30, 20, 20),
            (bar_x, bar_y, bar_w, bar_h),
            border_radius=2)

        # Colored fill — left to right
        fill_w = max(0, int(fraction * bar_w))
        if fill_w > 2:
            pygame.draw.rect(surface, fill_color,
                (bar_x, bar_y, fill_w, bar_h),
                border_radius=2)
            # Shine stripe
            shine = pygame.Surface(
                (max(1, fill_w - 2), max(1, bar_h // 3)),
                pygame.SRCALPHA)
            shine.fill((255, 255, 255, 60))
            surface.blit(shine, (bar_x + 1, bar_y + 1))


def create_arena(assets):
    """Build the entire game world: platforms, barrel, box, clouds.
    Loads custom images where available and sets up all collision zones."""
    
    import random

    # Load custom platform images
    plat_images = load_platform_images()

    # ── FIXED PLATFORM POSITIONS ──────────────────
    # These never change — consistent layout every session.
    # Reachability chain:
    #   ground(630) → barrel(545)/box(558)
    #   → low platforms (y≈500) reachable from barrel/box top
    #   → mid platforms (y≈400) reachable from low platforms
    #   → center high (y≈300) reachable from mid platforms
    #
    # (x_left, y_top, width) — x_left is left edge of platform
    fixed_platforms = [
        ( 55, 315, 150),   # far left — low, reachable from ground/barrel
        ( 900, 410, 155),   # left-center low — stepping stone up
        ( 550, 205, 170),   # center high — top of the map
        ( 250, 400, 155),   # right-center low — stepping stone up
        (1076, 275, 150),   # far right — low, reachable from ground/box
    ]

    platforms = []
    # Per-platform player Y offsets
    from src.constants import (
        PLAYER_PLATFORM_1_Y_OFFSET, PLAYER_PLATFORM_2_Y_OFFSET,
        PLAYER_PLATFORM_3_Y_OFFSET, PLAYER_PLATFORM_4_Y_OFFSET,
        PLAYER_PLATFORM_5_Y_OFFSET, PLAYER_BARREL_Y_OFFSET,
        PLAYER_BOX_Y_OFFSET
    )
    plat_offsets = [
        PLAYER_PLATFORM_1_Y_OFFSET, PLAYER_PLATFORM_2_Y_OFFSET,
        PLAYER_PLATFORM_3_Y_OFFSET, PLAYER_PLATFORM_4_Y_OFFSET,
        PLAYER_PLATFORM_5_Y_OFFSET,
    ]
    for i, (px, py, pw) in enumerate(fixed_platforms):
        # Pick custom image cycling through list
        custom = None
        if plat_images:
            custom = plat_images[i % len(plat_images)]

        p = Platform(px, py, pw, 20,
                     assets['platform'],
                     custom_image=custom)
        p.player_y_offset = plat_offsets[i] if i < len(plat_offsets) else 0
        platforms.append(p)

    # Load obstacle images
    obs_images = load_obstacle_images()

    # Create single barrel + destructible box
    from src.constants import BARREL_X, BOX_X
    barrel = Barrel(BARREL_X, GROUND_Y,
                    custom_image=obs_images['barrel'])
    barrel.player_y_offset = PLAYER_BARREL_Y_OFFSET
    barrels = [barrel]

    # Destructible box — slightly right of center
    box = DestructibleBox(
        BOX_X, GROUND_Y,
        custom_image=obs_images['box'],
        custom_cracked=obs_images['box_cracked']
    )
    box.player_y_offset = PLAYER_BOX_Y_OFFSET
    
    # Load custom cloud images (if any)
    bg_images     = load_cloud_images("cloud_bg")
    bounce_images = load_cloud_images("cloud_bounce")

    # Background decorative clouds — no collision
    Cloud._cloud_index = 0
    bg_clouds = [
        Cloud( -60,  120, trampoline=False, shape_id=0,
               image_list=bg_images),
        Cloud(800,  95, trampoline=False, shape_id=2,
               image_list=bg_images),
        Cloud(1150,  85, trampoline=False, shape_id=3,
               image_list=bg_images),
        Cloud(400, 50, trampoline=False, shape_id=5,
               image_list=bg_images),
    ]

    # Trampoline clouds — vibrant, interactive
    Cloud._cloud_index = 0
    from src.constants import (
        PLAYER_CLOUD_1_Y_OFFSET, PLAYER_CLOUD_2_Y_OFFSET,
        CLOUD_1_EDGE_LEFT, CLOUD_1_EDGE_RIGHT,
        CLOUD_2_EDGE_LEFT, CLOUD_2_EDGE_RIGHT
    )
    cloud_1 = Cloud(730, 307, trampoline=True, shape_id=4,
                    image_list=bounce_images)
    cloud_1.player_y_offset = PLAYER_CLOUD_1_Y_OFFSET
    cloud_1.edge_left  = CLOUD_1_EDGE_LEFT
    cloud_1.edge_right = CLOUD_1_EDGE_RIGHT

    cloud_2 = Cloud(310, 245, trampoline=True, shape_id=6,
                    image_list=bounce_images)
    cloud_2.player_y_offset = PLAYER_CLOUD_2_Y_OFFSET
    cloud_2.edge_left  = CLOUD_2_EDGE_LEFT
    cloud_2.edge_right = CLOUD_2_EDGE_RIGHT

    trampoline_clouds = [cloud_1, cloud_2]

    return platforms, barrels, box, bg_clouds, trampoline_clouds
