# src/animation.py

import pygame
import math
import random
from src.constants import GRAVITY, MAX_FALL_SPEED, GROUND_Y, VIRTUAL_W


def create_head():
    """Smooth 3D head with rich detail — rendered at 3x."""
    S = 3
    big = pygame.Surface((22*S, 24*S), pygame.SRCALPHA)

    skin = (210, 170, 115)
    dark = (170, 125,  75)

    face_pts = [(p[0]*S, p[1]*S) for p in [
        (11,  1), (20,  8), (21, 15), (16, 22),
        (11, 24), ( 6, 22), ( 1, 15), ( 2,  8),
    ]]
    pygame.draw.polygon(big, skin, face_pts)
    pygame.draw.polygon(big, dark, face_pts, 2)

    # Multi-gradient face shading
    pygame.draw.ellipse(big, (235, 200, 145), (6*S, 4*S, 10*S, 6*S))    # forehead glow
    pygame.draw.ellipse(big, (225, 190, 135), (5*S, 8*S, 12*S, 5*S))    # mid-face glow
    pygame.draw.ellipse(big, (175, 135,  85), (7*S, 19*S, 8*S, 4*S))    # chin shadow
    # Jaw highlight — soft glow under cheekbone
    pygame.draw.ellipse(big, (220, 182, 125), (4*S, 16*S, 6*S, 4*S))
    # Left temple gradient — 2 strips for smoother falloff
    pygame.draw.line(big, (245, 215, 160), (2*S, 9*S), (2*S, 18*S), 3)
    pygame.draw.line(big, (230, 195, 140), (3*S, 8*S), (3*S, 19*S), 2)
    # Right temple shadow — 2 strips
    pygame.draw.line(big, (160, 115,  65), (19*S, 9*S), (19*S, 18*S), 3)
    pygame.draw.line(big, (180, 135,  80), (18*S, 8*S), (18*S, 19*S), 2)

    # Cheek volumes
    pygame.draw.ellipse(big, (225, 185, 130), (3*S, 7*S, 7*S, 7*S))
    pygame.draw.ellipse(big, (195, 150,  95), (3*S, 14*S, 7*S, 6*S))
    pygame.draw.ellipse(big, (225, 185, 130), (12*S, 7*S, 7*S, 7*S))
    pygame.draw.ellipse(big, (195, 150,  95), (12*S, 14*S, 7*S, 6*S))

    # Ear suggestion — small bumps on sides
    pygame.draw.ellipse(big, (200, 160, 105), (0, 10*S, 3*S, 5*S))
    pygame.draw.ellipse(big, (185, 142,  90), (0, 11*S, 2*S, 3*S))
    pygame.draw.ellipse(big, (200, 160, 105), (20*S, 10*S, 3*S, 5*S))
    pygame.draw.ellipse(big, (185, 142,  90), (21*S, 11*S, 2*S, 3*S))

    # Hair
    hair = (40, 28, 15)
    highlight = (80, 58, 30)
    hair_pts = [(p[0]*S, p[1]*S) for p in [
        (2, 8), (3, 3), (7, 0), (15, 0), (19, 3), (20, 8),
        (17, 6), (14, 2), (8, 2), (5, 6)
    ]]
    pygame.draw.polygon(big, hair, hair_pts)
    for pts in [[(7,2),(9,-3),(11,2)], [(10,1),(12,-4),(14,1)], [(13,2),(15,-2),(17,3)]]:
        pygame.draw.polygon(big, hair, [(p[0]*S, p[1]*S) for p in pts])
    # Hair volume highlights
    pygame.draw.line(big, highlight, (8*S, 1*S), (14*S, 1*S), 3)
    pygame.draw.line(big, highlight, (9*S, 0), (13*S, 0), 2)
    pygame.draw.line(big, (95, 70, 35), (4*S, 4*S), (3*S, 7*S), 2)
    pygame.draw.ellipse(big, (55, 38, 20), (9*S, 0, 5*S, 3*S))  # hair crown glow
    # Sideburns
    pygame.draw.rect(big, hair, (2*S, 7*S, 2*S, 5*S))
    pygame.draw.rect(big, hair, (18*S, 7*S, 2*S, 5*S))
    # Secondary strands
    pygame.draw.line(big, (65, 45, 22), (6*S, 3*S), (10*S, 1*S), 1)
    pygame.draw.line(big, (65, 45, 22), (12*S, 1*S), (16*S, 3*S), 1)

    # Face details
    pygame.draw.line(big, (190, 150, 100), (11*S, 10*S), (11*S, 16*S), 1)  # nose bridge
    pygame.draw.line(big, (185, 145, 95), (5*S, 8*S), (17*S, 8*S), 2)      # brow ridge

    return pygame.transform.smoothscale(big, (22, 24))

