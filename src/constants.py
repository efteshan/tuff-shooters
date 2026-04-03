# src/constants.py — COMPLETE

import pygame

# Screen
SCREEN_W        = 1280
SCREEN_H        = 720

# Virtual Canvas
VIRTUAL_W       = 1280
VIRTUAL_H       = 720

# Players
PLAYER_WIDTH    = 48
PLAYER_HEIGHT   = 72
PLAYER_SPEED    = 260
JUMP_FORCE      = 620
FAST_FALL_SPEED = 700
MAX_FALL_SPEED  = 900
GROUND_FRICTION = 0.82

# ═══════════════════════════════════════════════════════════════
# PLAYER Y OFFSETS — Adjust how players sit on each surface
# ═══════════════════════════════════════════════════════════════
# Positive = push player DOWN (into/onto surface)
# Negative = push player UP (away from surface)
PLAYER_GROUND_Y_OFFSET     = 2
PLAYER_PLATFORM_1_Y_OFFSET = 0   # far left platform  (x=55,  y=315)
PLAYER_PLATFORM_2_Y_OFFSET = 2   # right-low platform (x=900, y=410)
PLAYER_PLATFORM_3_Y_OFFSET = 0   # center high        (x=550, y=205)
PLAYER_PLATFORM_4_Y_OFFSET = 0   # left-mid platform  (x=250, y=400)
PLAYER_PLATFORM_5_Y_OFFSET = 2   # far right platform (x=1076,y=275)
PLAYER_BARREL_Y_OFFSET     = 8
PLAYER_BOX_Y_OFFSET        = 8

# ═══════════════════════════════════════════════════════════════
# PLAYER WALKING LEVEL — The Y line where players walk/stand
# ═══════════════════════════════════════════════════════════════
# Decrease = players walk HIGHER on screen (move up)
# Increase = players walk LOWER on screen (move down)
GROUND_Y        = 570

CLIFF_DEATH_Y   = 715    # player.rect.bottom >= this triggers cliff death

# ═══════════════════════════════════════════════════════════════
# GROUND IMAGE TUNING — Change these to resize/reposition ground
# ═══════════════════════════════════════════════════════════════
GROUND_IMG_SCALE        = 0.58   # Image width as fraction of screen (0.40 = small, 1.0 = full width)
GROUND_IMG_X_OFFSET     = 0      # Shift image left (-) or right (+) from center, in pixels
GROUND_IMG_Y_OFFSET     = 14     # Shift image up (-) or down (+) from auto position, in pixels
GROUND_SURFACE_FRACTION = 0.20   # Where GROUND_Y sits in the image (0.0 = top, 0.5 = middle, 1.0 = bottom)

# ═══════════════════════════════════════════════════════════════
# CLIFF / FALL-OFF EDGES — Where the player falls off the ground
# ═══════════════════════════════════════════════════════════════
# Decrease GROUND_LEFT = player falls off sooner on the LEFT side
# Increase GROUND_LEFT = player can walk further LEFT before falling
# Increase GROUND_RIGHT = player can walk further RIGHT before falling
# Decrease GROUND_RIGHT = player falls off sooner on the RIGHT side
GROUND_LEFT     = 270    # left cliff edge (pixels from left screen edge)
GROUND_RIGHT    = 1005   # right cliff edge (pixels from left screen edge)

# Barrel size (taller than player by 23 pixels)
BARREL_WIDTH    = 58  # Widest point in the middle
BARREL_HEIGHT   = 85  # Slightly taller than 72px player

# Combat
BULLET_SPEED    = 1500
BULLET_DAMAGE   = 7
MAX_AMMO        = 37
KNIFE_DAMAGE    = 10
KNIFE_RANGE     = 55
KNIFE_COOLDOWN  = 0.35

DASH_SPEED      = 800
DASH_DURATION   = 0.2
DASH_COOLDOWN   = 2

HIT_STUN_DURATION = 0.2
KNOCKBACK_FORCE   = 300

# ── OBSTACLES ────────────────────────────────
# Single barrel — slightly left of screen center
BARREL_X        = 500          # shifted further left of center
# Single box — slightly right of screen center
BOX_X           = 760          # shifted further right of center
BOX_WIDTH       = 60
BOX_HEIGHT      = 74
BOX_MAX_HP      = 50           # box destroyed at 0 HP
BOX_RESPAWN_TIME = 20.0        # seconds until box reappears after burst

