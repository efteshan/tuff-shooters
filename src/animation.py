# src/animation.py — Skeletal animation system for player characters.
# Draws body parts (head, torso, arms, legs) with procedural pixel art.
# Handles walk cycles, jump poses, knife swings, gun recoil, squash/stretch, and ragdoll death.

import pygame
import math
import random
from src.constants import (
    GRAVITY, MAX_FALL_SPEED, GROUND_Y, VIRTUAL_W,
    JUMP_LAUNCH_VEL, JUMP_RISE_VEL, JUMP_FALL_VEL,
    JUMP_LEG_LAUNCH, JUMP_LEG_RISE, JUMP_LEG_APEX, JUMP_LEG_FALL, JUMP_LEG_LAND,
    JUMP_ARM_LAUNCH, JUMP_ARM_RISE, JUMP_ARM_APEX, JUMP_ARM_FALL, JUMP_ARM_LAND,
    JUMP_TORSO_LAUNCH, JUMP_TORSO_FALL, JUMP_TORSO_LAND,
    JUMP_HEAD_LAUNCH, JUMP_HEAD_FALL,
    JUMP_LERP_LEGS, JUMP_LERP_TORSO, JUMP_LERP_ARMS, JUMP_LERP_HEAD,
    JUMP_LAND_DURATION,
    P1_HIDE_HAT_IF_CUSTOM,
    HEAD_Y_OFFSET_P1, HEAD_Y_OFFSET_P2,
)