def create_torso():
    """Smooth 3D torso with rich gradient shading — rendered at 3x."""
    S = 3
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

def create_arm(color, w=8, h=22):
    """Smooth 3D arm with hand shape — rendered at 3x."""
    S = 3
    big = pygame.Surface((w*S, h*S), pygame.SRCALPHA)
    skin       = (210, 170, 115)
    skin_dk    = (185, 145,  95)
    skin_sh    = (160, 120,  75)
    fist_color = tuple(max(0, c - 30) for c in color)
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

    # ── HAND SHAPE ────────────────────────────────
    # Palm — rounded wider block
    pygame.draw.rect(big, skin, (0, 19*S, 7*S, 4*S), border_radius=2*S)
    # Palm highlight — 3D roundness
    pygame.draw.ellipse(big, (225, 188, 132), (1*S, 19*S, 4*S, 3*S))
    # Palm shadow — right side
    pygame.draw.line(big, skin_sh, (6*S, 19*S), (6*S, 22*S), 2)
    # Thumb nub — small ellipse on left side
    pygame.draw.ellipse(big, skin, (0, 18*S, 3*S, 3*S))
    pygame.draw.ellipse(big, (220, 180, 125), (0, 18*S, 2*S, 2*S))  # thumb highlight
    # Finger bumps — 3 small rounded rects along bottom
    for fx in [0, 2, 4]:
        pygame.draw.rect(big, skin_dk, (fx*S + S//2, 22*S, 2*S, 2*S), border_radius=S)
    # Knuckle ridge line
    pygame.draw.line(big, skin_sh, (1*S, 22*S), (6*S, 22*S), 2)
    # Palm crease lines
    pygame.draw.line(big, skin_sh, (1*S, 20*S), (5*S, 20*S), 1)
    pygame.draw.line(big, skin_sh, (2*S, 21*S), (5*S, 21*S), 1)

    # ── 3D ARM SHADING ────────────────────────────
    # 3-strip gradient: rim → mid → shadow
    pygame.draw.line(big, rim,    (1*S, 1*S), (1*S, 18*S), 3)
    pygame.draw.line(big, mid_lt, (2*S, 1*S), (2*S, 18*S), 2)
    pygame.draw.line(big, mid_dk, (5*S, 1*S), (5*S, 18*S), 2)
    pygame.draw.line(big, darker, (6*S, 1*S), (6*S, 18*S), 3)
    # Shoulder specular
    pygame.draw.rect(big, lighter, (2*S, 1*S, 3*S, 5*S), border_radius=2*S)
    # Mid-arm muscle bulge
    pygame.draw.ellipse(big, mid_lt, (2*S, 5*S, 4*S, 4*S))
    # Elbow joint shadow
    pygame.draw.line(big, darker, (2*S, 11*S), (5*S, 11*S), 2)
    # Forearm tendon line
    pygame.draw.line(big, mid_dk, (3*S, 14*S), (3*S, 18*S), 1)
    # Wrist crease
    pygame.draw.line(big, darker, (1*S, 18*S), (5*S, 18*S), 1)
    return pygame.transform.smoothscale(big, (w, h))

def create_leg(color, w=11, h=26):
    """Smooth 3D leg with multi-gradient shading — rendered at 3x."""
    S = 3
    big = pygame.Surface((w*S, h*S), pygame.SRCALPHA)
    thigh_color = color
    shin_color  = tuple(max(0, c - 25) for c in color)
    darker      = tuple(max(0, c - 55) for c in color)
    mid_dk      = tuple(max(0, c - 35) for c in color)
    rim         = tuple(min(255, c + 65) for c in color)
    mid_lt      = tuple(min(255, c + 30) for c in color)
    shoe_color  = (62,  38, 12)
    toe_color   = (185, 88, 28)

    # Thigh
    pygame.draw.rect(big, thigh_color, (1*S, 0, 9*S, 11*S), border_radius=3*S)
    # Knee
    pygame.draw.rect(big, thigh_color, (2*S, 10*S, 7*S, 5*S))
    # Shin
    pygame.draw.rect(big, shin_color, (2*S, 14*S, 7*S, 8*S), border_radius=2*S)
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
    # Calf muscle bulge — highlight ellipse
    pygame.draw.ellipse(big, mid_lt, (3*S, 15*S, 4*S, 4*S))
    # Thigh highlight
    lighter = tuple(min(255, c + 45) for c in color)
    pygame.draw.rect(big, lighter, (3*S, 1*S, 4*S, 5*S), border_radius=2*S)
    # Shoe
    pygame.draw.rect(big, shoe_color, (1*S, 21*S, 11*S, 5*S), border_radius=2*S)
    pygame.draw.ellipse(big, toe_color, (5*S, 22*S, 7*S, 3*S))
    pygame.draw.rect(big, (35,16,2), (1*S, 21*S, 11*S, 5*S), 2, border_radius=2*S)
    # Boot top rim highlight
    pygame.draw.rect(big, (95, 62, 25), (3*S, 21*S, 4*S, 2*S), border_radius=S)
    pygame.draw.line(big, (85, 55, 18), (2*S, 21*S), (9*S, 21*S), 1)
    # Ankle crease
    pygame.draw.line(big, darker, (2*S, 21*S), (8*S, 21*S), 1)
    # Heel detail
    pygame.draw.rect(big, (42, 25, 8), (1*S, 24*S, 4*S, 2*S), border_radius=S)
    # Mid-shin taper highlight
    pygame.draw.line(big, rim, (4*S, 17*S), (6*S, 17*S), 1)
    return pygame.transform.smoothscale(big, (w, h))

def create_gun():
    """Smooth 3D gun — rendered at 3x then downsampled."""
    S = 3
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
    """Smooth 3D knife — rendered at 3x then downsampled."""
    S = 3
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

def create_cowboy_hat():
    """Smooth 3D cowboy hat — rendered at 3x then downsampled."""
    S = 3
    big = pygame.Surface((40*S, 22*S), pygame.SRCALPHA)

    hat_crown = (95,  65, 25)
    hat_dark  = (65,  42, 12)
    hat_band  = (192, 162, 82)
    hat_hi    = (125,  90, 35)
    brim_c    = (78,  52, 16)
    brim_sh   = (48,  30,  6)
    ol        = (35,  16,  2)

    # Brim
    pygame.draw.ellipse(big, brim_c,  (0, 12*S, 40*S, 9*S))
    pygame.draw.ellipse(big, brim_sh, (3*S, 15*S, 34*S, 5*S))
    pygame.draw.ellipse(big, (105, 75, 28), (4*S, 12*S, 32*S, 4*S))
    # Crown
    pygame.draw.rect(big, hat_crown, (10*S, 0, 20*S, 14*S), border_radius=4*S)
    pygame.draw.rect(big, hat_dark,  (11*S, 0, 18*S, 5*S), border_radius=3*S)
    pygame.draw.rect(big, hat_hi,    (11*S, 2*S, 6*S, 8*S), border_radius=2*S)
    # Crown specular
    pygame.draw.ellipse(big, (155, 118, 55), (13*S, 3*S, 5*S, 4*S))
    # Crown right shadow
    pygame.draw.rect(big, (72, 48, 15), (25*S, 2*S, 3*S, 10*S), border_radius=2*S)
    # Band
    pygame.draw.rect(big, hat_band, (10*S, 10*S, 20*S, 3*S))
    pygame.draw.line(big, (215,185,105), (11*S,10*S), (28*S,10*S), 2)
    # Outlines
    pygame.draw.ellipse(big, ol, (0, 12*S, 40*S, 9*S), 2)
    pygame.draw.rect(big, ol, (10*S, 0, 20*S, 14*S), 2, border_radius=4*S)

    return pygame.transform.smoothscale(big, (40, 22))


class AnimationManager:
    """Manages animation state and timing for various game objects."""
    
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
    """Skeletal animation system for player body parts."""
    
    def __init__(self, player_id, assets):
        if player_id == 1:
            # Cowboy — brown jacket arms, brown trouser legs
            arm_r_color  = (148, 108,  42)   # brown jacket sleeve
            arm_l_color  = (148, 108,  42)   # brown jacket sleeve
            leg_r_color  = (108,  78,  32)   # brown trouser front
            leg_l_color  = ( 88,  62,  22)   # brown trouser back (slightly darker)
        else:
            arm_r_color  = (170,  50, 200)
            arm_l_color  = ( 70, 180,  50)
            leg_r_color  = (200,  45,  45)
            leg_l_color  = (215, 195,  25)

        self.head      = create_head()
        if player_id == 1:
            self.torso = self._make_cowboy_torso()
        else:
            self.torso = create_torso()
        self.arm_r     = create_arm(arm_r_color)
        self.arm_l     = create_arm(arm_l_color)
        self.leg_r     = create_leg(leg_r_color)
        self.leg_l     = create_leg(leg_l_color)
        self.gun_surf  = create_gun()
        self.knife_surf = create_knife()

        # Cowboy hat for P1 only
        if player_id == 1:
            self.cowboy_hat = create_cowboy_hat()
        else:
            self.cowboy_hat = None

        # Animation state
        self.walk_cycle   = 0.0
        self.arm_r_angle  = 0.0
        self.knife_phase  = 0
        self.knife_timer  = 0.0
        self.gun_recoil   = 0.0
        self.is_ragdoll   = False
        self.parts_physics = []
    
    def _make_cowboy_torso(self):
        """Smooth 3D cowboy jacket — rendered at 3x then downsampled."""
        S = 3
        big     = pygame.Surface((16*S, 22*S), pygame.SRCALPHA)
        jacket  = (148, 108,  42)
        jkt_dk  = ( 95,  68,  18)
        jkt_hi  = (178, 142,  65)
        bandana = (195,  42,  32)
        belt    = (105, 105, 105)
        buckle  = (208, 182,  62)
        ol      = ( 35,  16,   2)

        pygame.draw.rect(big, jacket, (0, 0, 16*S, 22*S), border_radius=3*S)
        pygame.draw.rect(big, jkt_hi, (1*S, 1*S, 6*S, 8*S), border_radius=2*S)
        # 3D rim light + shadow
        pygame.draw.rect(big, (188, 152, 72), (1*S, 2*S, 2*S, 14*S), border_radius=S)
        pygame.draw.rect(big, (108,  75, 22), (13*S, 2*S, 2*S, 14*S), border_radius=S)
        # V lapels
        pygame.draw.polygon(big, jkt_dk,
            [(5*S,0),(8*S,7*S),(7*S,22*S),(5*S,22*S),(4*S,7*S)])
        pygame.draw.polygon(big, jkt_dk,
            [(11*S,0),(8*S,7*S),(9*S,22*S),(11*S,22*S),(12*S,7*S)])
        # Red bandana
        pygame.draw.polygon(big, bandana, [(5*S,0),(11*S,0),(8*S,6*S)])
        pygame.draw.ellipse(big, (225, 72, 52), (7*S, 1*S, 3*S, 2*S))
        # Bandana fold lines
        pygame.draw.line(big, (165, 32, 22), (6*S, 2*S), (8*S, 5*S), 1)
        pygame.draw.line(big, (165, 32, 22), (10*S, 2*S), (8*S, 5*S), 1)
        # Belt
        pygame.draw.rect(big, belt, (0, 18*S, 16*S, 4*S))
        pygame.draw.rect(big, buckle, (6*S, 18*S, 4*S, 4*S))
        pygame.draw.rect(big, (238, 218, 105), (7*S, 19*S, 2*S, 2*S))
        # Belt holes — tiny dots
        for bx in [3, 5, 11, 13]:
            pygame.draw.circle(big, (80, 80, 80), (bx*S, 20*S), S//2)
        # Pocket flap on right side
        pygame.draw.line(big, jkt_dk, (11*S, 12*S), (14*S, 12*S), 2)
        pygame.draw.line(big, jkt_dk, (11*S, 12*S), (11*S, 15*S), 1)
        pygame.draw.line(big, jkt_dk, (14*S, 12*S), (14*S, 15*S), 1)
        # Chest button
        pygame.draw.circle(big, (175, 138, 58), (8*S, 9*S), S)
        pygame.draw.circle(big, (125, 92, 32), (8*S, 9*S), S, 1)
        # Outline
        pygame.draw.rect(big, ol, (0, 0, 16*S, 22*S), 2, border_radius=3*S)

        return pygame.transform.smoothscale(big, (16, 22))

    def update(self, player_state, vel_x, on_ground, dt):
        """Update skeletal animation based on player state."""
        if self.is_ragdoll:
            self._update_ragdoll(dt)
            return
        
        # Walking leg animation using sine wave
        if player_state == "WALKING" and on_ground:
            self.walk_cycle += 15.0 * dt
        else:
            # Hard snap to zero when not walking
            # This stops any residual leg movement completely
            self.walk_cycle = self.walk_cycle * 0.4
            if abs(self.walk_cycle) < 0.05:
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
    
    def trigger_knife(self):
        """Called when knife key is pressed."""
        if self.knife_phase == 0:
            self.knife_phase = 1
    
    def trigger_gun_recoil(self):
        """Called when a bullet is fired."""
        self.gun_recoil = 8.0
        self.arm_r_angle = 25.0 if self.knife_phase == 0 else self.arm_r_angle
    
    def draw(self, surface, x, y, facing, camera=None):
        if self.is_ragdoll:
            for part in self.parts_physics:
                part.draw(surface, camera)
            return

        flip = (facing == -1)
        t    = self.walk_cycle

        # Anchor points — unchanged from original
        feet_y    = int(y) + 72
        torso_cx  = int(x) + 24
        leg_top_y = feet_y - 26
        torso_y   = leg_top_y - 22
        torso_x   = torso_cx - 8
        arm_y     = torso_y + 2
        head_y    = torso_y - 23
        head_x    = torso_cx - 11

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

        # Weapon arm override
        weapon_angle = arm_f_angle
        if self.gun_recoil > 0 and self.knife_phase == 0:
            weapon_angle = -30 if not flip else 30
        if self.knife_phase > 0:
            weapon_angle = self.arm_r_angle

        # Head bob — up/down during walk
        bob = int(abs(math.sin(t * 2)) * 2)

        # Head tilt — small left/right tilt matching stride rhythm
        # ±5 degrees, synced with walk cycle
        head_tilt = math.sin(t) * 5
        head_tilt = head_tilt if not flip else -head_tilt

        # Walk depth — back limbs fade during stride peak
        walk_s = abs(math.sin(t))

        # Draw order — back to front
        # 1. Back leg — fades at stride peak
        bl = self._draw_part_img(self.leg_l,
            leg_b_angle if not flip else -leg_b_angle, flip)
        bl = bl.copy()
        bl.set_alpha(int(255 - walk_s * 100))
        surface.blit(bl, (leg_b_x, leg_top_y))

        # 2. Back arm — fades at stride peak
        ba = self._draw_part_img(self.arm_l,
            arm_b_angle if not flip else -arm_b_angle, flip)
        ba = ba.copy()
        ba.set_alpha(int(255 - walk_s * 130))
        surface.blit(ba, (arm_b_x, arm_y))

        # 3. Torso — slight lean forward during walk
        torso_lean = math.sin(t) * 1.5
        torso_lean = torso_lean if not flip else -torso_lean
        self._draw_part(surface, self.torso,
            torso_x + int(torso_lean), torso_y, 0, flip)

        # 4. Front leg
        self._draw_part(surface, self.leg_r,
            leg_f_x, leg_top_y,
            leg_f_angle if not flip else -leg_f_angle, flip)

        # 5. Front arm
        self._draw_part(surface, self.arm_r,
            arm_f_x, arm_y,
            weapon_angle, flip)

        # 6. Gun
        if self.gun_recoil > 0 and self.knife_phase == 0:
            gx = arm_f_x + 8 if not flip else arm_f_x - 22
            surface.blit(
                self.gun_surf if not flip
                else pygame.transform.flip(self.gun_surf, True, False),
                (gx, arm_y + 14))

        # 7. Knife
        if self.knife_phase > 0:
            kx = arm_f_x + 8 if not flip else arm_f_x - 26
            surface.blit(
                self.knife_surf if not flip
                else pygame.transform.flip(self.knife_surf, True, False),
                (kx, arm_y + 13))

        # 8. Head — bob + tilt + lean
        head_lean_x = int(torso_lean)
        self._draw_part(surface, self.head,
            head_x + head_lean_x, head_y - bob, head_tilt, flip)

        # 9. Cowboy hat — follows head exactly
        if self.cowboy_hat is not None:
            hat = self.cowboy_hat
            hx  = head_x + 11 - 20 + head_lean_x
            hy  = head_y - bob - 14
            self._draw_part(surface, hat, hx, hy, head_tilt, flip)
    
    def _draw_part(self, surface, img, x, y, angle_deg, flip):
        if flip:
            img = pygame.transform.flip(img, True, False)
        if abs(angle_deg) > 0.5:
            big = pygame.transform.scale(
                img, (img.get_width()*2, img.get_height()*2))
            rot = pygame.transform.rotate(big, -angle_deg)
            img = pygame.transform.smoothscale(
                rot, (rot.get_width()//2, rot.get_height()//2))
        surface.blit(img, (x, y))
    
    def _draw_part_img(self, img, angle_deg, flip):
        """Like _draw_part but returns the image instead of blitting."""
        if flip:
            img = pygame.transform.flip(img, True, False)
        if abs(angle_deg) > 0.5:
            big = pygame.transform.scale(
                img, (img.get_width()*2, img.get_height()*2))
            rot = pygame.transform.rotate(big, -angle_deg)
            img = pygame.transform.smoothscale(
                rot, (rot.get_width()//2, rot.get_height()//2))
        return img
    
    def trigger_ragdoll(self, x, y, facing):
        """Convert body to ragdoll physics on death."""
        self.is_ragdoll = True
        
        # Each part gets a random scatter velocity
        part_configs = [
            (self.head,  int(x)+13, int(y),
             random.uniform(-200, 200),  random.uniform(-520, -320)),
            (self.torso, int(x)+16, int(y)+22,
             random.uniform(-100, 100),  random.uniform(-200, -100)),
            (self.arm_r, int(x)+30, int(y)+24,
             random.uniform(100, 320),   random.uniform(-420, -220)),
            (self.arm_l, int(x)+4,  int(y)+24,
             random.uniform(-320,-100),  random.uniform(-420, -220)),
            (self.leg_r, int(x)+26, int(y)+46,
             random.uniform(60, 220),    random.uniform(-320, -120)),
            (self.leg_l, int(x)+8,  int(y)+46,
             random.uniform(-220,-60),   random.uniform(-320, -120)),
        ]
        
        for img, px, py, vx, vy in part_configs:
            self.parts_physics.append(RagdollPart(img, px, py, vx, vy))
    
    def _update_ragdoll(self, dt):
        """Update all ragdoll parts."""
        for part in self.parts_physics:
            part.update(dt)


class RagdollPart:
    """Individual body part with physics when player dies."""
    
    def __init__(self, img, x, y, vel_x, vel_y):
        self.img = img
        self.x = float(x)
        self.y = float(y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.angle = 0.0
        self.spin = random.uniform(-300, 300)
        self.bounced = False
        self.settled = False
    
    def update(self, dt):
        """Update ragdoll part physics."""
        if self.settled:
            return
        
        self.vel_y += GRAVITY * dt
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.angle += self.spin * dt
        
        # Clamp to virtual canvas
        self.x = max(0, min(self.x, VIRTUAL_W))
        
        # One bounce on ground
        if self.y >= GROUND_Y - self.img.get_height():
            self.y = GROUND_Y - self.img.get_height()
            if not self.bounced:
                self.vel_y *= -0.35
                self.vel_x *= 0.6
                self.spin *= 0.4
                self.bounced = True
            else:
                self.vel_y = 0
                self.vel_x *= 0.9
                self.spin *= 0.9
                
                # Check if settled
                if abs(self.vel_x) < 5 and abs(self.spin) < 10:
                    self.settled = True
    
    def draw(self, surface, camera):
        """Draw ragdoll part."""
        rotated = pygame.transform.rotate(self.img, self.angle)
        # Draw at world position
        surface.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))