# ═══════════════════════════════════════════════════════════════
# OBSTACLE Y OFFSET — Move barrel and box up(-) or down(+)
# ═══════════════════════════════════════════════════════════════
# These shift the barrel/box independently from GROUND_Y.
# 0 = sits exactly on the walking level
# -20 = floats 20px above the walking level
# +20 = sinks 20px below the walking level
BARREL_Y_OFFSET = 2
BOX_Y_OFFSET    = 2

# ═══════════════════════════════════════════════════════════════
# BARREL / BOX FALLING EDGE OFFSETS
# ═══════════════════════════════════════════════════════════════
# Controls where the player falls off the top of barrel/box.
# Increase = player falls off sooner (narrower walkable top)
# Decrease / negative = player can walk further toward the edge
BARREL_EDGE_LEFT   = 10
BARREL_EDGE_RIGHT  = 13
BOX_EDGE_LEFT      = 23
BOX_EDGE_RIGHT     = 13

# ═══════════════════════════════════════════════════════════════
# TRAMPOLINE CLOUD OFFSETS
# ═══════════════════════════════════════════════════════════════
# Player Y offsets (adjust the bounce trigger point):
#   Positive = trigger lower, Negative = trigger higher
PLAYER_CLOUD_1_Y_OFFSET = 25   # cloud at (730, 305)
PLAYER_CLOUD_2_Y_OFFSET = 25   # cloud at (310, 245)
# Edge offsets (narrowing the bounce zone):
#   Increase = player bounces only from narrower center area
CLOUD_1_EDGE_LEFT   = -25
CLOUD_1_EDGE_RIGHT  = 0
CLOUD_2_EDGE_LEFT   = -10
CLOUD_2_EDGE_RIGHT  = -10

# ═══════════════════════════════════════════════════════════════
# JUMP ANIMATION TUNING
# ═══════════════════════════════════════════════════════════════
# Phase velocity thresholds (vel_y values)
JUMP_LAUNCH_VEL     = -400    # below this = launch burst
JUMP_RISE_VEL       = -100    # between launch and this = rising
JUMP_FALL_VEL       = 100     # above this = falling

# Leg angles per phase (degrees)
JUMP_LEG_LAUNCH     = 25      # tucked on launch
JUMP_LEG_RISE       = 15      # spread while rising
JUMP_LEG_APEX       = 20      # wide spread at peak
JUMP_LEG_FALL       = 18      # braced forward on fall
JUMP_LEG_LAND       = 30      # deep bend on landing

# Arm angles per phase (degrees)
JUMP_ARM_LAUNCH     = -15     # swept back
JUMP_ARM_RISE       = 20      # raised up
JUMP_ARM_APEX       = 30      # spread wide
JUMP_ARM_FALL       = 25      # trailing up
JUMP_ARM_LAND       = 15      # swept forward

# Torso lean per phase (degrees)
JUMP_TORSO_LAUNCH   = -4      # lean back
JUMP_TORSO_FALL     = 5       # lean forward
JUMP_TORSO_LAND     = 6       # compress on land

# Head tilt per phase (degrees)
JUMP_HEAD_LAUNCH    = -6      # look up
JUMP_HEAD_FALL      = 6       # look down

# Lerp speeds — higher = snappier, lower = smoother
# Different speeds per body part for overlapping action
JUMP_LERP_LEGS      = 8.0     # legs lead — moderate speed
JUMP_LERP_TORSO     = 7.0     # follows legs
JUMP_LERP_ARMS      = 6.0     # trails behind — smooth
JUMP_LERP_HEAD      = 5.0     # slowest — naturalistic lag

# Land recovery duration (seconds)
JUMP_LAND_DURATION  = 0.20

# ── SHOTGUN ──────────────────────────────────
SHOTGUN_PELLETS       = 7      # pellets per shot
SHOTGUN_SPREAD_DEG    = 25     # half-angle of spread cone in degrees
SHOTGUN_PELLET_DAMAGE = 8      # damage per pellet
SHOTGUN_PELLET_SPEED  = 600    # px/s initial pellet speed
SHOTGUN_MAX_RANGE     = 320    # px — pellets die beyond this distance
SHOTGUN_MIN_RANGE     = 60     # px — pellets do 0 damage closer than this
SHOTGUN_COOLDOWN      = 1.2    # seconds between shots
SHOTGUN_AMMO          = 5      # reloads (each reload = full pellet spread)
SHOTGUN_PICKUP_LIFETIME = 10.0 # seconds shotgun stays on ground before despawn
SHOTGUN_ICON_COLOR    = (180, 80, 30)  # orange-brown for HUD icon

