# DUEL-STRIKE — COMPLETE PRODUCT REQUIREMENTS DOCUMENT (PRD)
### Version 1.0 | 2D Same-Screen Multiplayer Shooter | Python / pygame-ce

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Folder & File Architecture](#3-folder--file-architecture)
4. [Asset Manifest & Placeholders](#4-asset-manifest--placeholders)
5. [Game State Machine](#5-game-state-machine)
6. [Input System](#6-input-system)
7. [Physics System](#7-physics-system)
8. [Player Class — Full Specification](#8-player-class--full-specification)
9. [Skeletal Animation System](#9-skeletal-animation-system)
10. [Combat System — Gun](#10-combat-system--gun)
11. [Combat System — Knife](#11-combat-system--knife)
12. [Pickup System](#12-pickup-system)
13. [Arena & Environmental Design](#13-arena--environmental-design)
14. [Dynamic Camera / Zoom System](#14-dynamic-camera--zoom-system)
15. [Particle & VFX System](#15-particle--vfx-system)
16. [K.O. & Round Reset System](#16-ko--round-reset-system)
17. [UI / HUD System](#17-ui--hud-system)
18. [Menu & Pause System](#18-menu--pause-system)
19. [Collision Detection Strategy](#19-collision-detection-strategy)
20. [Full Class Architecture](#20-full-class-architecture)
21. [Rendering Pipeline](#21-rendering-pipeline)
22. [Performance & Stability Guidelines](#22-performance--stability-guidelines)
23. [Complete Main Game Loop](#23-complete-main-game-loop)
24. [Known Edge Cases & Bug Prevention](#24-known-edge-cases--bug-prevention)

---

## 1. PROJECT OVERVIEW

**Game Name:** Duel-Strike
**Genre:** 2D Arena Shooter / Fighting Game
**Platform:** PC — Windows (Single Machine, Single Keyboard)
**Players:** 2 (Local Multiplayer, same keyboard)
**View:** Side-scrolling 2D, single fixed arena
**Inspiration:** Mustapha, Eight Marbles, Mini Militia

### Core Experience Goals
- Fast-paced, skill-based combat between two human players
- Both players visible on screen at all times via dynamic zoom
- Satisfying physical hit feedback (blood sparks, ragdoll death)
- Zero ambiguity in controls — all actions are immediate, responsive
- Smooth, stable 60 FPS with no frame-rate-dependent physics bugs

---

## 2. TECHNOLOGY STACK

| Component | Library / Tool |
|---|---|
| Language | Python 3.11+ |
| Game Engine | **pygame-ce** (Community Edition, NOT standard pygame) |
| Math Helpers | `math`, `random` (stdlib) |
| Timing | `pygame.time.Clock` with delta-time (`dt`) |
| Rendering | Virtual Surface → scaled blit to window |
| GIF Playback | Custom frame-strip loader (GIFs pre-converted to PNG strips) |
| IDE | Visual Studio Code + Claude Code extension |

### Why pygame-ce?
- Faster rendering and better `pygame.transform.smoothscale` for zoom
- Actively maintained with bug fixes absent in vanilla pygame
- Install: `pip install pygame-ce`
- Import: `import pygame` (drop-in replacement, same API)

---

## 3. FOLDER & FILE ARCHITECTURE

```
duel_strike/
│
├── main.py                  # Entry point. Creates Game object and calls game.run()
│
├── src/
│   ├── __init__.py
│   ├── game.py              # Master Game class, main loop, state machine
│   ├── player.py            # Player class, skeletal body, state logic
│   ├── bullet.py            # Bullet class
│   ├── weapons.py           # Gun and Knife logic/data
│   ├── physics.py           # PhysicsObject base, gravity constants
│   ├── camera.py            # Dynamic zoom camera
│   ├── arena.py             # Platform, Barrel, Ground classes
│   ├── pickups.py           # HealthPack, AmmoPack, SpawnManager
│   ├── particles.py         # ParticleEmitter, BloodSpark, GifPlayer
│   ├── ui.py                # HealthBar, AmmoDisplay, KOScreen
│   ├── menu.py              # MainMenu, PauseMenu
│   ├── animation.py         # AnimationManager, frame sequencing
│   └── constants.py         # All magic numbers in one place
│
└── assets/
    ├── sprites/
    │   ├── p1_head.png
    │   ├── p1_torso.png
    │   ├── p1_arm_right.png
    │   ├── p1_arm_left.png
    │   ├── p1_leg_right.png
    │   ├── p1_leg_left.png
    │   ├── p2_head.png
    │   ├── p2_torso.png
    │   ├── p2_arm_right.png
    │   ├── p2_arm_left.png
    │   ├── p2_leg_right.png
    │   ├── p2_leg_left.png
    │   ├── barrel.png
    │   ├── platform.png
    │   └── ground_tile.png
    ├── pickups/
    │   ├── health_pack.png
    │   └── ammo_box.png
    ├── effects/
    │   ├── blood_strip.png   # Blood GIF converted to horizontal PNG strip
    │   └── ko_strip.png      # K.O. GIF converted to horizontal PNG strip
    ├── ui/
    │   ├── health_bar_bg.png
    │   ├── health_bar_fill.png
    │   ├── pause_icon.png
    │   └── menu_bg.png
    └── sounds/               # (Optional, for future audio)
```

---

## 4. ASSET MANIFEST & PLACEHOLDERS

All asset paths are defined in `constants.py` as string variables. This allows easy swapping without editing game logic.

```python
# constants.py — ASSET PATHS
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

IMG_BARREL        = "assets/sprites/barrel.png"
IMG_PLATFORM      = "assets/sprites/platform.png"
IMG_GROUND        = "assets/sprites/ground_tile.png"
IMG_HEALTH_PACK   = "assets/pickups/health_pack.png"
IMG_AMMO_BOX      = "assets/pickups/ammo_box.png"

GIF_BLOOD_STRIP   = "assets/effects/blood_strip.png"   # PNG strip, 4 frames wide
GIF_KO_STRIP      = "assets/effects/ko_strip.png"      # PNG strip, 6 frames wide
GIF_BLOOD_FRAMES  = 4
GIF_KO_FRAMES     = 6

IMG_MENU_BG       = "assets/ui/menu_bg.png"
IMG_PAUSE_ICON    = "assets/ui/pause_icon.png"
```

### Placeholder Generation (No Assets Yet)
If asset files do not exist, the code must auto-generate colored rectangles as placeholders at startup. This ensures the game runs completely even before real art is added.

```python
def load_or_placeholder(path: str, size: tuple, color: tuple) -> pygame.Surface:
    """Load image or return a colored rectangle if file not found."""
    try:
        return pygame.image.load(path).convert_alpha()
    except FileNotFoundError:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf
```

---

## 5. GAME STATE MACHINE

The game must implement a clean state machine. Only one state is active at any time. States do not overlap.

```
States:
  STATE_MENU      → Home screen, shows "Play" button
  STATE_PLAYING   → Active match, all systems running
  STATE_PAUSED    → Game frozen, pause overlay visible
  STATE_KO        → Match over, K.O. animation playing, auto-reset timer running
```

### State Transitions

```
STATE_MENU
  → [Click "Play"] → STATE_PLAYING

STATE_PLAYING
  → [Click Pause icon / press Esc] → STATE_PAUSED
  → [Player HP reaches 0] → STATE_KO

STATE_PAUSED
  → [Click "Continue"] → STATE_PLAYING
  → [Click "Start New"] → reset_game() → STATE_PLAYING
  → [Click "Exit"] → STATE_MENU

STATE_KO
  → [Timer expires, 3 seconds] → reset_game() → STATE_PLAYING
```

### Implementation in game.py

```python
class Game:
    def __init__(self):
        self.state = "STATE_MENU"

    def update(self, dt):
        if self.state == "STATE_PLAYING":
            self._update_playing(dt)
        elif self.state == "STATE_KO":
            self._update_ko(dt)
        # PAUSED and MENU only process UI events, no physics

    def draw(self):
        if self.state == "STATE_MENU":
            self.menu.draw(self.screen)
        elif self.state == "STATE_PLAYING":
            self._draw_playing()
        elif self.state == "STATE_PAUSED":
            self._draw_playing()         # Draw frozen game underneath
            self.pause_menu.draw(self.screen)  # Draw overlay on top
        elif self.state == "STATE_KO":
            self._draw_playing()
            self.ko_screen.draw(self.screen)
```

---

## 6. INPUT SYSTEM

### Critical Requirement
Both players press keys simultaneously. Standard `pygame.key.get_pressed()` returns ALL currently held keys every frame. This is the correct method — do NOT use KEYDOWN events for movement or shooting logic.

```python
# constants.py — CONTROLS
CONTROLS = {
    "p1": {
        "left":  pygame.K_a,
        "right": pygame.K_d,
        "jump":  pygame.K_w,
        "crouch": pygame.K_s,
        "shoot": pygame.K_c,
        "knife": pygame.K_v,
    },
    "p2": {
        "left":  pygame.K_j,
        "right": pygame.K_l,
        "jump":  pygame.K_i,
        "crouch": pygame.K_k,
        "shoot": pygame.K_n,
        "knife": pygame.K_b,
    }
}
```

### Input Processing Per Player Per Frame

```python
def handle_input(self, keys, dt):
    ctrl = self.controls  # dict from constants above

    # Horizontal movement
    if keys[ctrl["left"]]:
        self.vel_x = -PLAYER_SPEED
        self.facing = -1
    elif keys[ctrl["right"]]:
        self.vel_x = PLAYER_SPEED
        self.facing = 1
    else:
        self.vel_x = 0

    # Jump — only when on ground
    if keys[ctrl["jump"]] and self.on_ground:
        self.vel_y = -JUMP_FORCE
        self.on_ground = False

    # Crouch / Fast Fall
    if keys[ctrl["crouch"]]:
        if self.on_ground:
            self.state = "CROUCHING"
        else:
            self.vel_y = FAST_FALL_SPEED   # Large downward velocity

    # Shoot — detect NEW press this frame (not held)
    if keys[ctrl["shoot"]] and not self.shoot_held:
        self.try_shoot()
    self.shoot_held = keys[ctrl["shoot"]]

    # Knife — detect NEW press this frame
    if keys[ctrl["knife"]] and not self.knife_held:
        self.try_knife()
    self.knife_held = keys[ctrl["knife"]]
```

### Shoot Key — "Tap to Fire" Implementation
The shoot key fires ONE bullet per press. The player can fire quickly by tapping repeatedly. This is achieved by tracking `shoot_held` — the bullet is only fired on the frame the key transitions from NOT held to held.

```python
# This pattern prevents holding the key from auto-firing:
if keys[ctrl["shoot"]] and not self.shoot_held_last_frame:
    self.fire_bullet()
self.shoot_held_last_frame = keys[ctrl["shoot"]]
```

---

## 7. PHYSICS SYSTEM

All physics use **delta-time (dt)** multiplication. This ensures the game runs identically on slow and fast computers.

```python
# constants.py — PHYSICS
GRAVITY           = 1800     # px per second squared
JUMP_FORCE        = 620      # px per second (upward impulse)
PLAYER_SPEED      = 260      # px per second horizontal
FAST_FALL_SPEED   = 700      # px per second downward (fast fall override)
MAX_FALL_SPEED    = 900      # terminal velocity, clamp vel_y to this
GROUND_FRICTION   = 0.82     # multiplier per frame when on ground (reduces slide)
BULLET_SPEED      = 950      # px per second horizontal
VIRTUAL_W         = 2000     # Virtual canvas width in pixels
VIRTUAL_H         = 700      # Virtual canvas height in pixels
GROUND_Y          = 620      # Y coordinate of the top of the ground surface
```

### Physics Update Loop (per frame, per physics object)

```python
def apply_physics(self, dt):
    # Apply gravity if not on ground
    if not self.on_ground:
        self.vel_y += GRAVITY * dt
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)

    # Apply velocity to position
    self.x += self.vel_x * dt
    self.y += self.vel_y * dt

    # Ground collision
    if self.y >= GROUND_Y - self.height:
        self.y = GROUND_Y - self.height
        self.vel_y = 0
        self.on_ground = True

    # Apply friction when on ground and no directional input
    if self.on_ground and self.vel_x != 0 and not self.moving:
        self.vel_x *= GROUND_FRICTION
        if abs(self.vel_x) < 5:
            self.vel_x = 0

    # Arena boundary clamp — players cannot leave the map
    self.x = max(0, min(self.x, VIRTUAL_W - self.width))
```

### Platform Collision
Platforms are one-way: players land on top but can jump through from below.

```python
def check_platform_collision(self, platforms):
    for plat in platforms:
        plat_rect = plat.rect
        player_rect = self.get_rect()
        prev_bottom = self.y + self.height - self.vel_y * dt  # where feet were last frame

        if (player_rect.colliderect(plat_rect) and
                prev_bottom <= plat_rect.top + 5 and
                self.vel_y >= 0):
            self.y = plat_rect.top - self.height
            self.vel_y = 0
            self.on_ground = True
```

---

## 8. PLAYER CLASS — FULL SPECIFICATION

```python
class Player:
    def __init__(self, player_id: int, start_x: int, controls: dict, assets: dict):
        # Identity
        self.player_id = player_id       # 1 or 2
        self.controls  = controls

        # Position & Physics
        self.x         = float(start_x)
        self.y         = float(GROUND_Y - PLAYER_HEIGHT)
        self.vel_x     = 0.0
        self.vel_y     = 0.0
        self.on_ground = True
        self.facing    = 1 if player_id == 1 else -1  # 1=right, -1=left

        # Stats
        self.health    = 100
        self.max_health = 100
        self.ammo      = 67
        self.max_ammo  = 67
        self.alive     = True

        # State
        self.state     = "IDLE"   # IDLE, WALKING, JUMPING, CROUCHING, ATTACKING_GUN, ATTACKING_KNIFE, DEAD

        # Input tracking (edge detection for shoot/knife)
        self.shoot_held_last = False
        self.knife_held_last  = False

        # Combat cooldowns
        self.knife_cooldown   = 0.0   # seconds remaining before next knife swing allowed
        self.knife_active     = False # True during the stab animation window (hit detection active)
        self.knife_anim_timer = 0.0

        # Skeletal body (see Animation System section)
        self.body = SkeletalBody(player_id, assets)

        # Dead-body ragdoll parts (activated on death)
        self.ragdoll_parts = []

    def take_damage(self, amount: int, hit_pos: tuple):
        """Apply damage. Returns True if this hit killed the player."""
        if not self.alive:
            return False
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.die()
            return True
        return False

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def add_ammo(self, amount: int):
        """Returns True if pickup was consumed."""
        if self.ammo >= self.max_ammo:
            return False
        self.ammo = self.max_ammo
        return True

    def die(self):
        self.alive = False
        self.state = "DEAD"
        self.body.trigger_ragdoll(self.x, self.y, self.facing)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), PLAYER_WIDTH, PLAYER_HEIGHT)

    def get_knife_hitbox(self) -> pygame.Rect:
        """Knife hits a box directly in front of the player."""
        offset = PLAYER_WIDTH if self.facing == 1 else -KNIFE_RANGE
        return pygame.Rect(int(self.x) + offset, int(self.y) + 10, KNIFE_RANGE, PLAYER_HEIGHT - 20)
```

### Player States and Transitions

```
IDLE         → receives input → WALKING or JUMPING or CROUCHING
WALKING      → no input → IDLE
              → jump key → JUMPING
JUMPING      → lands on ground → IDLE
              → crouch key in air → FAST_FALL (subset of JUMPING)
CROUCHING    → release crouch key → IDLE
ATTACKING_GUN  → one frame, returns to previous movement state
ATTACKING_KNIFE→ animation completes (~200ms) → returns to previous movement state
DEAD         → permanent, cannot transition out (game resets entire match)
```

---

## 9. SKELETAL ANIMATION SYSTEM

### Body Structure
Each player is NOT a single sprite. It is a container of 6 independent surfaces rendered each frame relative to the torso anchor point.

```
Body Parts:
  torso       — center anchor, all other parts positioned relative to this
  head        — positioned above torso
  arm_right   — positioned right side of torso
  arm_left    — positioned left side of torso
  leg_right   — positioned below torso right
  leg_left    — positioned below torso left
```

### SkeletalBody Class

```python
class SkeletalBody:
    def __init__(self, player_id, assets):
        self.torso     = assets["torso"]
        self.head      = assets["head"]
        self.arm_r     = assets["arm_r"]
        self.arm_l     = assets["arm_l"]
        self.leg_r     = assets["leg_r"]
        self.leg_l     = assets["leg_l"]

        # Animation state variables
        self.walk_cycle    = 0.0    # 0..2*pi, driven by time
        self.arm_r_angle   = 0.0    # degrees, for knife/gun animation
        self.arm_r_offset  = (0, 0) # pixel offset for gun recoil

        self.knife_phase   = 0      # 0=idle, 1=raise, 2=thrust, 3=return
        self.knife_timer   = 0.0
        self.gun_recoil    = 0.0    # pixels of recoil remaining

        self.is_ragdoll    = False
        self.parts_physics = []     # List of RagdollPart on death

    def update(self, player_state, vel_x, on_ground, dt):
        if self.is_ragdoll:
            self._update_ragdoll(dt)
            return

        # Walking leg animation using sine wave
        if player_state == "WALKING" and on_ground:
            self.walk_cycle += 8.0 * dt   # speed of leg swing
        else:
            # Smoothly return legs to neutral
            self.walk_cycle *= 0.85

        # Knife animation phases
        if self.knife_phase == 1:   # Raise
            self.arm_r_angle += 400 * dt
            if self.arm_r_angle >= 45:
                self.arm_r_angle = 45
                self.knife_phase = 2
        elif self.knife_phase == 2: # Thrust forward
            self.arm_r_angle -= 900 * dt
            if self.arm_r_angle <= -45:
                self.arm_r_angle = -45
                self.knife_phase = 3
        elif self.knife_phase == 3: # Return
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
        self.gun_recoil = 6.0   # pixels

    def draw(self, surface, x, y, facing):
        """Draw all body parts to the virtual surface."""
        if self.is_ragdoll:
            for part in self.parts_physics:
                part.draw(surface)
            return

        # Flip all surfaces if facing left
        flip = (facing == -1)

        # Leg positions driven by sin wave
        leg_swing = math.sin(self.walk_cycle) * 18   # degrees

        # Draw order: back leg, back arm, torso, front leg, front arm, head
        torso_x = int(x)
        torso_y = int(y + 18)   # torso is offset down from player origin

        # Back leg
        self._draw_part(surface, self.leg_l, torso_x - 5, torso_y + 28,
                        -leg_swing if not flip else leg_swing, flip)
        # Back arm
        self._draw_part(surface, self.arm_l, torso_x - 8, torso_y + 6,
                        leg_swing * 0.5, flip)
        # Torso
        self._draw_part(surface, self.torso, torso_x, torso_y, 0, flip)
        # Front leg
        self._draw_part(surface, self.leg_r, torso_x + 5, torso_y + 28,
                        leg_swing if not flip else -leg_swing, flip)
        # Front arm (gun/knife arm)
        arm_angle = self.arm_r_angle + (-self.gun_recoil * 4 if not flip else self.gun_recoil * 4)
        self._draw_part(surface, self.arm_r, torso_x + 10, torso_y + 6,
                        arm_angle, flip)
        # Head
        self._draw_part(surface, self.head, torso_x + 2, torso_y - 22, 0, flip)

    def _draw_part(self, surface, img, x, y, angle_deg, flip):
        """Rotate and blit a single body part."""
        if flip:
            img = pygame.transform.flip(img, True, False)
        if abs(angle_deg) > 0.5:
            img = pygame.transform.rotate(img, angle_deg)
        rect = img.get_rect(center=(x + img.get_width()//2, y + img.get_height()//2))
        surface.blit(img, rect)
```

### Ragdoll System (Death Animation)

When a player dies, the 6 body parts become independent physics objects:

```python
def trigger_ragdoll(self, x, y, facing):
    self.is_ragdoll = True
    import random

    # Each part gets a random scatter velocity
    part_configs = [
        (self.head,   x + 10, y,      random.uniform(-200, 200), random.uniform(-500, -300)),
        (self.torso,  x + 5,  y + 18, random.uniform(-100, 100), random.uniform(-200, -100)),
        (self.arm_r,  x + 18, y + 18, random.uniform(100, 300),  random.uniform(-400, -200)),
        (self.arm_l,  x - 8,  y + 18, random.uniform(-300, -100),random.uniform(-400, -200)),
        (self.leg_r,  x + 8,  y + 36, random.uniform(50, 200),   random.uniform(-300, -100)),
        (self.leg_l,  x - 4,  y + 36, random.uniform(-200, -50), random.uniform(-300, -100)),
    ]

    for img, px, py, vx, vy in part_configs:
        self.parts_physics.append(RagdollPart(img, px, py, vx, vy))
```

```python
class RagdollPart:
    def __init__(self, img, x, y, vel_x, vel_y):
        self.img   = img
        self.x     = float(x)
        self.y     = float(y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.angle = 0.0
        self.spin  = random.uniform(-300, 300)   # degrees/sec
        self.bounced = False

    def update(self, dt):
        self.vel_y += GRAVITY * dt
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.angle += self.spin * dt

        # One bounce on ground
        if self.y >= GROUND_Y - self.img.get_height():
            self.y = GROUND_Y - self.img.get_height()
            if not self.bounced:
                self.vel_y *= -0.35   # bounce damping
                self.vel_x *= 0.6
                self.spin  *= 0.4
                self.bounced = True
            else:
                self.vel_y = 0
                self.vel_x *= 0.9
                self.spin  *= 0.9

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.img, self.angle)
        surface.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))
```

---

## 10. COMBAT SYSTEM — GUN

### Bullet Class

```python
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner_id):
        super().__init__()
        self.x         = float(x)
        self.y         = float(y)
        self.vel_x     = BULLET_SPEED * direction  # direction: 1 or -1
        self.vel_y     = 0.0                        # strictly horizontal, no arc
        self.owner_id  = owner_id                   # 1 or 2 — prevents self-damage
        self.damage    = 5
        self.alive     = True

        # Visual: 10px wide, 4px tall rectangle in yellow/white
        self.image = pygame.Surface((10, 4), pygame.SRCALPHA)
        self.image.fill((255, 230, 80))
        self.rect  = self.image.get_rect(center=(int(x), int(y)))

    def update(self, dt):
        self.x += self.vel_x * dt
        self.rect.centerx = int(self.x)

        # Destroy if outside virtual canvas
        if self.x < -50 or self.x > VIRTUAL_W + 50:
            self.kill()
            self.alive = False
```

### Firing Logic

```python
def try_shoot(self):
    """Called when shoot key is freshly pressed."""
    if self.ammo <= 0:
        return   # Cannot shoot — no ammo. No sound, no effect.

    self.ammo -= 1

    # Spawn bullet at gun-hand position
    gun_x = self.x + (PLAYER_WIDTH + 5) if self.facing == 1 else self.x - 5
    gun_y = self.y + 20   # vertical center of the torso

    bullet = Bullet(gun_x, gun_y, self.facing, self.player_id)
    self.game.bullet_group.add(bullet)

    # Trigger gun recoil animation on the arm
    self.body.trigger_gun_recoil()
```

### Ammo Display
Ammo is displayed as a number: `"AMMO: 47 / 67"` next to each health bar. When ammo = 0, display in red and show `"RELOAD!"`.

---

## 11. COMBAT SYSTEM — KNIFE

### Knife Logic

```python
KNIFE_RANGE    = 55    # pixels in front of player
KNIFE_DAMAGE   = 10
KNIFE_COOLDOWN = 0.35  # seconds between stabs (prevents spam with some feel)

def try_knife(self):
    """Called when knife key is freshly pressed."""
    if self.knife_cooldown > 0:
        return

    self.knife_cooldown = KNIFE_COOLDOWN
    self.body.trigger_knife()

    # Knife hit detection happens mid-animation, not immediately
    # Schedule hit check 100ms into the animation
    self.knife_hit_pending = True
    self.knife_hit_timer   = 0.1   # seconds until hit detection fires

def update_knife(self, opponent, particle_system, dt):
    if self.knife_cooldown > 0:
        self.knife_cooldown -= dt

    if self.knife_hit_pending:
        self.knife_hit_timer -= dt
        if self.knife_hit_timer <= 0:
            self.knife_hit_pending = False
            # Check if opponent is in range
            knife_box = self.get_knife_hitbox()
            opp_box   = opponent.get_rect()
            if knife_box.colliderect(opp_box) and opponent.alive:
                hit_x = (knife_box.centerx + opp_box.centerx) // 2
                hit_y = (knife_box.centery + opp_box.centery) // 2
                killed = opponent.take_damage(KNIFE_DAMAGE, (hit_x, hit_y))
                particle_system.spawn_blood(hit_x, hit_y)
```

---

## 12. PICKUP SYSTEM

### Health Pack

```python
class HealthPack(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.value = 30

    # No update needed — static until collected
```

### Ammo Pack

```python
class AmmoPack(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image     = image
        self.rect      = self.image.get_rect(topleft=(x, y))
        self.lifetime  = random.uniform(4.0, 5.0)  # seconds before auto-disappear

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
```

### Spawn Manager

```python
class PickupSpawnManager:
    def __init__(self, arena_platforms, barrel_positions):
        # Valid spawn X positions — between barrels and on platforms
        self.spawn_points_ground   = [300, 500, 700, 900, 1100, 1300, 1600]
        self.spawn_points_platform = []  # populated from platform list
        for plat in arena_platforms:
            self.spawn_points_platform.append(plat.rect.centerx)

        self.health_timer  = random.uniform(10.0, 15.0)
        self.ammo_timer    = random.uniform(5.0, 7.0)

    def update(self, dt, health_group, ammo_group, images):
        self.health_timer -= dt
        self.ammo_timer   -= dt

        if self.health_timer <= 0:
            self.health_timer = random.uniform(10.0, 15.0)
            x = random.choice(self.spawn_points_ground + self.spawn_points_platform)
            y = GROUND_Y - 40   # ground level — adjust for platform if on platform
            health_group.add(HealthPack(x, y, images["health_pack"]))

        if self.ammo_timer <= 0:
            self.ammo_timer = random.uniform(5.0, 7.0)
            x = random.choice(self.spawn_points_ground + self.spawn_points_platform)
            y = GROUND_Y - 40
            ammo_group.add(AmmoPack(x, y, images["ammo_box"]))
```

### Pickup Collection

```python
def check_pickups(self, health_group, ammo_group, particle_system):
    player_rect = self.get_rect()

    # Health
    hits = pygame.sprite.spritecollide(self, health_group, False)
    for pack in hits:
        if self.health < self.max_health:
            self.heal(pack.value)
            pack.kill()

    # Ammo
    hits = pygame.sprite.spritecollide(self, ammo_group, False)
    for pack in hits:
        if self.ammo < self.max_ammo:
            self.ammo = self.max_ammo
            pack.kill()
```

---

## 13. ARENA & ENVIRONMENTAL DESIGN

### Layout (Virtual Canvas: 2000 x 700 px)

```
Ground:        Y = 620 (full width, solid)

Platforms (approximate positions):
  Platform A:  X=300,  Y=430,  Width=180  (left side, low)
  Platform B:  X=700,  Y=330,  Width=200  (left-center, mid height)
  Platform C:  X=1000, Y=260,  Width=220  (center, high)
  Platform D:  X=1350, Y=340,  Width=200  (right-center, mid height)
  Platform E:  X=1600, Y=430,  Width=180  (right side, low)

Barrels (fixed, on ground):
  Barrel 1:    X=420,  Y=580   (left cluster)
  Barrel 2:    X=480,  Y=580
  Barrel 3:    X=950,  Y=580   (center)
  Barrel 4:    X=1020, Y=580
  Barrel 5:    X=1530, Y=580  (right cluster)
  Barrel 6:    X=1590, Y=580

Players spawn at:
  P1: X=150,  facing RIGHT
  P2: X=1820, facing LEFT
```

### Barrel Class

```python
class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image   # ~40x60 px
        self.rect  = self.image.get_rect(bottomleft=(x, GROUND_Y))
```

### Ground Class

```python
class Ground:
    def __init__(self, tile_image):
        self.tile  = tile_image
        self.rect  = pygame.Rect(0, GROUND_Y, VIRTUAL_W, VIRTUAL_H - GROUND_Y)

    def draw(self, surface):
        tile_w = self.tile.get_width()
        for x in range(0, VIRTUAL_W, tile_w):
            surface.blit(self.tile, (x, GROUND_Y))
```

---

## 14. DYNAMIC CAMERA / ZOOM SYSTEM

This is the most technically complex system. The game renders to a large virtual canvas and then scales it to fit the window while keeping both players centered and visible.

### Implementation

```python
# constants.py
SCREEN_W       = 1280
SCREEN_H       = 720
VIRTUAL_W      = 2000
VIRTUAL_H      = 700
ZOOM_MIN       = 0.42   # Most zoomed out — players very far apart
ZOOM_MAX       = 0.90   # Most zoomed in  — players very close together
ZOOM_SPEED     = 2.5    # How fast zoom transitions (lerp factor per second)
```

```python
class Camera:
    def __init__(self):
        self.virtual_surface = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
        self.zoom            = 0.65    # Current zoom (0..1 relative to min/max)
        self.target_zoom     = 0.65
        self.offset_x        = 0.0
        self.offset_y        = 0.0

    def update(self, p1_x, p2_x, dt):
        # Midpoint between players
        mid_x = (p1_x + p2_x) / 2.0

        # Distance drives zoom
        distance = abs(p2_x - p1_x)

        # Map distance to zoom: close=zoom in, far=zoom out
        # Normalize distance: 0 = players touching, max = 1800px apart
        norm = min(distance / 1800.0, 1.0)
        self.target_zoom = ZOOM_MAX - norm * (ZOOM_MAX - ZOOM_MIN)

        # Smooth zoom transition
        self.zoom += (self.target_zoom - self.zoom) * ZOOM_SPEED * dt
        self.zoom  = max(ZOOM_MIN, min(ZOOM_MAX, self.zoom))

        # Camera X follows midpoint, clamped so we don't show outside virtual canvas
        # Convert midpoint to screen position
        visible_w = SCREEN_W / self.zoom
        self.offset_x = mid_x - visible_w / 2
        self.offset_x = max(0, min(self.offset_x, VIRTUAL_W - visible_w))

        # Y is fixed (no vertical scrolling needed for this arena)
        self.offset_y = 0.0

    def apply(self, screen):
        """Scale virtual surface and blit to real screen."""
        # Crop the visible region from virtual surface
        visible_w = int(SCREEN_W / self.zoom)
        visible_h = int(SCREEN_H / self.zoom)

        crop_x = int(self.offset_x)
        crop_y = int(self.offset_y)

        # Clamp crop to avoid going outside virtual canvas
        crop_x = max(0, min(crop_x, VIRTUAL_W - visible_w))
        crop_y = max(0, min(crop_y, VIRTUAL_H - visible_h))

        crop_rect = pygame.Rect(crop_x, crop_y, visible_w, visible_h)
        cropped   = self.virtual_surface.subsurface(crop_rect)

        # Scale to screen
        scaled = pygame.transform.smoothscale(cropped, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))

    def get_virtual_surface(self) -> pygame.Surface:
        return self.virtual_surface
```

**All game objects are drawn to `camera.virtual_surface`, NOT the screen. Only the camera's `apply()` method draws to the actual window.**

---

## 15. PARTICLE & VFX SYSTEM

### GIF Frame Player
GIFs are pre-exported as horizontal PNG strips (all frames in one row). The code reads frame width from total image width divided by frame count.

```python
class GifPlayer:
    def __init__(self, strip_path: str, frame_count: int, fps: float = 24):
        strip = pygame.image.load(strip_path).convert_alpha()
        fw    = strip.get_width() // frame_count
        fh    = strip.get_height()
        self.frames = [
            strip.subsurface(pygame.Rect(i * fw, 0, fw, fh))
            for i in range(frame_count)
        ]
        self.fps     = fps
        self.spf     = 1.0 / fps      # seconds per frame
        self.timer   = 0.0
        self.current = 0

    def update(self, dt) -> bool:
        """Returns True when animation completes."""
        self.timer += dt
        if self.timer >= self.spf:
            self.timer -= self.spf
            self.current += 1
        return self.current >= len(self.frames)

    def get_frame(self) -> pygame.Surface:
        idx = min(self.current, len(self.frames) - 1)
        return self.frames[idx]
```

### Blood Spark Instance

```python
class BloodSpark:
    def __init__(self, x, y, gif_strip_path, frame_count):
        self.x      = x
        self.y      = y
        self.player = GifPlayer(gif_strip_path, frame_count, fps=20)
        self.done   = False

    def update(self, dt):
        self.done = self.player.update(dt)

    def draw(self, surface):
        if not self.done:
            frame = self.player.get_frame()
            # Center the spark on the hit point, small scale (~40x40)
            scaled = pygame.transform.scale(frame, (40, 40))
            surface.blit(scaled, (self.x - 20, self.y - 20))
```

### Particle System Manager

```python
class ParticleSystem:
    def __init__(self, blood_strip_path, blood_frames):
        self.blood_strip_path = blood_strip_path
        self.blood_frames     = blood_frames
        self.active_sparks    = []

    def spawn_blood(self, x, y):
        self.active_sparks.append(BloodSpark(x, y, self.blood_strip_path, self.blood_frames))

    def update(self, dt):
        for spark in self.active_sparks[:]:
            spark.update(dt)
            if spark.done:
                self.active_sparks.remove(spark)

    def draw(self, surface):
        for spark in self.active_sparks:
            spark.draw(surface)
```

---

## 16. K.O. & ROUND RESET SYSTEM

### K.O. Screen

```python
class KOScreen:
    def __init__(self, ko_strip_path, ko_frames):
        self.gif      = GifPlayer(ko_strip_path, ko_frames, fps=15)
        self.timer    = 0.0
        self.duration = 3.0   # seconds before auto-reset
        self.done     = False

        # Pulse scaling effect
        self.scale    = 1.0
        self.scale_dir = 1

    def update(self, dt):
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
        frame  = self.gif.get_frame()
        size   = int(400 * self.scale)
        scaled = pygame.transform.smoothscale(frame, (size, size))
        x = SCREEN_W // 2 - size // 2
        y = SCREEN_H // 2 - size // 2
        screen.blit(scaled, (x, y))
```

### Reset Game Function

```python
def reset_game(self):
    """Full match reset. Called by Start New, and by K.O. auto-restart."""
    # Reset Player 1
    self.p1.x        = 150.0
    self.p1.y        = float(GROUND_Y - PLAYER_HEIGHT)
    self.p1.vel_x    = 0.0
    self.p1.vel_y    = 0.0
    self.p1.health   = 100
    self.p1.ammo     = 67
    self.p1.alive    = True
    self.p1.state    = "IDLE"
    self.p1.facing   = 1
    self.p1.body     = SkeletalBody(1, self.assets)
    self.p1.knife_cooldown = 0.0
    self.p1.shoot_held_last = False

    # Reset Player 2
    self.p2.x        = 1820.0
    self.p2.y        = float(GROUND_Y - PLAYER_HEIGHT)
    self.p2.vel_x    = 0.0
    self.p2.vel_y    = 0.0
    self.p2.health   = 100
    self.p2.ammo     = 67
    self.p2.alive    = True
    self.p2.state    = "IDLE"
    self.p2.facing   = -1
    self.p2.body     = SkeletalBody(2, self.assets)
    self.p2.knife_cooldown = 0.0
    self.p2.shoot_held_last = False

    # Clear all active projectiles and pickups
    self.bullet_group.empty()
    self.health_group.empty()
    self.ammo_group.empty()

    # Reset particle system
    self.particles.active_sparks.clear()

    # Reset spawn timers
    self.spawn_manager.health_timer = random.uniform(10.0, 15.0)
    self.spawn_manager.ammo_timer   = random.uniform(5.0, 7.0)

    # Reset camera zoom to default
    self.camera.zoom        = 0.65
    self.camera.target_zoom = 0.65
```

---

## 17. UI / HUD SYSTEM

All HUD elements are drawn **directly to the real screen** (not the virtual surface), so they are always at fixed screen positions regardless of zoom.

```python
class HUD:
    def __init__(self, font):
        self.font = font

    def draw(self, screen, p1, p2):
        # === PLAYER 1 — top left ===
        # Background bar
        pygame.draw.rect(screen, (60, 60, 60),  pygame.Rect(20, 18, 304, 28), border_radius=6)
        # Health fill
        fill_w = int((p1.health / 100) * 300)
        color  = self._health_color(p1.health)
        pygame.draw.rect(screen, color, pygame.Rect(22, 20, fill_w, 24), border_radius=5)
        # Label
        label = self.font.render(f"P1  {p1.health}/100", True, (255,255,255))
        screen.blit(label, (26, 22))
        # Ammo
        ammo_text  = f"AMMO: {p1.ammo}/67"
        ammo_color = (255, 80, 80) if p1.ammo == 0 else (220, 220, 220)
        ammo_surf  = self.font.render(ammo_text, True, ammo_color)
        screen.blit(ammo_surf, (26, 52))

        # === PLAYER 2 — top right ===
        bar_x = SCREEN_W - 324
        pygame.draw.rect(screen, (60, 60, 60),  pygame.Rect(bar_x, 18, 304, 28), border_radius=6)
        fill_w = int((p2.health / 100) * 300)
        color  = self._health_color(p2.health)
        # Draw from right side
        pygame.draw.rect(screen, color,
                         pygame.Rect(bar_x + 300 - fill_w, 20, fill_w, 24), border_radius=5)
        label = self.font.render(f"{p2.health}/100  P2", True, (255,255,255))
        screen.blit(label, (bar_x + 300 - label.get_width() - 4, 22))
        ammo_text  = f"67/{p2.ammo} :OMMA"
        ammo_color = (255, 80, 80) if p2.ammo == 0 else (220, 220, 220)
        ammo_surf  = self.font.render(f"AMMO: {p2.ammo}/67", True, ammo_color)
        screen.blit(ammo_surf, (bar_x + 300 - ammo_surf.get_width() - 4, 52))

        # Pause button — top center
        pause_label = self.font.render("|| PAUSE", True, (200,200,200))
        px = SCREEN_W // 2 - pause_label.get_width() // 2
        screen.blit(pause_label, (px, 20))

    def _health_color(self, hp):
        if hp > 60: return (60, 200, 60)    # Green
        if hp > 30: return (230, 180, 20)   # Yellow
        return (220, 50, 50)                 # Red
```

---

## 18. MENU & PAUSE SYSTEM

### Main Menu

```python
class MainMenu:
    def __init__(self, bg_image, font_large, font_medium):
        self.bg          = bg_image
        self.font_large  = font_large
        self.font_medium = font_medium

        # Play button rect (centered on screen)
        self.play_rect = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H//2 - 40, 200, 80)

    def handle_event(self, event) -> str:
        """Returns 'play' if play was clicked, else None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_rect.collidepoint(event.pos):
                return "play"
        return None

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        # Title
        title = self.font_large.render("DUEL-STRIKE", True, (255, 220, 50))
        screen.blit(title, title.get_rect(centerx=SCREEN_W//2, y=180))

        # Play button
        mouse_pos = pygame.mouse.get_pos()
        hover = self.play_rect.collidepoint(mouse_pos)
        btn_color = (80, 200, 80) if hover else (50, 150, 50)
        pygame.draw.rect(screen, btn_color, self.play_rect, border_radius=12)
        pygame.draw.rect(screen, (255,255,255), self.play_rect, 3, border_radius=12)
        play_text = self.font_medium.render("PLAY", True, (255,255,255))
        screen.blit(play_text, play_text.get_rect(center=self.play_rect.center))
```

### Pause Menu

```python
class PauseMenu:
    def __init__(self, font):
        self.font = font
        w, h  = 340, 320
        self.panel_rect   = pygame.Rect(SCREEN_W//2 - w//2, SCREEN_H//2 - h//2, w, h)

        # Buttons stacked vertically, centered
        bw, bh  = 240, 56
        cx      = SCREEN_W // 2 - bw // 2
        base_y  = self.panel_rect.y + 80
        gap     = 68
        self.btn_continue  = pygame.Rect(cx, base_y,          bw, bh)
        self.btn_new       = pygame.Rect(cx, base_y + gap,     bw, bh)
        self.btn_exit      = pygame.Rect(cx, base_y + gap * 2, bw, bh)

    def handle_event(self, event) -> str:
        """Returns 'continue', 'new', 'exit', or None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_continue.collidepoint(event.pos): return "continue"
            if self.btn_new.collidepoint(event.pos):      return "new"
            if self.btn_exit.collidepoint(event.pos):     return "exit"
        # Also support Escape to resume
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "continue"
        return None

    def draw(self, screen):
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
            (self.btn_new,      "Start New"),
            (self.btn_exit,     "Exit"),
        ]:
            hover = rect.collidepoint(mouse)
            color = (70, 130, 200) if hover else (45, 90, 150)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 220), rect, 2, border_radius=10)
            text = self.font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=rect.center))
```

### Pause Button (In-Game)
The pause icon is a clickable area at the top of the real screen. It is detected via mouse click in the main event loop:

```python
PAUSE_BTN_RECT = pygame.Rect(SCREEN_W//2 - 50, 10, 100, 36)

# In event loop:
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    if PAUSE_BTN_RECT.collidepoint(event.pos) and self.state == "STATE_PLAYING":
        self.state = "STATE_PAUSED"
# Also map Escape key:
if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    if self.state == "STATE_PLAYING":
        self.state = "STATE_PAUSED"
```

---

## 19. COLLISION DETECTION STRATEGY

| Interaction | Method | Notes |
|---|---|---|
| Bullet vs Player | `pygame.Rect.colliderect()` | Fast, frame-accurate |
| Bullet vs Barrel | `pygame.Rect.colliderect()` | Bullet is destroyed |
| Bullet vs Platform | `pygame.Rect.colliderect()` | Bullet passes through platforms |
| Player vs Ground | Y-position comparison | `player.y + height >= GROUND_Y` |
| Player vs Platform | `pygame.Rect.colliderect()` + direction check | One-way platforms |
| Player vs Barrel (sides) | `pygame.Rect.colliderect()` | Player cannot walk through barrels |
| Knife vs Player | `pygame.Rect.colliderect()` on knife hitbox | Only active during stab window |
| Player vs Health Pack | `pygame.sprite.spritecollide()` | Auto-pickup |
| Player vs Ammo Pack | `pygame.sprite.spritecollide()` | Auto-pickup if ammo < max |

### Player vs Barrel (Solid Collision)

```python
def resolve_barrel_collision(player, barrels):
    player_rect = player.get_rect()
    for barrel in barrels:
        if player_rect.colliderect(barrel.rect):
            # Push player out horizontally only
            overlap_left  = player_rect.right - barrel.rect.left
            overlap_right = barrel.rect.right - player_rect.left

            if overlap_left < overlap_right:
                player.x -= overlap_left
                player.vel_x = 0
            else:
                player.x += overlap_right
                player.vel_x = 0
```

### Bullet Collision Check (Called Every Frame)

```python
def check_bullet_collisions(self):
    for bullet in list(self.bullet_group):
        # vs Barrels
        for barrel in self.barrels:
            if bullet.rect.colliderect(barrel.rect):
                bullet.kill()
                break
        if not bullet.alive:
            continue

        # vs Players (cannot hit own player)
        for player in [self.p1, self.p2]:
            if player.player_id == bullet.owner_id:
                continue
            if not player.alive:
                continue
            if bullet.rect.colliderect(player.get_rect()):
                killed = player.take_damage(bullet.damage, bullet.rect.center)
                self.particles.spawn_blood(bullet.rect.centerx, bullet.rect.centery)
                bullet.kill()
                if killed:
                    self._trigger_ko(player.player_id)
                break
```

---

## 20. FULL CLASS ARCHITECTURE

```
main.py
└── Game                        ← Master controller
    ├── Camera                  ← Virtual surface + zoom
    ├── MainMenu                ← Home screen
    ├── PauseMenu               ← Pause overlay
    ├── KOScreen                ← End-of-round animation
    ├── HUD                     ← Health bars + ammo display
    ├── Player (×2)             ← p1 and p2
    │   ├── SkeletalBody        ← 6 body part surfaces + animation
    │   │   └── RagdollPart (×6, on death)
    │   └── controls: dict
    ├── Bullet (sprite group)   ← All active bullets
    ├── Barrel (list)           ← Static arena objects
    ├── Platform (list)         ← Jumpable platforms
    ├── Ground                  ← Ground floor renderer
    ├── HealthPack (group)      ← Active health drops
    ├── AmmoPack (group)        ← Active ammo drops
    ├── PickupSpawnManager      ← Timer-based spawning
    └── ParticleSystem          ← Blood sparks, manages GifPlayer instances
        └── BloodSpark (list)
            └── GifPlayer       ← Frame strip animator
```

---

## 21. RENDERING PIPELINE

**Strict draw order every frame:**

```
1. camera.virtual_surface.fill(SKY_COLOR)        ← Clear virtual canvas

2. Draw background (parallax or static art)      ← On virtual canvas

3. Draw Ground tiles                              ← On virtual canvas

4. Draw Platforms                                 ← On virtual canvas

5. Draw Barrels                                   ← On virtual canvas

6. Draw HealthPacks and AmmoPacks                 ← On virtual canvas

7. Draw Bullets (all active)                      ← On virtual canvas

8. Draw Player 1 body                             ← On virtual canvas

9. Draw Player 2 body                             ← On virtual canvas

10. Draw Particle effects (blood sparks)          ← On virtual canvas

11. camera.apply(screen)                          ← Scale virtual → real screen

    ─── Everything below is drawn on real screen (not affected by zoom) ───

12. Draw HUD (health bars, ammo counters)         ← On real screen

13. [If PAUSED] Draw PauseMenu overlay            ← On real screen

14. [If KO] Draw KOScreen animation              ← On real screen

15. pygame.display.flip()                         ← Commit frame to monitor
```

---

## 22. PERFORMANCE & STABILITY GUIDELINES

### 60 FPS Target

```python
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000.0   # Delta time in seconds
    dt = min(dt, 0.05)             # CAP dt at 50ms — prevents physics explosion on lag spikes
```

The `min(dt, 0.05)` cap is critical. Without it, a single frame spike can send players through floors or launch them off screen.

### Sprite Group Management
- Use `pygame.sprite.Group` for bullets, health packs, ammo packs.
- Call `.empty()` on all groups in `reset_game()`.
- Do not iterate and modify a list simultaneously — use `list(group)` when iterating while potentially removing.

### Memory Leaks — Prevention
- `BloodSpark.done == True` → remove from list immediately in same frame.
- `RagdollPart` — once all parts stop moving (vel near zero, on ground), stop updating them (add `self.settled = True` flag).
- Bullet sprites call `self.kill()` on hit or out-of-bounds — this removes them from all groups automatically.

### Surface Conversion
All images must be converted at load time for fast blitting:

```python
img = pygame.image.load(path).convert_alpha()   # For images with transparency
img = pygame.image.load(path).convert()          # For images without transparency
```

### GIF Strip Loading — Only Once
Load all GIF strips once at startup and pass references. Never reload from disk during gameplay.

---

## 23. COMPLETE MAIN GAME LOOP

```python
# main.py
import pygame
from src.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Duel-Strike")

    game = Game(screen)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        # === EVENT HANDLING ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        # === UPDATE ===
        game.update(dt)

        # === DRAW ===
        game.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
```

```python
# src/game.py — Game.update() skeleton
def update(self, dt):
    if self.state != "STATE_PLAYING":
        if self.state == "STATE_KO":
            self.ko_screen.update(dt)
            if self.ko_screen.done:
                self.reset_game()
                self.state = "STATE_PLAYING"
        return

    keys = pygame.key.get_pressed()

    # Update players
    for player in [self.p1, self.p2]:
        if player.alive:
            player.handle_input(keys, dt)
            player.apply_physics(dt)
            player.check_platform_collision(self.platforms)
            player.check_barrel_collision(self.barrels)
            player.check_pickups(self.health_group, self.ammo_group)

    # Update knife combat
    if self.p1.alive: self.p1.update_knife(self.p2, self.particles, dt)
    if self.p2.alive: self.p2.update_knife(self.p1, self.particles, dt)

    # Update bullets
    self.bullet_group.update(dt)
    self.check_bullet_collisions()

    # Update pickups
    self.health_group.update(dt)
    self.ammo_group.update(dt)
    self.spawn_manager.update(dt, self.health_group, self.ammo_group, self.pickup_images)

    # Update particles
    self.particles.update(dt)

    # Update skeletal bodies
    for player in [self.p1, self.p2]:
        player.body.update(player.state, player.vel_x, player.on_ground, dt)

    # Update camera
    self.camera.update(self.p1.x, self.p2.x, dt)
```

---

## 24. KNOWN EDGE CASES & BUG PREVENTION

### 1. Platform Fall-Through
**Problem:** High-speed downward movement can skip past thin platforms in one frame.
**Fix:** Check previous frame Y position to determine if player "crossed" the platform top.
```python
prev_bottom = self.y - self.vel_y * dt
if prev_bottom <= plat.rect.top and self.y + self.height >= plat.rect.top:
    # landed this frame
```

### 2. Both Players Die Simultaneously
**Problem:** If a bullet kills P1 while P2 also has 0 HP, two K.O. events fire.
**Fix:** Add a `self.ko_triggered = False` flag. Once set, ignore further death events until reset.
```python
if not self.ko_triggered:
    self.ko_triggered = True
    self._trigger_ko(loser_id)
```

### 3. Ammo Goes Negative
**Problem:** Rapid fire near 0 ammo might decrement twice in one frame due to frame timing.
**Fix:** Always `max(0, self.ammo - 1)` instead of `self.ammo -= 1`. Check `ammo > 0` BEFORE decrementing.

### 4. Health Exceeds 100
**Problem:** Multiple health packs spawned at same location; player collides with both in one frame.
**Fix:** `self.health = min(self.max_health, self.health + amount)` — already capped. Also, limit to 1 health pack on screen at a time if desired.

### 5. Camera Crop Outside Virtual Canvas
**Problem:** When players are near the edge of the map, the camera crop rect extends outside the virtual surface, causing a crash.
**Fix:** Always clamp crop_x and crop_y before creating subsurface:
```python
crop_x = max(0, min(crop_x, VIRTUAL_W - visible_w))
```

### 6. Knife Hits Dead Player
**Problem:** If a player dies from a bullet the same frame a knife swing connects, double-death logic fires.
**Fix:** `if opponent.alive:` check before applying knife damage.

### 7. Ragdoll Parts Going Off-Screen
**Problem:** Scatter velocities can send parts outside the virtual canvas.
**Fix:** Clamp ragdoll part X positions to `[0, VIRTUAL_W]`.

### 8. pygame.Surface.subsurface Out of Range
**Problem:** If visible_w > VIRTUAL_W (zoom too far in on small gap), subsurface crashes.
**Fix:** Ensure `visible_w = min(VIRTUAL_W, int(SCREEN_W / self.zoom))`.

### 9. Input Ghosting
**Problem:** Some cheaper keyboards block certain simultaneous key combinations.
**Fix:** The chosen key layout (WASD + CV for P1, IJKL + BN for P2) is specifically selected to minimize keyboard matrix conflicts. This cannot be fully solved in software — it is a hardware limitation. Document this for users.

### 10. dt Spike on Window Minimize/Restore
**Problem:** When the window is minimized, `clock.tick()` accumulates large dt on restore, causing a physics explosion.
**Fix:** `dt = min(dt, 0.05)` cap in the main loop (already specified above).

---

## CONSTANTS REFERENCE SHEET

```python
# src/constants.py — COMPLETE

import pygame

# Screen
SCREEN_W        = 1280
SCREEN_H        = 720

# Virtual Canvas
VIRTUAL_W       = 2000
VIRTUAL_H       = 700

# Players
PLAYER_WIDTH    = 48
PLAYER_HEIGHT   = 72
PLAYER_SPEED    = 260
JUMP_FORCE      = 620
FAST_FALL_SPEED = 700
MAX_FALL_SPEED  = 900
GROUND_FRICTION = 0.82
GROUND_Y        = 630

# Combat
BULLET_SPEED    = 950
BULLET_DAMAGE   = 5
MAX_AMMO        = 67
KNIFE_DAMAGE    = 10
KNIFE_RANGE     = 55
KNIFE_COOLDOWN  = 0.35

# Physics
GRAVITY         = 1800

# Camera
ZOOM_MIN        = 0.42
ZOOM_MAX        = 0.90
ZOOM_SPEED      = 2.5

# Pickups
HEALTH_PACK_VALUE    = 30
HEALTH_SPAWN_MIN     = 10.0
HEALTH_SPAWN_MAX     = 15.0
AMMO_SPAWN_MIN       = 5.0
AMMO_SPAWN_MAX       = 7.0
AMMO_PACK_LIFETIME_MIN = 4.0
AMMO_PACK_LIFETIME_MAX = 5.0

# KO
KO_DISPLAY_DURATION  = 3.0

# Colors
SKY_COLOR       = (100, 140, 200)
GROUND_COLOR    = (80, 60, 40)
P1_COLOR        = (60, 120, 220)
P2_COLOR        = (220, 60, 60)
```

---

*End of PRD — Duel-Strike v1.0*
*This document is the single source of truth for all game systems. Implement each section in order. All class names, constant names, and method signatures defined here must be used exactly as written to ensure compatibility across files.*