def _draw_head_base(S, skin_color=None, hair_color=None):
    """Draw the head base (everything except eyes) at scale S.
    skin_color and hair_color can be overridden per-player."""
    big = pygame.Surface((22*S, 24*S), pygame.SRCALPHA)

    skin = skin_color or (210, 170, 115)
    sr, sg, sb = skin
    dark = (max(0,sr-40), max(0,sg-45), max(0,sb-40))

    face_pts = [(p[0]*S, p[1]*S) for p in [
        (11,  1), (20,  8), (21, 15), (16, 22),
        (11, 24), ( 6, 22), ( 1, 15), ( 2,  8),
    ]]
    pygame.draw.polygon(big, skin, face_pts)
    pygame.draw.polygon(big, dark, face_pts, 2)

    # Multi-gradient face shading — derived from skin tone
    glow    = (min(255,sr+25), min(255,sg+30), min(255,sb+30))
    glow2   = (min(255,sr+15), min(255,sg+20), min(255,sb+20))
    chin_sh = (max(0,sr-35), max(0,sg-35), max(0,sb-30))
    jaw_hi  = (min(255,sr+10), min(255,sg+12), min(255,sb+10))

    pygame.draw.ellipse(big, glow,    (6*S, 4*S, 10*S, 6*S))
    pygame.draw.ellipse(big, glow2,   (5*S, 8*S, 12*S, 5*S))
    pygame.draw.ellipse(big, chin_sh, (7*S, 19*S, 8*S, 4*S))
    pygame.draw.ellipse(big, jaw_hi,  (4*S, 16*S, 6*S, 4*S))
    # Temple gradients
    t_hi = (min(255,sr+35), min(255,sg+45), min(255,sb+45))
    t_md = (min(255,sr+20), min(255,sg+25), min(255,sb+25))
    t_sh = (max(0,sr-50), max(0,sg-55), max(0,sb-50))
    t_sh2= (max(0,sr-30), max(0,sg-35), max(0,sb-35))
    pygame.draw.line(big, t_hi,  (2*S, 9*S), (2*S, 18*S), 3)
    pygame.draw.line(big, t_md,  (3*S, 8*S), (3*S, 19*S), 2)
    pygame.draw.line(big, t_sh,  (19*S, 9*S), (19*S, 18*S), 3)
    pygame.draw.line(big, t_sh2, (18*S, 8*S), (18*S, 19*S), 2)

    # Cheek volumes
    ch_hi = (min(255,sr+15), min(255,sg+15), min(255,sb+15))
    ch_sh = (max(0,sr-15), max(0,sg-20), max(0,sb-20))
    pygame.draw.ellipse(big, ch_hi, (3*S, 7*S, 7*S, 7*S))
    pygame.draw.ellipse(big, ch_sh, (3*S, 14*S, 7*S, 6*S))
    pygame.draw.ellipse(big, ch_hi, (12*S, 7*S, 7*S, 7*S))
    pygame.draw.ellipse(big, ch_sh, (12*S, 14*S, 7*S, 6*S))

    # Ear suggestion
    ear   = (max(0,sr-10), max(0,sg-10), max(0,sb-10))
    ear_d = (max(0,sr-25), max(0,sg-28), max(0,sb-25))
    pygame.draw.ellipse(big, ear,   (0, 10*S, 3*S, 5*S))
    pygame.draw.ellipse(big, ear_d, (0, 11*S, 2*S, 3*S))
    pygame.draw.ellipse(big, ear,   (20*S, 10*S, 3*S, 5*S))
    pygame.draw.ellipse(big, ear_d, (21*S, 11*S, 2*S, 3*S))

    # Hair
    hair = hair_color or (40, 28, 15)
    hr, hg, hb = hair
    highlight = (min(255,hr+40), min(255,hg+30), min(255,hb+15))
    hair_pts = [(p[0]*S, p[1]*S) for p in [
        (2, 8), (3, 3), (7, 0), (15, 0), (19, 3), (20, 8),
        (17, 6), (14, 2), (8, 2), (5, 6)
    ]]
    pygame.draw.polygon(big, hair, hair_pts)
    for pts in [[(7,2),(9,-3),(11,2)], [(10,1),(12,-4),(14,1)], [(13,2),(15,-2),(17,3)]]:
        pygame.draw.polygon(big, hair, [(p[0]*S, p[1]*S) for p in pts])
    pygame.draw.line(big, highlight, (8*S, 1*S), (14*S, 1*S), 3)
    pygame.draw.line(big, highlight, (9*S, 0), (13*S, 0), 2)
    h_mid = (min(255,hr+55), min(255,hg+42), min(255,hb+20))
    pygame.draw.line(big, h_mid, (4*S, 4*S), (3*S, 7*S), 2)
    h_dk = (min(255,hr+15), min(255,hg+10), min(255,hb+5))
    pygame.draw.ellipse(big, h_dk, (9*S, 0, 5*S, 3*S))
    # Sideburns
    pygame.draw.rect(big, hair, (2*S, 7*S, 2*S, 5*S))
    pygame.draw.rect(big, hair, (18*S, 7*S, 2*S, 5*S))
    sb_line = (min(255,hr+25), min(255,hg+17), min(255,hb+7))
    pygame.draw.line(big, sb_line, (6*S, 3*S), (10*S, 1*S), 1)
    pygame.draw.line(big, sb_line, (12*S, 1*S), (16*S, 3*S), 1)

    # Nose bridge + nose tip
    nose   = (max(0,sr-20), max(0,sg-20), max(0,sb-15))
    nose_t = (max(0,sr-10), max(0,sg-10), max(0,sb-7))
    pygame.draw.line(big, nose, (11*S, 10*S), (11*S, 16*S), 1)
    pygame.draw.ellipse(big, nose_t, (9*S, 15*S, 4*S, 3*S))
    # Brow ridge
    brow = (max(0,sr-25), max(0,sg-25), max(0,sb-20))
    pygame.draw.line(big, brow, (5*S, 8*S), (17*S, 8*S), 2)

    # Stubble suggestion
    stubble = (max(0,sr-30), max(0,sg-30), max(0,sb-20))
    for sx, sy in [(9,18),(11,18),(13,18),(8,20),(10,20),(12,20),(14,20),(10,22),(12,22)]:
        pygame.draw.circle(big, stubble, (sx*S, sy*S), max(1, S//3))

    return big


def create_head(skin_color=None, hair_color=None, brow_color=None):
    """Head with eyes OPEN — rendered at 4x."""
    S = 4
    big = _draw_head_base(S, skin_color=skin_color, hair_color=hair_color)
    bc = brow_color or (65, 42, 18)
    sk = skin_color or (210, 170, 115)
    closed_c = (max(0,sk[0]-25), max(0,sk[1]-25), max(0,sk[2]-20))

    # ── EYES ────────────────────────────────────
    # Left eye
    pygame.draw.ellipse(big, (240, 240, 235), (6*S, 10*S, 4*S, 3*S))   # sclera
    pygame.draw.ellipse(big, (55, 35, 20),    (7*S, 10*S, 3*S, 3*S))   # iris
    pygame.draw.circle(big,  (15, 8, 5),      (8*S + S, 11*S + S), S)  # pupil
    pygame.draw.circle(big,  (255,255,255),    (8*S, 10*S + S), max(1, S//2))  # specular
    # Left eyebrow
    pygame.draw.line(big, bc, (5*S, 9*S), (10*S, 8*S), max(2, S))

    # Right eye
    pygame.draw.ellipse(big, (240, 240, 235), (12*S, 10*S, 4*S, 3*S))  # sclera
    pygame.draw.ellipse(big, (55, 35, 20),    (12*S, 10*S, 3*S, 3*S))  # iris
    pygame.draw.circle(big,  (15, 8, 5),      (13*S + S, 11*S + S), S) # pupil
    pygame.draw.circle(big,  (255,255,255),    (13*S, 10*S + S), max(1, S//2))  # specular
    # Right eyebrow
    pygame.draw.line(big, bc, (12*S, 8*S), (17*S, 9*S), max(2, S))

    return pygame.transform.smoothscale(big, (22, 24))


def create_head_closed(skin_color=None, hair_color=None, brow_color=None):
    """Head with eyes CLOSED (for blinking) — rendered at 4x."""
    S = 4
    big = _draw_head_base(S, skin_color=skin_color, hair_color=hair_color)
    bc = brow_color or (65, 42, 18)
    sk = skin_color or (210, 170, 115)
    closed_c = (max(0,sk[0]-25), max(0,sk[1]-25), max(0,sk[2]-20))

    # Closed eyes — skin-colored line where eyes would be
    pygame.draw.line(big, closed_c, (6*S, 11*S), (10*S, 11*S), max(2, S))
    pygame.draw.line(big, closed_c, (12*S, 11*S), (16*S, 11*S), max(2, S))
    # Eyebrows (same as open)
    pygame.draw.line(big, bc, (5*S, 9*S), (10*S, 8*S), max(2, S))
    pygame.draw.line(big, bc, (12*S, 8*S), (17*S, 9*S), max(2, S))

    return pygame.transform.smoothscale(big, (22, 24))


def create_outlaw_head():
    """Outlaw head with bandit mask and black knit cap — eyes OPEN."""
    S = 4
    skin = (210, 180, 140)   # #D2B48C Desert Tan
    cap  = (0, 0, 0)         # Black knit cap
    mask = (26, 26, 26)      # #1A1A1A Charcoal mask
    big = _draw_head_base(S, skin_color=skin, hair_color=cap)

    # Black knit cap — covers top of head over the hair
    cap_pts = [(p[0]*S, p[1]*S) for p in [
        (2, 7), (3, 2), (7, -1), (15, -1), (19, 2), (20, 7),
        (17, 5), (14, 1), (8, 1), (5, 5)
    ]]
    pygame.draw.polygon(big, cap, cap_pts)
    # Cap fold / rim at bottom
    pygame.draw.line(big, (40, 40, 40), (3*S, 6*S), (19*S, 6*S), max(2, S))
    # Cap texture — subtle horizontal lines
    for cy in range(1, 6):
        pygame.draw.line(big, (20, 20, 20), (5*S, cy*S), (17*S, cy*S), 1)

    # Bandit mask — solid charcoal band over the eye area
    pygame.draw.rect(big, mask, (1*S, 8*S, 20*S, 5*S))
    # Mask edge highlights
    pygame.draw.line(big, (50, 50, 50), (2*S, 8*S), (20*S, 8*S), 1)

    # Eyes visible through mask holes
    # Left eye
    pygame.draw.ellipse(big, (240, 240, 235), (6*S, 10*S, 4*S, 3*S))
    pygame.draw.ellipse(big, (55, 35, 20),    (7*S, 10*S, 3*S, 3*S))
    pygame.draw.circle(big,  (15, 8, 5),      (8*S + S, 11*S + S), S)
    pygame.draw.circle(big,  (255,255,255),    (8*S, 10*S + S), max(1, S//2))
    # Right eye
    pygame.draw.ellipse(big, (240, 240, 235), (12*S, 10*S, 4*S, 3*S))
    pygame.draw.ellipse(big, (55, 35, 20),    (12*S, 10*S, 3*S, 3*S))
    pygame.draw.circle(big,  (15, 8, 5),      (13*S + S, 11*S + S), S)
    pygame.draw.circle(big,  (255,255,255),    (13*S, 10*S + S), max(1, S//2))

    # 2px cel-shaded outline around face perimeter
    face_pts = [(p[0]*S, p[1]*S) for p in [
        (11,  1), (20,  8), (21, 15), (16, 22),
        (11, 24), ( 6, 22), ( 1, 15), ( 2,  8),
    ]]
    pygame.draw.polygon(big, (0, 0, 0), face_pts, 2)

    return pygame.transform.smoothscale(big, (22, 24))


def create_outlaw_head_closed():
    """Outlaw head with bandit mask and black knit cap — eyes CLOSED."""
    S = 4
    skin = (210, 180, 140)   # #D2B48C
    cap  = (0, 0, 0)
    mask = (26, 26, 26)      # #1A1A1A
    big = _draw_head_base(S, skin_color=skin, hair_color=cap)

    # Black knit cap
    cap_pts = [(p[0]*S, p[1]*S) for p in [
        (2, 7), (3, 2), (7, -1), (15, -1), (19, 2), (20, 7),
        (17, 5), (14, 1), (8, 1), (5, 5)
    ]]
    pygame.draw.polygon(big, cap, cap_pts)
    pygame.draw.line(big, (40, 40, 40), (3*S, 6*S), (19*S, 6*S), max(2, S))
    for cy in range(1, 6):
        pygame.draw.line(big, (20, 20, 20), (5*S, cy*S), (17*S, cy*S), 1)

    # Bandit mask
    pygame.draw.rect(big, mask, (1*S, 8*S, 20*S, 5*S))
    pygame.draw.line(big, (50, 50, 50), (2*S, 8*S), (20*S, 8*S), 1)

    # Closed eyes through mask
    pygame.draw.line(big, (60, 60, 60), (6*S, 11*S), (10*S, 11*S), max(2, S))
    pygame.draw.line(big, (60, 60, 60), (12*S, 11*S), (16*S, 11*S), max(2, S))

    # 2px outline
    face_pts = [(p[0]*S, p[1]*S) for p in [
        (11,  1), (20,  8), (21, 15), (16, 22),
        (11, 24), ( 6, 22), ( 1, 15), ( 2,  8),
    ]]
    pygame.draw.polygon(big, (0, 0, 0), face_pts, 2)

    return pygame.transform.smoothscale(big, (22, 24))

def create_torso():
    """Smooth 3D torso with rich gradient shading — rendered at 4x."""
    S = 4
    big = pygame.Surface((16*S, 22*S), pygame.SRCALPHA)
    # Main body
    pygame.draw.rect(big, (215, 105, 30), (0, 0, 16*S, 22*S), border_radius=3*S)
    # 4-band gradient: left bright → right dark for cylinder feel
    pygame.draw.rect(big, (248, 158, 62), (1*S, 1*S, 3*S, 16*S), border_radius=S)  # band 1 rim
    pygame.draw.rect(big, (240, 140, 52), (3*S, 1*S, 4*S, 16*S))                    # band 2
    pygame.draw.rect(big, (200, 92, 25),  (10*S, 1*S, 3*S, 16*S))                   # band 3
    pygame.draw.rect(big, (170, 72, 15),  (13*S, 1*S, 2*S, 16*S), border_radius=S)  # band 4 shadow
    # Chest highlight — bright ellipse
    pygame.draw.ellipse(big, (255, 185, 90), (3*S, 3*S, 6*S, 5*S))
    # Secondary specular — smaller and brighter
    pygame.draw.ellipse(big, (255, 210, 130), (4*S, 4*S, 3*S, 2*S))
    # Belly shadow — subtle dark ellipse at bottom
    pygame.draw.ellipse(big, (185, 82, 18), (3*S, 13*S, 10*S, 5*S))
    # Belt
    pygame.draw.rect(big, (140, 70, 20), (0, 18*S, 16*S, 4*S), border_radius=2*S)
    pygame.draw.line(big, (165, 85, 28), (1*S, 18*S), (15*S, 18*S), 2)  # belt top edge
    # Center line
    pygame.draw.line(big, (170, 80, 20), (8*S, 2*S), (8*S, 17*S), 2)
    # Collar
    pygame.draw.line(big, (180, 85, 22), (2*S, 1*S), (14*S, 1*S), 2)
    # Shoulder seams
    pygame.draw.line(big, (195, 95, 28), (1*S, 3*S), (4*S, 1*S), 1)
    pygame.draw.line(big, (195, 95, 28), (15*S, 3*S), (12*S, 1*S), 1)
    # Outline
    pygame.draw.rect(big, (130, 58, 8), (0, 0, 16*S, 22*S), 2, border_radius=3*S)
    return pygame.transform.smoothscale(big, (16, 22))

def create_arm(color, w=8, h=22, skin_color=None, stripe_color=None):
    """Smooth 3D arm with hand shape — rendered at 4x.
    skin_color overrides hand color. stripe_color adds horizontal stripes."""
    S = 4
    big = pygame.Surface((w*S, h*S), pygame.SRCALPHA)
    skin       = skin_color or (210, 170, 115)
    skin_dk    = (max(0,skin[0]-25), max(0,skin[1]-25), max(0,skin[2]-20))
    skin_sh    = (max(0,skin[0]-50), max(0,skin[1]-50), max(0,skin[2]-40))
    darker     = tuple(max(0, c - 55) for c in color)
    mid_dk     = tuple(max(0, c - 35) for c in color)
    lighter    = tuple(min(255, c + 40) for c in color)
    rim        = tuple(min(255, c + 70) for c in color)
    mid_lt     = tuple(min(255, c + 25) for c in color)
    # Upper arm
    pygame.draw.rect(big, color, (1*S, 0, 6*S, 12*S), border_radius=3*S)
    # Elbow
    pygame.draw.rect(big, color, (1*S, 11*S, 6*S, 4*S))
    # Forearm — slightly tapered
    pygame.draw.rect(big, color, (1*S, 14*S, 6*S, 5*S), border_radius=2*S)
    # Wrist narrowing
    pygame.draw.rect(big, color, (1*S, 18*S, 5*S, 2*S), border_radius=S)

    # Horizontal stripes (Outlaw prisoner pattern)
    if stripe_color:
        stripe_h = 3 * S   # stripe thickness
        gap_h = 3 * S      # gap between stripes
        for sy in range(0, 19*S, stripe_h + gap_h):
            pygame.draw.rect(big, stripe_color, (1*S, sy, 6*S, stripe_h))

    # ── HAND SHAPE ────────────────────────────────
    # Palm
    pygame.draw.rect(big, skin, (0, 19*S, 7*S, 4*S), border_radius=2*S)
    palm_hi = (min(255,skin[0]+15), min(255,skin[1]+18), min(255,skin[2]+17))
    pygame.draw.ellipse(big, palm_hi, (1*S, 19*S, 4*S, 3*S))
    pygame.draw.line(big, skin_sh, (6*S, 19*S), (6*S, 22*S), 2)
    # Thumb
    pygame.draw.ellipse(big, skin, (0, 18*S, 3*S, 3*S))
    thumb_hi = (min(255,skin[0]+10), min(255,skin[1]+10), min(255,skin[2]+10))
    pygame.draw.ellipse(big, thumb_hi, (0, 18*S, 2*S, 2*S))
    # Finger bumps
    for fx in [0, 2, 4]:
        pygame.draw.rect(big, skin_dk, (fx*S + S//2, 22*S, 2*S, 2*S), border_radius=S)
    pygame.draw.line(big, skin_sh, (1*S, 22*S), (6*S, 22*S), 2)
    pygame.draw.line(big, skin_sh, (1*S, 20*S), (5*S, 20*S), 1)
    pygame.draw.line(big, skin_sh, (2*S, 21*S), (5*S, 21*S), 1)

    # ── 3D ARM SHADING ────────────────────────────
    pygame.draw.line(big, rim,    (1*S, 1*S), (1*S, 18*S), 3)
    pygame.draw.line(big, mid_lt, (2*S, 1*S), (2*S, 18*S), 2)
    pygame.draw.line(big, mid_dk, (5*S, 1*S), (5*S, 18*S), 2)
    pygame.draw.line(big, darker, (6*S, 1*S), (6*S, 18*S), 3)
    pygame.draw.rect(big, lighter, (2*S, 1*S, 3*S, 5*S), border_radius=2*S)
    pygame.draw.ellipse(big, mid_lt, (2*S, 5*S, 4*S, 4*S))
    pygame.draw.line(big, darker, (2*S, 11*S), (5*S, 11*S), 2)
    pygame.draw.line(big, mid_dk, (3*S, 14*S), (3*S, 18*S), 1)
    pygame.draw.line(big, darker, (1*S, 18*S), (5*S, 18*S), 1)

    # 2px cel-shaded outline
    pygame.draw.rect(big, (0, 0, 0), (1*S, 0, 6*S, 20*S), 2, border_radius=3*S)
    return pygame.transform.smoothscale(big, (w, h))

def create_leg(color, w=11, h=26, shoe=None, shoe_hi=None, stripe_color=None):
    """Smooth 3D leg with multi-gradient shading — rendered at 4x.
    shoe/shoe_hi override boot colors. stripe_color adds horizontal stripes."""
    S = 4
    big = pygame.Surface((w*S, h*S), pygame.SRCALPHA)
    thigh_color = color
    shin_color  = tuple(max(0, c - 25) for c in color)
    darker      = tuple(max(0, c - 55) for c in color)
    mid_dk      = tuple(max(0, c - 35) for c in color)
    rim         = tuple(min(255, c + 65) for c in color)
    mid_lt      = tuple(min(255, c + 30) for c in color)
    shoe_color  = shoe    or (62,  38, 12)
    toe_color   = shoe_hi or (185, 88, 28)
    shoe_ol     = (max(0,shoe_color[0]-27), max(0,shoe_color[1]-22), max(0,shoe_color[2]-10))
    boot_rim    = (min(255,shoe_color[0]+33), min(255,shoe_color[1]+24), min(255,shoe_color[2]+13))
    boot_line   = (min(255,shoe_color[0]+23), min(255,shoe_color[1]+17), min(255,shoe_color[2]+6))
    heel_c      = (max(0,shoe_color[0]-20), max(0,shoe_color[1]-13), max(0,shoe_color[2]-4))

    # Thigh
    pygame.draw.rect(big, thigh_color, (1*S, 0, 9*S, 11*S), border_radius=3*S)
    # Knee
    pygame.draw.rect(big, thigh_color, (2*S, 10*S, 7*S, 5*S))
    # Shin
    pygame.draw.rect(big, shin_color, (2*S, 14*S, 7*S, 8*S), border_radius=2*S)

    # Horizontal stripes (Outlaw prisoner pattern)
    if stripe_color:
        stripe_h = 3 * S
        gap_h = 3 * S
        for sy in range(0, 21*S, stripe_h + gap_h):
            pygame.draw.rect(big, stripe_color, (1*S, sy, 9*S, stripe_h))

    # 3-strip gradient on thigh
    pygame.draw.line(big, rim,    (2*S, 1*S), (2*S, 9*S), 3)
    pygame.draw.line(big, mid_lt, (3*S, 1*S), (3*S, 9*S), 2)
    pygame.draw.line(big, mid_dk, (7*S, 1*S), (7*S, 9*S), 2)
    pygame.draw.line(big, darker, (8*S, 1*S), (8*S, 9*S), 3)
    # 3-strip gradient on shin
    pygame.draw.line(big, rim,    (3*S, 15*S), (3*S, 20*S), 3)
    pygame.draw.line(big, mid_lt, (4*S, 15*S), (4*S, 20*S), 2)
    pygame.draw.line(big, mid_dk, (6*S, 15*S), (6*S, 20*S), 2)
    pygame.draw.line(big, darker, (7*S, 15*S), (7*S, 20*S), 3)
    # Knee joint shadow
    pygame.draw.line(big, darker, (3*S, 10*S), (7*S, 10*S), 2)
    # Calf muscle bulge
    pygame.draw.ellipse(big, mid_lt, (3*S, 15*S, 4*S, 4*S))
    # Thigh highlight
    lighter = tuple(min(255, c + 45) for c in color)
    pygame.draw.rect(big, lighter, (3*S, 1*S, 4*S, 5*S), border_radius=2*S)
    # Shoe
    pygame.draw.rect(big, shoe_color, (1*S, 21*S, 11*S, 5*S), border_radius=2*S)
    pygame.draw.ellipse(big, toe_color, (5*S, 22*S, 7*S, 3*S))
    pygame.draw.rect(big, shoe_ol, (1*S, 21*S, 11*S, 5*S), 2, border_radius=2*S)
    # Boot top rim highlight
    pygame.draw.rect(big, boot_rim, (3*S, 21*S, 4*S, 2*S), border_radius=S)
    pygame.draw.line(big, boot_line, (2*S, 21*S), (9*S, 21*S), 1)
    # Ankle crease
    pygame.draw.line(big, darker, (2*S, 21*S), (8*S, 21*S), 1)
    # Heel detail
    pygame.draw.rect(big, heel_c, (1*S, 24*S, 4*S, 2*S), border_radius=S)
    # Mid-shin taper highlight
    pygame.draw.line(big, rim, (4*S, 17*S), (6*S, 17*S), 1)
    return pygame.transform.smoothscale(big, (w, h))

def create_gun():
    """Smooth 3D gun — rendered at 4x then downsampled."""
    S = 4
    big = pygame.Surface((22*S, 10*S), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(big, (50, 50, 50), (0, 2*S, 16*S, 6*S), border_radius=S)
    # Barrel
    pygame.draw.rect(big, (30, 30, 30), (14*S, 3*S, 8*S, 4*S))
    # Handle
    pygame.draw.rect(big, (80, 50, 30), (3*S, 6*S, 6*S, 4*S), border_radius=S)
    # 3D metallic highlights
    pygame.draw.line(big, (120, 120, 120), (0, 2*S), (21*S, 2*S), 2)
    pygame.draw.line(big, (18, 18, 18), (0, 7*S), (14*S, 7*S), 2)
    pygame.draw.rect(big, (85, 85, 85), (20*S, 3*S, 2*S, 2*S))
    pygame.draw.line(big, (110, 72, 42), (4*S, 7*S), (4*S, 9*S), 2)
    # Trigger guard — small arc
    pygame.draw.arc(big, (40, 40, 40), (6*S, 6*S, 4*S, 4*S), 0, 3.14, 2)
    # Sight notch on top
    pygame.draw.rect(big, (75, 75, 75), (13*S, 1*S, 2*S, 2*S))
    # Grip texture — tiny horizontal lines
    for gy in [7, 8, 9]:
        pygame.draw.line(big, (65, 40, 22), (4*S, gy*S), (7*S, gy*S), 1)
    # Outline
    pygame.draw.rect(big, (15, 15, 15), (0, 2*S, 16*S, 6*S), 2, border_radius=S)
    return pygame.transform.smoothscale(big, (22, 10))

def create_knife():
    """Smooth 3D knife — rendered at 4x then downsampled."""
    S = 4
    big = pygame.Surface((26*S, 10*S), pygame.SRCALPHA)
    # Blade
    blade_pts = [(6*S, 4*S), (24*S, 2*S), (24*S, 6*S), (6*S, 6*S)]
    pygame.draw.polygon(big, (190, 200, 210), blade_pts)
    # 3D blade reflections
    pygame.draw.line(big, (235, 245, 255), (6*S, 3*S), (24*S, 2*S), 2)
    pygame.draw.line(big, (220, 230, 245), (8*S, 5*S), (22*S, 3*S), 2)
    pygame.draw.line(big, (140, 148, 160), (7*S, 6*S), (23*S, 6*S), 2)
    # Handle
    pygame.draw.rect(big, (110, 70, 30), (0, 3*S, 7*S, 5*S), border_radius=S)
    pygame.draw.line(big, (145, 100, 52), (1*S, 4*S), (1*S, 6*S), 2)
    # Guard
    pygame.draw.rect(big, (60, 60, 60), (6*S, 1*S, 2*S, 8*S))
    pygame.draw.line(big, (95, 95, 95), (6*S, 2*S), (6*S, 7*S), 2)
    return pygame.transform.smoothscale(big, (26, 10))

def create_shotgun():
    """Rich 3D Shotgun for drawing in hand."""
    S = 3
    s = pygame.Surface((36*S, 18*S), pygame.SRCALPHA)
    
    pygame.draw.rect(s, (110,  60, 20),  ( 0,  6*S, 12*S, 4*S), border_radius=S)
    pygame.draw.rect(s, (140,  80, 30),  ( 1*S, 7*S, 10*S, 2*S), border_radius=S)
    
    pygame.draw.rect(s, (50, 50, 50),  (10*S, 5*S, 10*S, 5*S), border_radius=S)
    pygame.draw.rect(s, (80, 80, 80),  (11*S, 6*S, 8*S, 2*S), border_radius=S)
    
    pygame.draw.rect(s, (40, 40, 40), (20*S, 5*S, 16*S, 2*S))
    pygame.draw.rect(s, (30, 30, 30), (20*S, 8*S, 12*S, 2*S))
    pygame.draw.line(s, (100, 100, 100), (21*S, 5*S), (35*S, 5*S), 1)
    
    pygame.draw.rect(s, (90, 50, 15), (22*S, 7*S, 6*S, 4*S), border_radius=1)
    for px in range(23, 28, 2):
        pygame.draw.line(s, (50, 25, 5), (px*S, 7*S), (px*S, 10*S), 1)
        
    return pygame.transform.smoothscale(s, (36, 18))

def create_bazooka():
    """Rich 3D side-view RPG Bazooka for drawing in hand/shoulder."""
    S = 3
    s = pygame.Surface((44*S, 20*S), pygame.SRCALPHA)
    
    pygame.draw.rect(s, (50,  65,  50), (4*S, 6*S, 36*S, 8*S), border_radius=S)
    pygame.draw.rect(s, (70,  90,  70), (4*S, 6*S, 36*S, 3*S), border_radius=S)
    pygame.draw.rect(s, (30,  40,  30), (4*S, 11*S, 36*S, 3*S), border_radius=S)
    
    pygame.draw.polygon(s, (150, 40, 40), [(40*S, 6*S), (44*S, 10*S), (40*S, 14*S)])
    pygame.draw.polygon(s, (40, 40, 40), [(0, 4*S), (5*S, 6*S), (5*S, 14*S), (0, 16*S)])
    pygame.draw.rect(s, (40, 40, 40), (36*S, 4*S, 4*S, 12*S), border_radius=1)
    
    pygame.draw.rect(s, (30, 30, 30), (16*S, 2*S, 12*S, 4*S), border_radius=1)
    pygame.draw.rect(s, (20, 20, 20), (18*S, 0*S,  8*S, 2*S), border_radius=1)
    
    pygame.draw.rect(s, (30, 30, 30), (12*S, 14*S, 4*S, 4*S), border_radius=1)
    pygame.draw.rect(s, (30, 30, 30), (28*S, 14*S, 4*S, 4*S), border_radius=1)

    return pygame.transform.smoothscale(s, (44, 20))

def create_cowboy_hat():
    """Lawman cowboy hat in Espresso Brown #3D2B1F — rendered at 4x."""
    S = 4
    big = pygame.Surface((40*S, 22*S), pygame.SRCALPHA)

    # Espresso Brown palette
    hat_crown = (61,  43, 31)   # #3D2B1F base
    hat_dark  = (40,  28, 18)
    hat_hi    = (85,  62, 42)
    hat_band  = (255, 215, 0)   # #FFD700 Gold band
    brim_c    = (52,  36, 22)
    brim_sh   = (35,  22, 12)
    ol        = (20,  10,  2)

    # Brim
    pygame.draw.ellipse(big, brim_c,  (0, 12*S, 40*S, 9*S))
    pygame.draw.ellipse(big, brim_sh, (3*S, 15*S, 34*S, 5*S))
    pygame.draw.ellipse(big, (75, 55, 35), (4*S, 12*S, 32*S, 4*S))
    # Crown
    pygame.draw.rect(big, hat_crown, (10*S, 0, 20*S, 14*S), border_radius=4*S)
    pygame.draw.rect(big, hat_dark,  (11*S, 0, 18*S, 5*S), border_radius=3*S)
    pygame.draw.rect(big, hat_hi,    (11*S, 2*S, 6*S, 8*S), border_radius=2*S)
    # Crown specular
    pygame.draw.ellipse(big, (105, 82, 58), (13*S, 3*S, 5*S, 4*S))
    # Crown right shadow
    pygame.draw.rect(big, (30, 20, 10), (25*S, 2*S, 3*S, 10*S), border_radius=2*S)
    # Gold band
    pygame.draw.rect(big, hat_band, (10*S, 10*S, 20*S, 3*S))
    pygame.draw.line(big, (255, 235, 100), (11*S,10*S), (28*S,10*S), 2)
    # Outlines
    pygame.draw.ellipse(big, ol, (0, 12*S, 40*S, 9*S), 2)
    pygame.draw.rect(big, ol, (10*S, 0, 20*S, 14*S), 2, border_radius=4*S)

    return pygame.transform.smoothscale(big, (40, 22))


class AnimationManager:
    """Simple frame-by-frame animation player. Register named sequences,
    then call update() each frame to advance and get_frame() to render."""
    
    def __init__(self):
        self.animations = {}
    
    def register(self, name, frames, fps=24):
        """Register a new animation sequence."""
        self.animations[name] = {
            'frames': frames,
            'fps': fps,
            'spf': 1.0 / fps,
            'current': 0,
            'timer': 0.0
        }
    
    def update(self, name, dt):
        """Update animation and return True if completed."""
        if name not in self.animations:
            return False
        
        anim = self.animations[name]
        anim['timer'] += dt
        
        if anim['timer'] >= anim['spf']:
            anim['timer'] -= anim['spf']
            anim['current'] += 1
            
            if anim['current'] >= len(anim['frames']):
                return True
        
        return False
    
    def get_frame(self, name):
        """Get current frame of animation."""
        if name not in self.animations:
            return None
        
        anim = self.animations[name]
        idx = min(anim['current'], len(anim['frames']) - 1)
        return anim['frames'][idx]
    
    def reset(self, name):
        """Reset animation to first frame."""
        if name in self.animations:
            self.animations[name]['current'] = 0
            self.animations[name]['timer'] = 0.0


class SkeletalBody:
    """The player's animated body. Each body part (head, torso, arms, legs) is a small
    pygame Surface that gets rotated and positioned each frame based on the current
    animation state (idle, walking, jumping, attacking, etc.).
    Also handles ragdoll death physics and custom face images."""
    
    def __init__(self, player_id, assets, custom_face=None):
        self.player_id = player_id
        self.current_head_scale = 1.0
        if player_id == 1:
            # ══ THE LAWMAN (Cowboy) ══
            lawman_skin = (255, 219, 172)   # #FFDBAC Pale Gold
            lawman_hair = (40, 28, 15)      # dark brown hair
            lawman_brow = (65, 42, 18)
            arm_color   = (128, 0, 0)       # #800000 Maroon arms
            leg_color   = (47, 79, 79)      # #2F4F4F Dark Slate Grey legs
            leg_color_b = (37, 65, 65)      # slightly darker back leg
            shoe_c      = (75, 54, 33)      # #4B3621 Dark Leather
            shoe_h      = (120, 85, 55)

            self.head        = create_head(skin_color=lawman_skin, hair_color=lawman_hair, brow_color=lawman_brow)
            self.head_closed = create_head_closed(skin_color=lawman_skin, hair_color=lawman_hair, brow_color=lawman_brow)
            self.torso       = self._make_cowboy_torso()
            self.arm_r       = create_arm(arm_color, skin_color=lawman_skin)
            self.arm_l       = create_arm(arm_color, skin_color=lawman_skin)
            self.leg_r       = create_leg(leg_color,   shoe=shoe_c, shoe_hi=shoe_h)
            self.leg_l       = create_leg(leg_color_b, shoe=shoe_c, shoe_hi=shoe_h)
            self.cowboy_hat  = create_cowboy_hat()
        else:
            # ══ THE OUTLAW (Bandit) ══
            outlaw_skin = (210, 180, 140)   # #D2B48C Desert Tan
            arm_color   = (224, 224, 224)   # #E0E0E0 Platinum Grey
            leg_color   = (224, 224, 224)
            stripe_c    = (0, 0, 0)         # #000000 Black stripes
            shoe_c      = (26, 26, 26)      # #1A1A1A Black Stealth Boots
            shoe_h      = (50, 50, 50)

            self.head        = create_outlaw_head()
            self.head_closed = create_outlaw_head_closed()
            self.torso       = self._make_outlaw_torso()
            self.arm_r       = create_arm(arm_color, skin_color=outlaw_skin, stripe_color=stripe_c)
            self.arm_l       = create_arm(arm_color, skin_color=outlaw_skin, stripe_color=stripe_c)
            self.leg_r       = create_leg(leg_color, shoe=shoe_c, shoe_hi=shoe_h, stripe_color=stripe_c)
            self.leg_l       = create_leg(leg_color, shoe=shoe_c, shoe_hi=shoe_h, stripe_color=stripe_c)
            self.cowboy_hat  = None

        # Shared weapon sprites (same for both characters)
        self.gun_surf  = create_gun()
        self.shotgun_surf = create_shotgun()
        self.shotgun_surf_f = pygame.transform.flip(self.shotgun_surf, True, False)
        self.bazooka_surf = create_bazooka()
        self.bazooka_surf_f = pygame.transform.flip(self.bazooka_surf, True, False)
        self.knife_surf = create_knife()
        self.current_weapon = "pistol"

        # ── Pre-cache flipped sprites for performance ──
        self.head_f        = pygame.transform.flip(self.head, True, False)
        self.head_closed_f = pygame.transform.flip(self.head_closed, True, False)
        self.torso_f     = pygame.transform.flip(self.torso, True, False)
        self.arm_r_f     = pygame.transform.flip(self.arm_r, True, False)
        self.arm_l_f     = pygame.transform.flip(self.arm_l, True, False)
        self.leg_r_f     = pygame.transform.flip(self.leg_r, True, False)
        self.leg_l_f     = pygame.transform.flip(self.leg_l, True, False)
        self.gun_surf_f  = pygame.transform.flip(self.gun_surf, True, False)
        self.knife_surf_f = pygame.transform.flip(self.knife_surf, True, False)
        if self.cowboy_hat is not None:
            self.cowboy_hat_f = pygame.transform.flip(self.cowboy_hat, True, False)
        else:
            self.cowboy_hat_f = None

        # Custom face (bobblehead) — pre-cache flipped version
        self.custom_face = custom_face
        self.custom_face_base_scale = 1.0  # set by game.py from settings
        if self.custom_face is not None:
            self.custom_face_f = pygame.transform.flip(self.custom_face, True, False)
        else:
            self.custom_face_f = None

        # Animation state
        self.walk_cycle   = 0.0
        self.arm_r_angle  = 0.0
        self.knife_phase  = 0
        self.knife_timer  = 0.0
        self.gun_recoil   = 0.0
        self.is_ragdoll   = False
        self.parts_physics = []

        # Jump animation state — separate front/back for proper body shape
        self.jump_leg_f  = 0.0   # front leg angle
        self.jump_leg_b  = 0.0   # back leg angle
        self.jump_arm_f  = 0.0   # front arm angle
        self.jump_arm_b  = 0.0   # back arm angle
        self.jump_torso_lean = 0.0
        self.jump_head_tilt  = 0.0
        self.was_airborne    = False
        self.land_timer      = 0.0

        # Idle breathing
        self.breathe_cycle = 0.0

        # Eye blink
        self.blink_timer    = random.uniform(2.5, 5.0)
        self.is_blinking    = False
        self.blink_duration = 0.0

        # Hat bounce (spring physics)
        self.hat_offset_y = 0.0
        self.hat_vel_y    = 0.0

        # Turn lean
        self.prev_facing  = 1
        self.turn_lean    = 0.0

        # Squash/stretch
        self.squash_x = 1.0
        self.squash_y = 1.0

        # Hit flash
        self.hit_flash = 0.0

        # Death freeze (Tier 3: anticipation pause before ragdoll)
        self._death_pending = False
        self._death_freeze = 0.0
        self._death_x = 0
        self._death_y = 0
        self._death_facing = 1
        self._death_hit_dir = 0
        self._death_is_cliff = False

        # Pre-cached shadow ellipses (avoid per-frame Surface allocation)
        self._shadow_layers = []
        for sw, sh, sa in [(28, 5, 45), (22, 4, 35), (14, 3, 50)]:
            ss = pygame.Surface((sw, sh), pygame.SRCALPHA)
            pygame.draw.ellipse(ss, (0, 0, 0, sa), (0, 0, sw, sh))
            self._shadow_layers.append((ss, sw, sh))

    def _make_cowboy_torso(self):
        """Lawman torso — Deep Crimson #B22222 with Gold #FFD700 accents."""
        S = 4
        big     = pygame.Surface((16*S, 22*S), pygame.SRCALPHA)
        jacket  = (178, 34, 34)     # #B22222 Firebrick Red
        jkt_dk  = (128, 20, 20)
        jkt_hi  = (210, 60, 60)
        gold    = (255, 215, 0)     # #FFD700 Gold
        gold_dk = (200, 170, 0)
        belt_c  = (50, 50, 50)      # dark belt
        ol      = (0, 0, 0)         # cel-shaded black outline

        # Main body fill
        pygame.draw.rect(big, jacket, (0, 0, 16*S, 22*S), border_radius=3*S)
        pygame.draw.rect(big, jkt_hi, (1*S, 1*S, 6*S, 8*S), border_radius=2*S)
        # 3D rim light + shadow
        pygame.draw.rect(big, (220, 75, 75), (1*S, 2*S, 2*S, 14*S), border_radius=S)
        pygame.draw.rect(big, (100, 15, 15), (13*S, 2*S, 2*S, 14*S), border_radius=S)
        # V lapels
        pygame.draw.polygon(big, jkt_dk,
            [(5*S,0),(8*S,7*S),(7*S,22*S),(5*S,22*S),(4*S,7*S)])
        pygame.draw.polygon(big, jkt_dk,
            [(11*S,0),(8*S,7*S),(9*S,22*S),(11*S,22*S),(12*S,7*S)])
        # Collar V
        pygame.draw.polygon(big, (160, 28, 28), [(5*S,0),(11*S,0),(8*S,5*S)])
        # Gold waistcoat buttons
        for by in [7, 10, 13]:
            pygame.draw.circle(big, gold, (8*S, by*S), S)
            pygame.draw.circle(big, gold_dk, (8*S, by*S), S, 1)
        # Belt
        pygame.draw.rect(big, belt_c, (0, 18*S, 16*S, 4*S))
        # Gold buckle
        pygame.draw.rect(big, gold, (6*S, 18*S, 4*S, 4*S))
        pygame.draw.rect(big, gold_dk, (7*S, 19*S, 2*S, 2*S))
        # Belt holes
        for bx in [3, 5, 11, 13]:
            pygame.draw.circle(big, (30, 30, 30), (bx*S, 20*S), S//2)
        # Pocket flap on right side
        pygame.draw.line(big, jkt_dk, (11*S, 12*S), (14*S, 12*S), 2)
        pygame.draw.line(big, jkt_dk, (11*S, 12*S), (11*S, 15*S), 1)
        pygame.draw.line(big, jkt_dk, (14*S, 12*S), (14*S, 15*S), 1)
        # 2px black cel-shaded outline
        pygame.draw.rect(big, ol, (0, 0, 16*S, 22*S), 2, border_radius=3*S)

        return pygame.transform.smoothscale(big, (16, 22))

    def _make_outlaw_torso(self):
        """Outlaw torso — Platinum Grey #E0E0E0 with Black #000000 stripes."""
        S = 4
        big     = pygame.Surface((16*S, 22*S), pygame.SRCALPHA)
        base    = (224, 224, 224)    # #E0E0E0 Platinum Grey
        stripe  = (0, 0, 0)          # #000000 Black stripes
        belt_c  = (26, 26, 26)       # #1A1A1A dark belt
        ol      = (0, 0, 0)          # outline

        # Main body fill
        pygame.draw.rect(big, base, (0, 0, 16*S, 22*S), border_radius=3*S)
        # 3D shading
        pygame.draw.rect(big, (240, 240, 240), (1*S, 1*S, 5*S, 14*S), border_radius=S)
        pygame.draw.rect(big, (180, 180, 180), (12*S, 1*S, 3*S, 14*S), border_radius=S)
        # Thick horizontal black stripes
        stripe_h = 3 * S
        gap_h = 3 * S
        for sy in range(0, 18*S, stripe_h + gap_h):
            pygame.draw.rect(big, stripe, (0, sy, 16*S, stripe_h), border_radius=1)
        # Belt
        pygame.draw.rect(big, belt_c, (0, 18*S, 16*S, 4*S))
        pygame.draw.rect(big, (50, 50, 50), (6*S, 18*S, 4*S, 4*S))  # buckle area
        # Center seam
        pygame.draw.line(big, (160, 160, 160), (8*S, 2*S), (8*S, 17*S), 1)
        # Collar line
        pygame.draw.line(big, (140, 140, 140), (2*S, 1*S), (14*S, 1*S), 2)
        # 2px black cel-shaded outline
        pygame.draw.rect(big, ol, (0, 0, 16*S, 22*S), 2, border_radius=3*S)

        return pygame.transform.smoothscale(big, (16, 22))

    def update(self, player_state, vel_x, on_ground, dt, vel_y=0):
        """Update skeletal animation based on player state."""
        if self.is_ragdoll:
            self._update_ragdoll(dt)
            return
        
        # Tier 3: Death freeze countdown
        if self._death_pending:
            self._death_freeze -= dt
            if self._death_freeze <= 0:
                self._death_pending = False
                self._execute_ragdoll()
            return
        
        # Walking leg animation using sine wave
        if player_state == "WALKING" and on_ground:
            self.walk_cycle += 15.0 * dt
        else:
            # Snap to zero faster when not walking
            self.walk_cycle *= 0.3
            if abs(self.walk_cycle) < 0.1:
                self.walk_cycle = 0.0
        
        # Knife animation phases
        if self.knife_phase == 1:  # Raise
            self.arm_r_angle += 400 * dt
            if self.arm_r_angle >= 45:
                self.arm_r_angle = 45
                self.knife_phase = 2
        elif self.knife_phase == 2:  # Thrust forward
            self.arm_r_angle -= 900 * dt
            if self.arm_r_angle <= -45:
                self.arm_r_angle = -45
                self.knife_phase = 3
        elif self.knife_phase == 3:  # Return
            self.arm_r_angle += 500 * dt
            if self.arm_r_angle >= 0:
                self.arm_r_angle = 0
                self.knife_phase = 0
        
        # Gun recoil decay
        if self.gun_recoil > 0:
            self.gun_recoil = max(0, self.gun_recoil - 60 * dt)
        
        # ── JUMP ANIMATION ────────────────────────────
        # Each phase sets SEPARATE front/back targets for the
        # correct body silhouette matching the jump arc:
        #   LAUNCH  → compressed (both tucked)   ╷
        #   RISE    → extending                  ╱
        #   APEX    → spread wide (opposite)     ◠
        #   FALL    → bracing (both forward)      ╲
        #   LAND    → compressed (absorb squat)   ╵
        if not on_ground:
            if vel_y < JUMP_LAUNCH_VEL:          # LAUNCH — crouch burst
                tgt_lf = JUMP_LEG_LAUNCH          # both legs tuck up
                tgt_lb = JUMP_LEG_LAUNCH
                tgt_af = JUMP_ARM_LAUNCH          # both arms sweep back
                tgt_ab = JUMP_ARM_LAUNCH
                tgt_torso = JUMP_TORSO_LAUNCH
                tgt_head = JUMP_HEAD_LAUNCH
            elif vel_y < JUMP_RISE_VEL:          # RISE — extending
                tgt_lf = JUMP_LEG_RISE            # front leg forward
                tgt_lb = -JUMP_LEG_RISE * 0.5     # back leg trailing
                tgt_af = JUMP_ARM_RISE            # arms reaching up
                tgt_ab = JUMP_ARM_RISE * 0.5
                tgt_torso = 0
                tgt_head = -3
            elif vel_y <= JUMP_FALL_VEL:          # APEX — wide spread
                tgt_lf = JUMP_LEG_APEX            # front leg forward
                tgt_lb = -JUMP_LEG_APEX           # back leg backward
                tgt_af = JUMP_ARM_APEX            # front arm up
                tgt_ab = -JUMP_ARM_APEX           # back arm down
                tgt_torso = 0
                tgt_head = 0
            else:                                 # FALL — brace
                tgt_lf = JUMP_LEG_FALL            # both legs forward
                tgt_lb = JUMP_LEG_FALL * 0.6
                tgt_af = JUMP_ARM_FALL            # both arms trail up
                tgt_ab = JUMP_ARM_FALL * 0.7
                tgt_torso = JUMP_TORSO_FALL
                tgt_head = JUMP_HEAD_FALL
            # Auto-trigger stretch on first airborne frame
            if not self.was_airborne:
                self.trigger_launch()
            self.was_airborne = True
        elif self.was_airborne:
            # Just landed — absorb squat + auto-trigger squash
            self.trigger_land()
            tgt_lf = JUMP_LEG_LAND
            tgt_lb = JUMP_LEG_LAND
            tgt_af = JUMP_ARM_LAND
            tgt_ab = JUMP_ARM_LAND
            tgt_torso = JUMP_TORSO_LAND
            tgt_head = 4
            self.land_timer = JUMP_LAND_DURATION
            self.was_airborne = False
        elif self.land_timer > 0:
            # Landing recovery — ease back to neutral
            self.land_timer -= dt
            frac = max(0.0, self.land_timer / JUMP_LAND_DURATION)
            tgt_lf = JUMP_LEG_LAND * frac
            tgt_lb = JUMP_LEG_LAND * frac
            tgt_af = JUMP_ARM_LAND * frac
            tgt_ab = JUMP_ARM_LAND * frac
            tgt_torso = JUMP_TORSO_LAND * frac
            tgt_head = 4 * frac
        else:
            # Grounded — no jump influence
            tgt_lf = tgt_lb = tgt_af = tgt_ab = tgt_torso = tgt_head = 0
        # Smooth lerp — clamp factor to [0,1] to prevent overshoot
        lf = min(1.0, JUMP_LERP_LEGS  * dt)
        af = min(1.0, JUMP_LERP_ARMS  * dt)
        tf = min(1.0, JUMP_LERP_TORSO * dt)
        hf = min(1.0, JUMP_LERP_HEAD  * dt)
        self.jump_leg_f      += (tgt_lf    - self.jump_leg_f)      * lf
        self.jump_leg_b      += (tgt_lb    - self.jump_leg_b)      * lf
        self.jump_arm_f      += (tgt_af    - self.jump_arm_f)      * af
        self.jump_arm_b      += (tgt_ab    - self.jump_arm_b)      * af
        self.jump_torso_lean += (tgt_torso - self.jump_torso_lean) * tf
        self.jump_head_tilt  += (tgt_head  - self.jump_head_tilt)  * hf
        
        # Snap to zero when very close (prevent micro-jitter)
        if abs(self.jump_leg_f)      < 0.3: self.jump_leg_f      = 0.0
        if abs(self.jump_leg_b)      < 0.3: self.jump_leg_b      = 0.0
        if abs(self.jump_arm_f)      < 0.3: self.jump_arm_f      = 0.0
        if abs(self.jump_arm_b)      < 0.3: self.jump_arm_b      = 0.0
        if abs(self.jump_torso_lean) < 0.2: self.jump_torso_lean = 0.0
        if abs(self.jump_head_tilt)  < 0.2: self.jump_head_tilt  = 0.0

        # ── IDLE BREATHING ────────────────────────────
        if on_ground and player_state != "WALKING":
            self.breathe_cycle += 2.0 * dt
        else:
            self.breathe_cycle *= 0.85  # fade out quickly

        # ── EYE BLINK ────────────────────────────────
        if self.is_blinking:
            self.blink_duration -= dt
            if self.blink_duration <= 0:
                self.is_blinking = False
                self.blink_timer = random.uniform(2.5, 5.0)
        else:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.is_blinking = True
                self.blink_duration = 0.12

        # ── HAT BOUNCE (spring physics) ─────────────
        # Spring force pulling hat back to 0
        spring_k = 120.0
        damping  = 8.0
        self.hat_vel_y += (-self.hat_offset_y * spring_k - self.hat_vel_y * damping) * dt
        self.hat_offset_y += self.hat_vel_y * dt
        # Clamp to prevent wild oscillation
        self.hat_offset_y = max(-4.0, min(4.0, self.hat_offset_y))
        # Walk bob feeds into hat
        if player_state == "WALKING" and on_ground:
            self.hat_vel_y += math.sin(self.walk_cycle * 2) * 15.0 * dt
        # Landing kick
        if self.was_airborne and on_ground:
            self.hat_vel_y = -4.0

        # ── TURN LEAN ────────────────────────────────
        facing = 1 if vel_x >= 0 else -1
        if vel_x == 0:
            facing = self.prev_facing
        if facing != self.prev_facing:
            self.turn_lean = -6.0 * facing
            self.prev_facing = facing
        # Lerp back to 0
        self.turn_lean += (0 - self.turn_lean) * min(1.0, 8.0 * dt)
        if abs(self.turn_lean) < 0.2:
            self.turn_lean = 0.0

        # ── SQUASH/STRETCH ────────────────────────────
        # Lerp back to 1.0
        self.squash_x += (1.0 - self.squash_x) * min(1.0, 10.0 * dt)
        self.squash_y += (1.0 - self.squash_y) * min(1.0, 10.0 * dt)
        if abs(self.squash_x - 1.0) < 0.01:
            self.squash_x = 1.0
        if abs(self.squash_y - 1.0) < 0.01:
            self.squash_y = 1.0

        # ── HIT FLASH ────────────────────────────────
        if self.hit_flash > 0:
            self.hit_flash = max(0.0, self.hit_flash - dt)
    
    def trigger_knife(self):
        """Start the knife swing animation."""
        if self.knife_phase == 0:
            self.knife_phase = 1
    
    def trigger_gun_recoil(self, weapon_type="pistol"):
        """Kick the arm back to simulate gun recoil. Different weapons have different feels."""
        self.gun_recoil = 8.0
        self.current_weapon = weapon_type
        self.arm_r_angle = 25.0 if self.knife_phase == 0 else self.arm_r_angle
    
    def trigger_hit(self):
        """Flash the body white briefly when taking damage."""
        self.hit_flash = 0.15

    def trigger_land(self):
        """Squash the body horizontally when landing on the ground (cartoon impact feel)."""
        self.squash_x = 1.12
        self.squash_y = 0.88
        self.hat_vel_y = -5.0

    def trigger_launch(self):
        """Stretch the body vertically when jumping (cartoon launch feel)."""
        self.squash_x = 0.92
        self.squash_y = 1.10
    def draw(self, surface, x, y, facing, camera=None):
        if self.is_ragdoll:
            for part in self.parts_physics:
                part.draw(surface, camera)
            return

        flip = (facing == -1)
        t    = self.walk_cycle

        # Breathing offset (subtle torso rise/fall when idle)
        breathe_off = math.sin(self.breathe_cycle) * 1.5 if self.breathe_cycle > 0.1 else 0

        # Turn lean horizontal offset
        lean_off = int(self.turn_lean)

        # Anchor points
        feet_y    = int(y) + 72
        torso_cx  = int(x) + 24 + lean_off
        leg_top_y = feet_y - 26
        torso_y   = leg_top_y - 22 - int(breathe_off)
        torso_x   = torso_cx - 8
        arm_y     = torso_y + 2
        head_y    = torso_y - 23
        head_x    = torso_cx - 11

        # ── GROUND SHADOW (only when on/near ground) ──────
        # feet_y is the bottom of the character; when on ground it equals GROUND_Y+2
        # Only draw shadow when feet are near the ground surface
        dist_from_ground = abs(feet_y - (GROUND_Y + 2))
        if dist_from_ground < 8:
            shadow_cx = torso_cx
            shadow_y  = GROUND_Y + 2
            for ss, sw, sh in self._shadow_layers:
                surface.blit(ss, (shadow_cx - sw // 2, shadow_y - sh // 2))

        if not flip:
            leg_f_x = torso_cx + 2
            leg_b_x = torso_cx - 10
            arm_f_x = torso_cx + 8
            arm_b_x = torso_cx - 16
        else:
            leg_f_x = torso_cx - 10
            leg_b_x = torso_cx + 2
            arm_f_x = torso_cx - 16
            arm_b_x = torso_cx + 8

        # Walk angles — legs and arms swing
        leg_f_angle = math.sin(t) * 32
        leg_b_angle = math.sin(t + math.pi) * 32
        arm_f_angle = math.sin(t + math.pi) * 24
        arm_b_angle = math.sin(t) * 24

        # Jump pose — add per-limb jump angles
        leg_f_angle += self.jump_leg_f
        leg_b_angle += self.jump_leg_b
        arm_f_angle += self.jump_arm_f
        arm_b_angle += self.jump_arm_b

        # Weapon arm override
        cw = getattr(self, 'current_weapon', 'pistol')
        recoil_kick_f = min(1.0, self.gun_recoil / 8.0) if self.gun_recoil > 0 else 0.0

        if self.knife_phase == 0:
            if cw == "shotgun":
                base_f = -85 if not flip else 85
                base_b = -85 if not flip else 85
                tilt = recoil_kick_f * 20
                if flip: tilt = -tilt
                arm_f_angle = base_f + tilt
                arm_b_angle = base_b + tilt
            elif cw == "bazooka":
                base_f = -90 if not flip else 90
                tilt = recoil_kick_f * 10
                if flip: tilt = -tilt
                arm_f_angle = base_f + tilt

        weapon_angle = arm_f_angle
        arm_f_draw_x = arm_f_x
        arm_b_draw_x = arm_b_x

        if self.knife_phase == 0:
            if cw == "shotgun" or cw == "bazooka":
                if flip:
                    arm_f_draw_x -= 14
                    if cw == "shotgun":
                        arm_b_draw_x -= 14
                        
                push = int(recoil_kick_f * 6)
                if push > 0:
                    arm_f_draw_x = arm_f_draw_x - push if not flip else arm_f_draw_x + push
                    if cw == "shotgun":
                        arm_b_draw_x = arm_b_draw_x - push if not flip else arm_b_draw_x + push
            elif cw == "pistol" and self.gun_recoil > 0:
                if not flip:
                    weapon_angle = -85
                else:
                    weapon_angle = 85
                    arm_f_draw_x -= 14
        if self.knife_phase > 0:
            weapon_angle = self.arm_r_angle

        # Head bob — up/down during walk
        bob = int(abs(math.sin(t * 2)) * 2)

        # Head tilt — small left/right tilt matching stride rhythm
        # ±5 degrees, synced with walk cycle
        head_tilt = math.sin(t) * 5
        head_tilt = head_tilt if not flip else -head_tilt
        # Add jump head tilt
        head_tilt += self.jump_head_tilt

        # Walk depth — back limbs fade during stride peak
        walk_s = abs(math.sin(t))

        # Draw order — back to front
        # 1. Back leg
        bl_img = self.leg_l_f if flip else self.leg_l
        bl_angle = leg_b_angle if not flip else -leg_b_angle
        if abs(bl_angle) > 2.0:
            bl_img = pygame.transform.rotate(bl_img, -bl_angle)
        surface.blit(bl_img, (leg_b_x, leg_top_y))

        # 2. Back arm
        ba_img = self.arm_l_f if flip else self.arm_l
        ba_angle = arm_b_angle if not flip else -arm_b_angle
        if abs(ba_angle) > 2.0:
            ba_img = pygame.transform.rotate(ba_img, -ba_angle)
        surface.blit(ba_img, (arm_b_draw_x, arm_y))

        # 3. Torso — slight lean forward during walk + jump lean
        torso_lean = math.sin(t) * 1.5 + self.jump_torso_lean
        torso_lean = torso_lean if not flip else -torso_lean
        t_img = self.torso_f if flip else self.torso
        surface.blit(t_img, (torso_x + int(torso_lean), torso_y))

        # 4. Front leg
        fl_img = self.leg_r_f if flip else self.leg_r
        fl_angle = leg_f_angle if not flip else -leg_f_angle
        if abs(fl_angle) > 2.0:
            fl_img = pygame.transform.rotate(fl_img, -fl_angle)
        surface.blit(fl_img, (leg_f_x, leg_top_y))

        # Calculate where the hand/muzzle will be
        if not flip:
            recoil_arm_x = arm_f_x
        else:
            recoil_arm_x = arm_f_x - 14

        recoil_kick_f = min(1.0, self.gun_recoil / 8.0) if self.gun_recoil > 0 else 0.0
        kickback_x = int(recoil_kick_f * 6)
        push_x = -kickback_x if not flip else kickback_x

        # 4.5. Two-Handed Weapons (Behind Front Arm!)
        cw = getattr(self, 'current_weapon', 'pistol')
        if self.knife_phase == 0:
            if cw == 'bazooka':
                if not flip:
                    gx = recoil_arm_x - 4 + push_x
                else:
                    gx = recoil_arm_x - 18 + push_x
                    
                gy = head_y + 6
                tilt = recoil_kick_f * 10
                tilt = tilt if not flip else -tilt
                bz_img = self.bazooka_surf if not flip else self.bazooka_surf_f 
                if abs(tilt) > 1:
                    bz_img = pygame.transform.rotate(bz_img, tilt)
                surface.blit(bz_img, (gx, gy))

                if not flip:
                    self.muzzle_x = gx + 40
                    self.muzzle_y = gy + 4 - int(recoil_kick_f * 4)
                else:
                    self.muzzle_x = gx + 4
                    self.muzzle_y = gy + 4 - int(recoil_kick_f * 4)

            elif cw == 'shotgun':
                gy = arm_y + 4
                tilt = recoil_kick_f * 20
                tilt = tilt if not flip else -tilt
                sg_img = self.shotgun_surf if not flip else self.shotgun_surf_f 
                if abs(tilt) > 1:
                    sg_img = pygame.transform.rotate(sg_img, tilt)

                if not flip:
                    gx = recoil_arm_x + 6 + push_x
                    surface.blit(sg_img, (gx, gy - int(recoil_kick_f * 4)))
                    self.muzzle_x = gx + 30
                    self.muzzle_y = gy + 4 - int(recoil_kick_f * 8)
                else:
                    gx = recoil_arm_x - 20 + push_x
                    surface.blit(sg_img, (gx, gy - int(recoil_kick_f * 4)))     
                    self.muzzle_x = gx + 6
                    self.muzzle_y = gy + 4 - int(recoil_kick_f * 8)

        # 5. Front arm
        fa_img = self.arm_r_f if flip else self.arm_r
        if abs(weapon_angle) > 2.0:
            fa_img = pygame.transform.rotate(fa_img, -weapon_angle)
        
        arm_f_final_x = arm_f_draw_x
        arm_f_final_y = arm_y
        if self.knife_phase == 0 and cw in ("shotgun", "bazooka"):
             if recoil_kick_f > 0:
                 arm_f_final_y -= int(recoil_kick_f * 4)
             
        surface.blit(fa_img, (arm_f_final_x, arm_f_final_y))

        if not (self.knife_phase == 0 and cw in ('shotgun', 'bazooka')):
            self.muzzle_x = arm_f_final_x
            self.muzzle_y = arm_f_final_y

        # 6. Gun (One-handed Pistol, in front of Front Arm)
        if self.knife_phase == 0 and cw == 'pistol':
            gy = head_y + 10
            
            tilt = 0
            if getattr(self, 'is_aiming', False):
                aim_deg = math.degrees(math.atan2(-self.aim_y, self.aim_x))
                aim_offset = aim_deg if not flip else (aim_deg - 180)
                while aim_offset > 180: aim_offset -= 360
                while aim_offset < -180: aim_offset += 360
                tilt += aim_offset

            if not flip:
                gx = arm_f_final_x + 16
                if self.gun_recoil > 0:
                    p_img = self.gun_surf
                    if abs(tilt) > 1:
                        p_img = pygame.transform.rotate(p_img, tilt)
                        new_rect = p_img.get_rect(center=self.gun_surf.get_rect(topleft=(gx, gy)).center)
                        gx_d, gy_d = new_rect.x, new_rect.y
                    else:
                        gx_d, gy_d = gx, gy
                    surface.blit(p_img, (gx_d, gy_d))
                self.muzzle_x = gx + 22
                self.muzzle_y = gy + 3
            else:
                gx = arm_f_final_x - 16
                if self.gun_recoil > 0:
                    p_img = self.gun_surf_f
                    if abs(tilt) > 1:
                        p_img = pygame.transform.rotate(p_img, tilt)
                        new_rect = p_img.get_rect(center=self.gun_surf_f.get_rect(topleft=(gx, gy)).center)
                        gx_d, gy_d = new_rect.x, new_rect.y
                    else:
                        gx_d, gy_d = gx, gy
                    surface.blit(p_img, (gx_d, gy_d))
                self.muzzle_x = gx + 1
                self.muzzle_y = gy + 3

        # 7. Knife
        if self.knife_phase > 0:
            kx = arm_f_x + 8 if not flip else arm_f_x - 26
            k_img = self.knife_surf_f if flip else self.knife_surf
            surface.blit(k_img, (kx, arm_y + 13))

        # 8. Head — bob + tilt + lean + blink + **scale** (grows UPWARD)
        head_lean_x = int(torso_lean)
        hs = self.current_head_scale  # visual-only multiplier
        # Manual Y offset per player
        head_y_manual = HEAD_Y_OFFSET_P1 if self.player_id == 1 else HEAD_Y_OFFSET_P2
        if self.custom_face is not None:
            cf_img = self.custom_face_f if flip else self.custom_face
            # Constrain the HD image to the default head size at scale 1.0,
            # then multiply by custom_face_base_scale and hs — always scaling from raw.
            def_head_w, def_head_h = self.head.get_size()  # 22x24
            cf_w0, cf_h0 = cf_img.get_size()
            fit_scale = min(def_head_w / cf_w0, def_head_h / cf_h0)
            total = fit_scale * self.custom_face_base_scale * hs
            new_w = max(1, int(cf_w0 * total))
            new_h = max(1, int(cf_h0 * total))
            cf_img = pygame.transform.smoothscale(cf_img, (new_w, new_h))
            if abs(head_tilt) > 2.0:
                cf_img = pygame.transform.rotate(cf_img, -head_tilt)
            # Anchor at BOTTOM (neck) — grow upward only
            cf_w, cf_h = cf_img.get_size()
            cx_offset = (def_head_w - cf_w) // 2
            cy_offset = def_head_h - cf_h  # bottom-anchor: all extra goes UP
            surface.blit(cf_img, (head_x + head_lean_x + cx_offset, head_y - bob + cy_offset + head_y_manual))
        else:
            if self.is_blinking:
                h_img = self.head_closed_f if flip else self.head_closed
            else:
                h_img = self.head_f if flip else self.head
            # Apply head scale
            if hs != 1.0:
                hw0, hh0 = h_img.get_size()
                h_img = pygame.transform.smoothscale(h_img, (max(1, int(hw0 * hs)), max(1, int(hh0 * hs))))
            if abs(head_tilt) > 2.0:
                h_img = pygame.transform.rotate(h_img, -head_tilt)
            # Anchor at BOTTOM (neck) — grow upward only
            if hs != 1.0:
                def_w, def_h = self.head.get_size()
                cur_w, cur_h = h_img.get_size()
                cx_off = (def_w - cur_w) // 2
                cy_off = def_h - cur_h  # bottom-anchor
                surface.blit(h_img, (head_x + head_lean_x + cx_off, head_y - bob + cy_off + head_y_manual))
            else:
                surface.blit(h_img, (head_x + head_lean_x, head_y - bob + head_y_manual))

        # 9. Cowboy hat — follows head + hat bounce
        # Skip hat if P1 has custom face and P1_HIDE_HAT_IF_CUSTOM is True
        draw_hat = self.cowboy_hat is not None
        if draw_hat and self.player_id == 1 and self.custom_face is not None and P1_HIDE_HAT_IF_CUSTOM:
            draw_hat = False
        if draw_hat:
            hat_img = self.cowboy_hat_f if flip else self.cowboy_hat
            hx  = head_x + 11 - 20 + head_lean_x
            hy  = head_y - bob - 14 + int(self.hat_offset_y) + head_y_manual
            # Scale hat proportionally with head — anchor at bottom
            if hs != 1.0:
                hat_w0, hat_h0 = hat_img.get_size()
                hat_img = pygame.transform.smoothscale(hat_img, (max(1, int(hat_w0 * hs)), max(1, int(hat_h0 * hs))))
                hx -= int((hat_w0 * hs - hat_w0) / 2)
                hy -= int(hat_h0 * hs - hat_h0)  # push hat upward too
            if abs(head_tilt) > 2.0:
                hat_img = pygame.transform.rotate(hat_img, -head_tilt)
            surface.blit(hat_img, (hx, hy))

        # (Hit flash removed — was drawing a white box over the character)
    
    def _draw_part(self, surface, img, x, y, angle_deg, flip):
        if flip:
            img = pygame.transform.flip(img, True, False)
        if abs(angle_deg) > 0.5:
            img = pygame.transform.rotate(img, -angle_deg)
        surface.blit(img, (x, y))
    
    def _draw_part_img(self, img, angle_deg, flip):
        """Like _draw_part but returns the image instead of blitting."""
        if flip:
            img = pygame.transform.flip(img, True, False)
        if abs(angle_deg) > 0.5:
            img = pygame.transform.rotate(img, -angle_deg)
        return img
    
    def trigger_ragdoll(self, x, y, facing, hit_dir=0, is_cliff=False):
        """Convert body to ragdoll physics on death.
        
        hit_dir: -1 = hit from left, +1 = hit from right, 0 = neutral
        is_cliff: True = cliff fall (tumble mode, no explosion)
        """
        # --- Tier 3: Anticipation freeze ---
        self._death_freeze = 0.08  # seconds to freeze before ragdoll
        self._death_x = x
        self._death_y = y
        self._death_facing = facing
        self._death_hit_dir = hit_dir
        self._death_is_cliff = is_cliff
        self._death_pending = True
    
    def _execute_ragdoll(self):
        """Actually spawn ragdoll parts after the death freeze."""
        x = self._death_x
        y = self._death_y
        facing = self._death_facing
        hit_dir = self._death_hit_dir
        
        if self._death_is_cliff:
            # --- Tier 4: Cliff tumble ---
            # Individual parts falling together (no expensive composite rotation)
            self.is_ragdoll = True
            drift = facing * random.uniform(30, 80)
            spin_base = facing * random.uniform(150, 300)
            
            parts = [
                (self.head,  int(x)+13, int(y)),
                (self.torso, int(x)+16, int(y)+22),
                (self.arm_r, int(x)+30, int(y)+24),
                (self.arm_l, int(x)+4,  int(y)+24),
                (self.leg_r, int(x)+26, int(y)+46),
                (self.leg_l, int(x)+8,  int(y)+46),
            ]
            if self.cowboy_hat is not None:
                parts.append((self.cowboy_hat, int(x)+4, int(y)-10))
            
            for img, px, py in parts:
                p = RagdollPart(
                    img, px, py,
                    drift + random.uniform(-20, 20),
                    random.uniform(-30, 30),
                    rest_angle=0, is_tumble=True
                )
                p.spin = spin_base + random.uniform(-50, 50)
                self.parts_physics.append(p)
            return
        
        self.is_ragdoll = True
        
        # --- Tier 1: Directional ragdoll ---
        # hit_dir > 0 means hit came from right, so parts fly LEFT
        # hit_dir < 0 means hit came from left, so parts fly RIGHT
        fly_dir = -hit_dir if hit_dir != 0 else facing
        
        # Base velocities biased by hit direction
        fly_x = fly_dir * random.uniform(80, 180)
        
        # Rest angles for Tier 5 (settle pose)
        # head=0 (upright), torso=90 (flat), arms=45, legs=-30
        part_configs = [
            # (img, px, py, vx, vy, rest_angle)
            (self.head,  int(x)+13, int(y),
             fly_x + random.uniform(-60, 60),
             random.uniform(-520, -350), 0),
            (self.torso, int(x)+16, int(y)+22,
             fly_x * 0.5 + random.uniform(-40, 40),
             random.uniform(-200, -100), 90 * fly_dir),
            (self.arm_r, int(x)+30, int(y)+24,
             fly_x + random.uniform(50, 150),
             random.uniform(-420, -250), 45 * fly_dir),
            (self.arm_l, int(x)+4,  int(y)+24,
             fly_x + random.uniform(-150, -50),
             random.uniform(-420, -250), -45 * fly_dir),
            (self.leg_r, int(x)+26, int(y)+46,
             fly_x + random.uniform(30, 120),
             random.uniform(-320, -150), -30 * fly_dir),
            (self.leg_l, int(x)+8,  int(y)+46,
             fly_x + random.uniform(-120, -30),
             random.uniform(-320, -150), 30 * fly_dir),
        ]
        
        # Add hat as a ragdoll part too
        if self.cowboy_hat is not None:
            part_configs.append(
                (self.cowboy_hat, int(x)+4, int(y)-10,
                 fly_x + random.uniform(-100, 100),
                 random.uniform(-600, -400), 0)
            )
        
        for img, px, py, vx, vy, rest_ang in part_configs:
            self.parts_physics.append(RagdollPart(img, px, py, vx, vy, rest_ang))
    
    def _update_ragdoll(self, dt):
        """Update all ragdoll parts."""
        for part in self.parts_physics:
            part.update(dt)


class RagdollPart:
    """One piece of the death ragdoll (head, torso, arm, leg, etc.).
    Has its own velocity, spin, gravity, and bounces off the ground a few times
    before fading out. Used to create the "body flying apart" effect on death."""
    
    def __init__(self, img, x, y, vel_x, vel_y, rest_angle=0, is_tumble=False):
        self.img = img
        self.x = float(x)
        self.y = float(y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.angle = 0.0
        self.spin = random.uniform(-300, 300)
        self.rest_angle = rest_angle
        self.is_tumble = is_tumble
        
        # Tier 2: Multi-bounce
        self.bounce_count = 0
        self.max_bounces = 3
        self.bounce_energy = [0.35, 0.20, 0.10]  # decreasing restitution
        
        # Tier 2: Fade
        self.settled = False
        self.alpha = 255
        self.fade_timer = 0.0
        self.fade_duration = 2.0
        self.fully_faded = False
        
        # Air drag
        self.drag = 0.98
    
    def update(self, dt):
        """Update ragdoll part physics."""
        if self.fully_faded:
            return
        
        # Tier 2: Fade after settling
        if self.settled:
            self.fade_timer += dt
            t = min(1.0, self.fade_timer / self.fade_duration)
            self.alpha = int(255 * (1.0 - t))
            if self.alpha <= 0:
                self.alpha = 0
                self.fully_faded = True
            
            # Tier 5: Lerp angle toward rest pose while fading
            angle_diff = self.rest_angle - self.angle
            if abs(angle_diff) > 1:
                self.angle += angle_diff * min(1.0, 3.0 * dt)
            return
        
        # Physics
        self.vel_y += GRAVITY * dt
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        # Air drag
        self.vel_x *= self.drag
        
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.angle += self.spin * dt
        
        # Spin damping
        self.spin *= 0.995
        
        # Clamp to virtual canvas horizontally
        self.x = max(0, min(self.x, VIRTUAL_W))
        
        # Tier 4: Tumble — fall off screen then vanish
        if self.is_tumble:
            if self.y > GROUND_Y + 200:
                self.settled = True
                self.fade_duration = 0.3  # quick vanish for cliff falls
            return
        
        # Ground collision with multi-bounce
        ground_y = GROUND_Y - self.img.get_height()
        if self.y >= ground_y:
            self.y = ground_y
            
            if self.bounce_count < self.max_bounces:
                restitution = self.bounce_energy[self.bounce_count]
                self.vel_y *= -restitution
                self.vel_x *= 0.6
                self.spin *= 0.4
                self.bounce_count += 1
            else:
                # All bounces used — settle
                self.vel_y = 0
                self.vel_x *= 0.85
                self.spin *= 0.85
                
                if abs(self.vel_x) < 5 and abs(self.spin) < 10:
                    self.settled = True
    
    def draw(self, surface, camera):
        """Draw ragdoll part with alpha fade."""
        if self.fully_faded:
            return
        
        rotated = pygame.transform.rotate(self.img, self.angle)
        
        # Apply alpha fade
        if self.alpha < 255:
            rotated = rotated.copy()
            rotated.set_alpha(self.alpha)
        
        surface.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))