# ── BAZOOKA ──────────────────────────────────
BAZOOKA_SPEED         = 450
BAZOOKA_DAMAGE        = 25     # Direct hit damage
BAZOOKA_SPLASH_DAMAGE = 15     # Splash damage
BAZOOKA_SPLASH_RADIUS = 120
BAZOOKA_COOLDOWN      = 1.5
BAZOOKA_AMMO          = 3
BAZOOKA_PICKUP_LIFETIME = 10.0
BAZOOKA_ICON_COLOR    = (80, 120, 80) # green for HUD icon

# Physics
GRAVITY         = 1800

# Camera
ZOOM_MIN        = 0.65
ZOOM_MAX        = 1.0
ZOOM_SPEED      = 2.5

# Pickups
HEALTH_PACK_VALUE    = 30
HEALTH_SPAWN_MIN     = 18.0
HEALTH_SPAWN_MAX     = 25.0
AMMO_SPAWN_MIN       = 8.0
AMMO_SPAWN_MAX       = 12.0
AMMO_PACK_LIFETIME_MIN = 3.0
AMMO_PACK_LIFETIME_MAX = 5.0
MEDKIT_LIFETIME_MIN    = 8.0
MEDKIT_LIFETIME_MAX    = 12.0

# ═══════════════════════════════════════════════════════════════
# CUSTOM PICKUP IMAGE SIZES — Change to resize custom images
# ═══════════════════════════════════════════════════════════════
# Place custom images at:
#   assets/pickups/medkit.png   — custom medkit / health pack
#   assets/pickups/ammo_box.png — custom ammo box
# If the file is missing, procedural pixel art is used instead.
# Width and height below control the DISPLAY size (pixels).
MEDKIT_DISPLAY_W     = 32
MEDKIT_DISPLAY_H     = 28
AMMOBOX_DISPLAY_W    = 32
AMMOBOX_DISPLAY_H    = 28

# ═══════════════════════════════════════════════════════════════
# PICKUP SPAWN POSITION OFFSETS — Fine-tune where pickups appear
# ═══════════════════════════════════════════════════════════════
# GROUND offsets: shift pickups on the ground level
#   Y: negative = higher (away from ground), positive = lower (into ground)
#   X: negative = shift left, positive = shift right
PICKUP_GROUND_Y_OFFSET  = 0
PICKUP_GROUND_X_OFFSET  = 0
# PLATFORM offsets: shift pickups on platforms
#   Y: negative = higher (away from platform), positive = lower (onto platform)
#   X: negative = shift left, positive = shift right
PICKUP_PLATFORM_Y_OFFSET = 6
PICKUP_PLATFORM_X_OFFSET = 0

# KO
KO_DISPLAY_DURATION  = 3.0

# Colors
SKY_COLOR       = (100, 140, 200)
GROUND_COLOR    = (80, 60, 40)
P1_COLOR        = (60, 120, 220)
P2_COLOR        = (220, 60, 60)

# Asset Paths
IMG_P1_HEAD       = "assets/sprites/p1_head.png"
IMG_P1_TORSO      = "assets/sprites/p1_torso.png"
IMG_P1_ARM_R      = "assets/sprites/p1_arm_right.png"
IMG_P1_ARM_L      = "assets/sprites/p1_arm_left.png"
IMG_P1_LEG_R      = "assets/sprites/p1_leg_right.png"
IMG_P1_LEG_L      = "assets/sprites/p1_leg_left.png"

IMG_P2_HEAD       = "assets/sprites/p2_head.png"
IMG_P2_TORSO      = "assets/sprites/p2_torso.png"
IMG_P2_ARM_R      = "assets/sprites/p2_arm_right.png"
IMG_P2_ARM_L      = "assets/sprites/p2_arm_left.png"
IMG_P2_LEG_R      = "assets/sprites/p2_leg_right.png"
IMG_P2_LEG_L      = "assets/sprites/p2_leg_left.png"

IMG_PLATFORM      = "assets/sprites/platform.png"
IMG_GROUND        = "assets/sprites/ground_tile.png"
IMG_HEALTH_PACK   = "assets/pickups/health_pack.png"
IMG_AMMO_BOX      = "assets/pickups/ammo_box.png"

GIF_BLOOD_STRIP   = "assets/effects/blood_strip.png"
GIF_KO_STRIP      = "assets/effects/ko_strip.png"
GIF_BLOOD_FRAMES  = 4
GIF_KO_FRAMES     = 6

IMG_MENU_BG       = "assets/ui/menu_bg.png"
IMG_PAUSE_ICON    = "assets/ui/pause_icon.png"

# Controls
CONTROLS = {
    "p1": {
        "left":  pygame.K_a,
        "right": pygame.K_d,
        "jump":  pygame.K_w,
        "crouch": pygame.K_s,
        "shoot": pygame.K_c,
        "knife": pygame.K_v,
        "dash":  pygame.K_e,
    },
    "p2": {
        "left":  pygame.K_j,
        "right": pygame.K_l,
        "jump":  pygame.K_i,
        "crouch": pygame.K_k,
        "shoot": pygame.K_n,
        "knife": pygame.K_b,
        "dash":  pygame.K_o,
    }
}

# Pause button rect
PAUSE_BTN_RECT = None  # Will be initialized as pygame.Rect(SCREEN_W//2 - 50, 10, 100, 36)


def create_barrel_art(width: int, height: int) -> pygame.Surface:
    import math
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    cx = width // 2

    # ── PALETTE ────────────────────────────────────
    outline     = ( 35,  20,   8)   # dark cartoon outline
    wood_edge   = ( 85,  45,  15)   # darkest edge of stave
    wood_shadow = (120,  65,  20)   # shadow side stave
    wood_mid    = (165,  95,  30)   # mid stave tone
    wood_light  = (210, 140,  50)   # lit stave
    wood_bloom  = (240, 185,  80)   # center light bloom
    ring_dark   = ( 38,  34,  28)   # ring shadow
    ring_mid    = ( 72,  66,  54)   # ring body
    ring_light  = (115, 108,  88)   # ring highlight
    ring_out    = ( 25,  20,  12)   # ring outline
    top_fill    = (155, 100,  35)   # flat closed top surface
    top_dark    = ( 90,  55,  18)   # top surface shadow edge
    top_out     = ( 35,  20,   8)   # top outline

    # ── SILHOUETTE ────────────────────────────────
    def bx(y_pos):
        t    = y_pos / height
        bulge = math.sin(t * math.pi)
        h_top = 16
        h_mid = 27
        h     = h_top + (h_mid - h_top) * bulge
        return int(cx - h), int(cx + h)

    # ── STEP 1: WOOD BODY ROW BY ROW ──────────────
    for y in range(2, height):
        lx, rx = bx(y)
        if rx <= lx:
            continue
        span = rx - lx
        for px in range(lx, rx + 1):
            t = (px - lx) / max(span, 1)
            # Light blooms from center-left like reference
            if   t < 0.08: c = wood_edge
            elif t < 0.20: c = wood_shadow
            elif t < 0.35: c = wood_mid
            elif t < 0.50: c = wood_light
            elif t < 0.62: c = wood_bloom
            elif t < 0.72: c = wood_light
            elif t < 0.82: c = wood_mid
            elif t < 0.92: c = wood_shadow
            else:           c = wood_edge
            pygame.draw.line(s, c, (px, y), (px, y), 1)

    # ── STEP 2: STAVE LINES ───────────────────────
    # 5 vertical dark lines — curve with silhouette
    fracs = [0.18, 0.32, 0.50, 0.67, 0.82]
    for frac in fracs:
        for y in range(2, height - 1):
            lx, rx = bx(y)
            if rx <= lx:
                continue
            px = int(lx + (rx - lx) * frac)
            # Line color depends on position
            if frac < 0.45 or frac > 0.55:
                lc = wood_shadow
            else:
                lc = wood_mid
            pygame.draw.line(s, lc, (px, y), (px, y), 1)

    # ── STEP 3: CARTOON OUTLINE ───────────────────
    for y in range(2, height):
        lx, rx = bx(y)
        if rx <= lx:
            continue
        pygame.draw.line(s, outline, (lx,     y), (lx,     y), 1)
        pygame.draw.line(s, outline, (lx + 1, y), (lx + 1, y), 1)
        pygame.draw.line(s, outline, (rx,     y), (rx,     y), 1)
        pygame.draw.line(s, outline, (rx - 1, y), (rx - 1, y), 1)
    # Bottom outline
    lxb, rxb = bx(height - 1)
    pygame.draw.line(s, outline, (lxb, height-1), (rxb, height-1), 2)

    # ── STEP 4: METAL RINGS ───────────────────────
    # 3 rings: top 18%, middle 50%, bottom 82%
    ring_ys  = [int(height * 0.18),
                int(height * 0.50),
                int(height * 0.82)]
    ring_h   = 8

    for ry in ring_ys:
        for dy in range(ring_h):
            y_pos = ry - ring_h // 2 + dy
            if y_pos < 2 or y_pos >= height:
                continue
            lx, rx = bx(y_pos)
            if rx <= lx:
                continue
            t = dy / (ring_h - 1)
            # Gradient: dark → light → dark
            if   t < 0.18: rc = ring_dark
            elif t < 0.38: rc = ring_mid
            elif t < 0.62: rc = ring_light
            elif t < 0.82: rc = ring_mid
            else:           rc = ring_dark
            pygame.draw.line(s, rc,
                (lx + 2, y_pos), (rx - 2, y_pos), 1)
        # Ring outlines top and bottom edge
        for edge_dy in [0, ring_h - 1]:
            y_pos = ry - ring_h // 2 + edge_dy
            if 2 <= y_pos < height:
                lx, rx = bx(y_pos)
                pygame.draw.line(s, ring_out,
                    (lx + 2, y_pos), (rx - 2, y_pos), 1)

    # ── STEP 5: CLEAN FLAT TOP ────────────────────
    lx0, rx0 = bx(0)
    top_w  = rx0 - lx0
    top_rx = top_w // 2 - 2
    top_ry = max(6, top_rx // 4)
    top_cx = cx
    top_cy = top_ry

    # Wood surface fill — covers the entire top face
    pygame.draw.ellipse(s, top_fill,
        (top_cx - top_rx,     top_cy - top_ry,
         top_rx * 2,          top_ry * 2))

    # Back half shadow — darker rear of top surface
    pygame.draw.ellipse(s, top_dark,
        (top_cx - top_rx + 3, top_cy,
         (top_rx - 3) * 2,    top_ry - 1))

    # Front highlight streak — bright front of top surface
    pygame.draw.ellipse(s, wood_bloom,
        (top_cx - top_rx + 8, top_cy - top_ry + 2,
         (top_rx - 12) * 2,   top_ry - 3))

    # Single clean outline — just one pixel dark border
    # NO thick ring, NO metal band on top
    pygame.draw.ellipse(s, outline,
        (top_cx - top_rx,     top_cy - top_ry,
         top_rx * 2,          top_ry * 2), 1)

    return s


def load_or_placeholder(path: str, size: tuple, color: tuple) -> pygame.Surface:
    """Load image or return a nice placeholder if file not found."""
    try:
        return pygame.image.load(path).convert_alpha()
    except FileNotFoundError:
        # Special case: create nice barrel art
        if "barrel" in path.lower():
            return create_barrel_art(size[0], size[1])
        
        # Default: colored rectangle
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

# ── Respawn / Head-Streak Tuning ──────────────────────────────
RESPAWN_DELAY         = 1.5    # seconds before dead player respawns
INVULN_DURATION       = 0.5    # seconds of invulnerability after respawn
MAX_KILLS_TO_WIN      = 3      # kills needed to win the match
HEAD_SIZE_BASE        = 1.0    # default head scale multiplier
HEAD_SIZE_STEP        = 0.2    # head growth per kill (1.0 → 1.3 → 1.6 → win)
P1_HIDE_HAT_IF_CUSTOM = True   # hide cowboy hat when P1 uses custom face
HEAD_Y_OFFSET_P1      = -1      # manual Y offset for P1 head (negative = up)
HEAD_Y_OFFSET_P2      = -1      # manual Y offset for P2 head (negative = up)
