# src/player.py — Player character: movement, combat, weapons, collision, and death/respawn.

import pygame
from src.physics import PhysicsObject
from src.animation import SkeletalBody
from src.bullet import Bullet, ShotgunPellet, Rocket
from src.constants import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, JUMP_FORCE, FAST_FALL_SPEED,
    GROUND_Y, GROUND_LEFT, GROUND_RIGHT, CLIFF_DEATH_Y,
    KNIFE_RANGE, KNIFE_DAMAGE, KNIFE_COOLDOWN, MAX_AMMO,
    DASH_SPEED, DASH_DURATION, DASH_COOLDOWN,
    HIT_STUN_DURATION, KNOCKBACK_FORCE,
    SHOTGUN_AMMO, BAZOOKA_COOLDOWN, BAZOOKA_AMMO,
    BARREL_EDGE_LEFT, BARREL_EDGE_RIGHT,
    BOX_EDGE_LEFT, BOX_EDGE_RIGHT,
    HEAD_SIZE_BASE
)


class Player(PhysicsObject, pygame.sprite.Sprite):
    """A playable character. Handles keyboard/gamepad input, shooting, melee,
    dashing, weapon pickups, collision with platforms/obstacles, and death/respawn.
    Inherits physics (gravity, ground collision) from PhysicsObject."""
    
    def __init__(self, player_id: int, start_x: int, controls: dict, assets: dict):
        PhysicsObject.__init__(self, start_x, GROUND_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.sprite.Sprite.__init__(self)
        
        # Identity
        self.player_id = player_id
        self.controls = controls
        self.joystick = None
        
        # Position already set by PhysicsObject
        self.facing = 1 if player_id == 1 else -1
        
        # Add rect as actual attribute (not property) for pygame.sprite collision detection
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        # Stats
        self.health = 100
        self.max_health = 100
        self.ammo = 67
        self.max_ammo = MAX_AMMO
        self.alive = True
        
        # State
        self.state = "IDLE"
        
        # Input tracking (edge detection for shoot/knife)
        self.shoot_held_last = False
        self.knife_held_last = False
        
        # Combat cooldowns
        self.knife_cooldown = 0.0
        self.knife_active = False
        self.knife_anim_timer = 0.0
        self.knife_hit_pending = False
        self.knife_hit_timer = 0.0
        
        # Hit Stun
        self.hit_stun_timer = 0.0
        
        # Audio
        self.footstep_timer = 0.0

        # Dash state
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.is_dashing = False
        self.dash_held_last = False

        # Weapon states
        self.has_shotgun = False
        self.shotgun_ammo = 0
        self.shotgun_cooldown = 0.0
        
        self.has_bazooka = False
        self.bazooka_ammo = 0
        self.bazooka_cooldown = 0.0
        
        # Skeletal body
        self.body = SkeletalBody(player_id, assets)
        
        # Head-streak / respawn state
        self.start_x = start_x
        self.head_streak = 0
        self.head_scale = HEAD_SIZE_BASE
        self.is_invulnerable = False
        self.invuln_timer = 0.0
        self.respawn_timer = -1.0   # <0 means not waiting to respawn
        self.materialize_alpha = 255
        self._materialize_timer = 0.0
        
        # Reference to game (will be set by game.py)
        self.game = None
        self.audio_manager = None
    
    def update_rect(self):
        """Update rect to match current position."""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def is_action_pressed(self, action: str, keys) -> bool:
        """Check if an action key is pressed on either keyboard or gamepad."""
        if action not in self.controls:
            return False
            
        pressed = keys[self.controls[action]]
        if pressed:
            return True
            
        if self.joystick:
            j = self.joystick
            try:
                if action == "left":
                    hat = j.get_hat(0) if j.get_numhats() > 0 else (0, 0)
                    if hat[0] == -1: return True
                    if j.get_numaxes() > 0 and j.get_axis(0) < -0.5: return True
                elif action == "right":
                    hat = j.get_hat(0) if j.get_numhats() > 0 else (0, 0)
                    if hat[0] == 1: return True
                    if j.get_numaxes() > 0 and j.get_axis(0) > 0.5: return True
                elif action == "crouch":
                    hat = j.get_hat(0) if j.get_numhats() > 0 else (0, 0)
                    if hat[1] == -1: return True
                    if j.get_numaxes() > 1 and j.get_axis(1) > 0.5: return True
                elif action == "jump":
                    # L-Stick Up / R2 (Axis 1 Neg / Axis 5 / Button)
                    hat = j.get_hat(0) if j.get_numhats() > 0 else (0, 0)
                    if hat[1] == 1: return True
                    if j.get_numaxes() > 1 and j.get_axis(1) < -0.5: return True
                    # Many controllers map R2 as axis 5, and some as axis 4/2
                    if j.get_numaxes() > 5 and j.get_axis(5) > 0.1: return True
                elif action == "shoot":
                    # R1 (Button 5)
                    if j.get_numbuttons() > 5 and j.get_button(5): return True
                elif action == "dash":
                    # L2 (Axis 4) / A/Cross (Button 0)
                    if j.get_numaxes() > 4 and j.get_axis(4) > 0.1: return True
                    if j.get_numbuttons() > 0 and j.get_button(0): return True
                elif action == "knife":
                    # B/Circle (Button 1)
                    if j.get_numbuttons() > 1 and j.get_button(1): return True
            except pygame.error:
                pass
        return False

    def handle_input(self, keys, dt):
        """Read all input and update movement, combat, and dash state for this frame."""
        if not self.alive:
            return
        
        # Cooldowns
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
            
        if self.hit_stun_timer > 0:
            self.hit_stun_timer -= dt
            # Still apply dash physics if dashing, but can't change direction while stunned
            if self.is_dashing:
                self.dash_timer -= dt
                if self.dash_timer <= 0:
                    self.is_dashing = False
            self.apply_friction(moving=False)
            self.update_rect()
            return
            
        ctrl = self.controls
        moving = False
        
        # Handle Dash
        is_dash_pressed = self.is_action_pressed("dash", keys)
        if is_dash_pressed and not self.dash_held_last and self.dash_cooldown <= 0:
            self.is_dashing = True
            self.dash_timer = DASH_DURATION
            self.dash_cooldown = DASH_COOLDOWN
            if self.audio_manager:
                self.audio_manager.play_sound("dash")
        self.dash_held_last = is_dash_pressed

        if self.is_dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
            else:
                self.vel_x = DASH_SPEED * self.facing
                moving = True
                
                # High-performance dash dust purely using primitive fast particles
                if self.game and hasattr(self.game, 'particles') and getattr(self, '_dust_timer', 0) <= 0:
                    dust_x = self.x + (0 if self.facing == 1 else PLAYER_WIDTH)
                    dust_y = self.y + PLAYER_HEIGHT - 10
                    self.game.particles.spawn_dash_dust(dust_x, dust_y, self.facing)
                    self._dust_timer = 0.05
                self._dust_timer = getattr(self, '_dust_timer', 0) - dt

        if not self.is_dashing:
            # Horizontal movement
            if self.is_action_pressed("left", keys):
                self.vel_x = -PLAYER_SPEED
                self.facing = -1
                moving = True
                if self.on_ground:
                    self.state = "WALKING"
            elif self.is_action_pressed("right", keys):
                self.vel_x = PLAYER_SPEED
                self.facing = 1
                moving = True
                if self.on_ground:
                    self.state = "WALKING"
            else:
                self.vel_x = 0
                if self.on_ground and self.state == "WALKING":
                    self.state = "IDLE"
                    
            if self.state == "WALKING" and self.on_ground:
                self.footstep_timer -= dt
                if self.footstep_timer <= 0:
                    if self.audio_manager:
                        self.audio_manager.play_sound("footstep")
                    self.footstep_timer = 0.35
            else:
                self.footstep_timer = 0.0
        
        # Jump — only when on ground and not dashing
        if self.is_action_pressed("jump", keys) and self.on_ground and not self.is_dashing:
            self.vel_y = -JUMP_FORCE
            self.on_ground = False
            self.state = "JUMPING"
            if self.audio_manager:
                self.audio_manager.play_sound("jump")
        
        # Crouch / Fast Fall
        if self.is_action_pressed("crouch", keys) and not self.is_dashing:
            if self.on_ground:
                self.state = "CROUCHING"
            else:
                self.vel_y = FAST_FALL_SPEED
        
        # Shoot — detect NEW press this frame (not held)
        if self.is_action_pressed("shoot", keys) and not self.shoot_held_last:
            if self.has_bazooka and self.bazooka_ammo > 0:
                self.try_bazooka()
            elif self.has_shotgun and self.shotgun_ammo > 0:
                self.try_shotgun()
            else:
                self.try_shoot()
        self.shoot_held_last = self.is_action_pressed("shoot", keys)
        
        # Knife — detect NEW press this frame
        if self.is_action_pressed("knife", keys) and not self.knife_held_last:
            self.try_knife()
        self.knife_held_last = self.is_action_pressed("knife", keys)
        
        # Apply friction
        self.apply_friction(moving)
        
        # Update rect after all movement
        self.update_rect()
    
    def try_shoot(self):
        """Fire a pistol bullet in the facing direction (or aim direction if aiming)."""
        if self.ammo <= 0:
            return
        
        # Bug fix #3: Check ammo > 0 BEFORE decrementing
        self.ammo = max(0, self.ammo - 1)
        
        if getattr(self, 'is_aiming', False):
            cx = self.x + PLAYER_WIDTH / 2
            cy = self.y + PLAYER_HEIGHT / 2 - 4
            flash_x = cx + self.aim_x * 24
            flash_y = cy + self.aim_y * 24
            gun_x = cx + self.aim_x * 16
            gun_y = cy + self.aim_y * 16
        else:
            if hasattr(self.body, 'muzzle_x') and self.body.muzzle_x != 0:
                flash_x, flash_y = self.body.muzzle_x, self.body.muzzle_y
            else:
                flash_x = self.x + (PLAYER_WIDTH + 8) if self.facing == 1 else self.x - 8
                flash_y = self.y + 16

            gun_x = self.x + (PLAYER_WIDTH + 8) if self.facing == 1 else self.x - 8
            gun_y = self.y + 16
        
        # Import here to avoid circular dependency
        bullet = Bullet(gun_x, gun_y, self.facing, self.player_id, self.aim_x if getattr(self, 'is_aiming', False) else None, self.aim_y if getattr(self, 'is_aiming', False) else None)
        if self.game:
            self.game.bullet_group.add(bullet)
            if hasattr(self.game, 'camera'):
                self.game.camera.add_shake(2.0, 0.1)
            if hasattr(self.game, 'particles'):
                self.game.particles.spawn_muzzle_flash(flash_x, flash_y, self.facing, size=0.7)
                self.game.particles.spawn_sparks(flash_x, flash_y)
        
        # Trigger gun recoil animation
        self.body.trigger_gun_recoil("pistol")
        if self.audio_manager:
            self.audio_manager.play_sound("shoot")
    
    def try_knife(self):
        """Start a melee attack. Damage check happens 100ms later (mid-swing)."""
        if self.knife_cooldown > 0:
            return
        
        self.knife_cooldown = KNIFE_COOLDOWN
        self.body.trigger_knife()
        
        # Schedule hit check 100ms into the animation
        self.knife_hit_pending = True
        self.knife_hit_timer = 0.1
        if self.audio_manager:
            self.audio_manager.play_sound("knife_swoosh")
    
    def try_shotgun(self):
        """Fire shotgun: spawns multiple pellets in a spread pattern. Auto-drops when ammo runs out."""
        from src.constants import (
            SHOTGUN_PELLETS, SHOTGUN_SPREAD_DEG,
            SHOTGUN_COOLDOWN
        )

        if self.shotgun_cooldown > 0 or self.shotgun_ammo <= 0:
            return

        self.shotgun_ammo -= 1
        self.shotgun_cooldown = SHOTGUN_COOLDOWN

        # If shotgun ammo hits 0, drop the shotgun
        if self.shotgun_ammo <= 0:
            self.has_shotgun = False
            self.body.current_weapon = "pistol"

        # Spread: evenly distribute pellets across ±SHOTGUN_SPREAD_DEG
        if getattr(self, 'is_aiming', False):
            cx = self.x + PLAYER_WIDTH / 2
            cy = self.y + PLAYER_HEIGHT / 2 - 4
            gun_x = cx + self.aim_x * 16
            gun_y = cy + self.aim_y * 16
            flash_x_ov = cx + self.aim_x * 30
            flash_y_ov = cy + self.aim_y * 30
        else:
            gun_x = (self.x + PLAYER_WIDTH + 8
                     if self.facing == 1 else self.x - 8)
            gun_y = self.y + 16
            flash_x_ov = None
            flash_y_ov = None

        if SHOTGUN_PELLETS == 1:
            angles = [0]
        else:
            step = (SHOTGUN_SPREAD_DEG * 2) / (SHOTGUN_PELLETS - 1)
            angles = [-SHOTGUN_SPREAD_DEG + i * step
                      for i in range(SHOTGUN_PELLETS)]

        import math
        base_angle = None
        if getattr(self, 'is_aiming', False):
            base_angle = math.degrees(math.atan2(-self.aim_y, self.aim_x))
            
        for angle in angles:
            pellet = ShotgunPellet(
                gun_x, gun_y, self.facing, angle, self.player_id, base_angle)
            if self.game:
                self.game.bullet_group.add(pellet)

        # Particle coordinates (track tip of barrel perfectly)
        if getattr(self, 'is_aiming', False) and flash_x_ov is not None:
            flash_x, flash_y = flash_x_ov, flash_y_ov
        elif hasattr(self.body, 'muzzle_x') and self.body.muzzle_x != 0:
            flash_x, flash_y = self.body.muzzle_x, self.body.muzzle_y
        else:
            flash_x, flash_y = gun_x, gun_y

        # Trigger gun recoil animation — stronger kick
        self.body.trigger_gun_recoil("shotgun")
        if self.game and hasattr(self.game, 'camera'):
            self.game.camera.add_shake(7.0, 0.2)
            if hasattr(self.game, 'particles'):
                self.game.particles.spawn_muzzle_flash(flash_x, flash_y, self.facing, size=1.5)
                self.game.particles.spawn_sparks(flash_x, flash_y)
        if self.audio_manager:
            self.audio_manager.play_sound("shotgun_fire")

    def try_bazooka(self):
        """Fire a rocket. Biggest screen shake, strongest recoil. Auto-drops when ammo runs out."""

        if self.bazooka_cooldown > 0 or self.bazooka_ammo <= 0:
            return

        self.bazooka_ammo -= 1
        self.bazooka_cooldown = BAZOOKA_COOLDOWN

        if self.bazooka_ammo <= 0:
            self.has_bazooka = False
            self.body.current_weapon = "pistol"

        if getattr(self, 'is_aiming', False):
            cx = self.x + PLAYER_WIDTH / 2
            cy = self.y + 12
            gun_x = cx + self.aim_x * 16
            gun_y = cy + self.aim_y * 16
            flash_x_ov = cx + self.aim_x * 40
            flash_y_ov = cy + self.aim_y * 40
        else:
            gun_x = (self.x + PLAYER_WIDTH + 8
                     if self.facing == 1 else self.x - 8)
            gun_y = self.y + 12  # Bazooka slightly higher onto shoulder/head level
            flash_x_ov = None
            flash_y_ov = None

        rocket = Rocket(gun_x, gun_y, self.facing, self.player_id, self.aim_x if getattr(self, 'is_aiming', False) else None, self.aim_y if getattr(self, 'is_aiming', False) else None)
        
        if getattr(self, 'is_aiming', False) and flash_x_ov is not None:
            flash_x, flash_y = flash_x_ov, flash_y_ov
        elif hasattr(self.body, 'muzzle_x') and self.body.muzzle_x != 0:
            flash_x, flash_y = self.body.muzzle_x, self.body.muzzle_y
        else:
            flash_x, flash_y = gun_x, gun_y

        if self.game:
            self.game.bullet_group.add(rocket)
            if hasattr(self.game, 'camera'):
                self.game.camera.add_shake(12.0, 0.3)
            if hasattr(self.game, 'particles'):
                self.game.particles.spawn_muzzle_flash(flash_x, flash_y, self.facing, size=2.0)
                self.game.particles.spawn_sparks(flash_x, flash_y)

        self.body.trigger_gun_recoil("bazooka")
        if self.audio_manager:
            self.audio_manager.play_sound("bazooka_fire")

    def update_knife(self, opponent, particle_system, dt):
        """Tick weapon cooldowns and check if a knife swing connects with the opponent."""
        if self.knife_cooldown > 0:
            self.knife_cooldown -= dt
        if self.shotgun_cooldown > 0:
            self.shotgun_cooldown -= dt
        if self.bazooka_cooldown > 0:
            self.bazooka_cooldown -= dt
        
        if self.knife_hit_pending:
            self.knife_hit_timer -= dt
            if self.knife_hit_timer <= 0:
                self.knife_hit_pending = False
                # Check if opponent is in range (Bug fix #6: check alive)
                if opponent.alive:
                    knife_box = self.get_knife_hitbox()
                    opp_box = opponent.get_rect()
                    if knife_box.colliderect(opp_box):
                        hit_x = (knife_box.centerx + opp_box.centerx) // 2
                        hit_y = (knife_box.centery + opp_box.centery) // 2
                        kb = KNOCKBACK_FORCE if self.facing == 1 else -KNOCKBACK_FORCE
                        killed = opponent.take_damage(KNIFE_DAMAGE, (hit_x, hit_y), kb)
                        particle_system.spawn_blood(hit_x, hit_y)
                        if killed and self.game:
                            self.game._handle_kill(opponent.player_id, is_self_death=False)
    
    def take_damage(self, amount: int, hit_pos: tuple, knockback_x: float = 0.0):
        """Apply damage to this player. Triggers hit-stop, knockback, and death if HP hits 0.
        Returns True if this hit killed the player."""
        if not self.alive:
            return False
        if self.is_invulnerable:
            return False
            
        # Add hit-stop based on damage dealt (heavy hits = longer screen pause)
        if self.game and hasattr(self.game, 'add_hit_stop'):
            # e.g., 25 damage (bazooka) -> 0.15s, 5 damage (bullet) -> 0.03s
            freeze_time = min(0.2, amount * 0.006)
            self.game.add_hit_stop(freeze_time)
        
        # Bug fix #4: Use max to prevent negative health
        self.health = max(0, self.health - amount)
        
        # Trigger hit flash visual effect
        self.body.trigger_hit()
        
        if self.health > 0 and knockback_x != 0:
            self.vel_x = knockback_x
            self.hit_stun_timer = HIT_STUN_DURATION
        
        if self.health <= 0:
            # Determine hit direction for directional ragdoll
            hit_dir = 1 if knockback_x > 0 else (-1 if knockback_x < 0 else 0)
            self.die(hit_dir=hit_dir)
            
            # Tier 6: Longer hit-stop + screen shake on kill
            if self.game and hasattr(self.game, 'add_hit_stop'):
                self.game.add_hit_stop(0.1)  # brief dramatic pause
            if self.game and hasattr(self.game, 'camera'):
                self.game.camera.add_shake(4, 0.2)
            return True
        return False
    
    def heal(self, amount: int):
        """Restore health up to max health."""
        self.health = min(self.max_health, self.health + amount)
    
    def die(self, hit_dir=0):
        """Kill this player: set HP to 0, trigger ragdoll animation in the hit direction."""
        if not self.alive:
            return
        self.health = 0
        self.alive = False
        self.state = "DEAD"
        if hasattr(self, 'body'):
            self.body.trigger_ragdoll(self.x, self.y, self.facing, hit_dir=hit_dir)
        if self.audio_manager:
            self.audio_manager.play_sound("player_death")

        """Add ammo. Returns True if pickup was consumed."""
        if self.ammo >= self.max_ammo:
            return False
        self.ammo = self.max_ammo
        return True
    
    def pickup_shotgun(self):
        """Pick up a shotgun from the world. Grants full shotgun ammo."""
        self.has_shotgun = True
        self.shotgun_ammo = SHOTGUN_AMMO
        self.shotgun_cooldown = 0.0
        self.has_bazooka = False
        self.body.current_weapon = "shotgun"
        if self.audio_manager:
            self.audio_manager.play_sound("pickup_weapon")

    def pickup_bazooka(self):
        """Pick up a bazooka from the world."""
        self.has_bazooka = True
        self.bazooka_ammo = BAZOOKA_AMMO
        self.bazooka_cooldown = 0.0
        self.has_shotgun = False
        self.body.current_weapon = "bazooka"
        if self.audio_manager:
            self.audio_manager.play_sound("pickup_weapon")
            self.audio_manager.play_sound("player_death")
    
    def take_cliff_death(self):
        """Instant death from falling off the map edge. Uses a spinning ragdoll."""
        if not self.alive:
            return
        self.health = 0
        self.alive = False
        self.state = "DEAD"
        # Tier 4: Cliff deaths use tumble mode (whole body spins off)
        self.body.trigger_ragdoll(self.x, self.y, self.facing, hit_dir=0, is_cliff=True)
        if self.audio_manager:
            self.audio_manager.play_sound("player_death")
        if self.game:
            self.game._handle_kill(self.player_id, is_self_death=True)
    
    def get_knife_hitbox(self) -> pygame.Rect:
        """Get knife attack hitbox."""
        offset = PLAYER_WIDTH if self.facing == 1 else -KNIFE_RANGE
        return pygame.Rect(int(self.x) + offset, int(self.y) + 10, KNIFE_RANGE, PLAYER_HEIGHT - 20)
    
    def check_platform_collision(self, platforms):
        """One-way platform landing: player passes through from below, lands on top when falling."""
        player_rect = self.get_rect()
        # Extend 2px below feet so standing-on-edge still detects overlap
        feet_probe = pygame.Rect(player_rect.x, player_rect.y,
                                  player_rect.width, player_rect.height + 2)
        
        for plat in platforms:
            plat_rect = plat.rect
            
            # Bug fix #1: Check previous frame position to prevent fall-through
            prev_bottom = self.y + self.height - self.vel_y * 0.016  # Approximate dt
            
            if (feet_probe.colliderect(plat_rect) and
                    prev_bottom <= plat_rect.top + 5 and
                    self.vel_y >= 0):
                self.y = plat_rect.top - self.height + getattr(plat, 'player_y_offset', 0)
                self.vel_y = 0
                self.on_ground = True
                self.update_rect()
                break
    
    def check_trampoline_collision(self, clouds):
        """If the player lands on a bounce cloud, launch them upward."""
        player_rect = self.get_rect()
        for cloud in clouds:
            if not cloud.trampoline:
                continue
            # Only trigger when falling downward onto top of cloud
            prev_bottom = self.y + self.height - self.vel_y * 0.016
            # Use detected solid bounds for custom cloud images
            cx_off = getattr(cloud, 'solid_x_offset', 0)
            cw     = getattr(cloud, 'solid_w', cloud.rect.width)
            cy_off = getattr(cloud, 'solid_y_offset', 0)

            cloud_top = pygame.Rect(
                cloud.rect.x + cx_off,
                cloud.rect.y + cy_off,
                cw,
                8
            )
            if (player_rect.colliderect(cloud_top) and
                    prev_bottom <= cloud.rect.top + cy_off + 8 and
                    self.vel_y >= 0):
                # Check if player center is within cloud walkable edges
                center_x = self.x + self.width / 2
                c_edge_l = getattr(cloud, 'edge_left', 0)
                c_edge_r = getattr(cloud, 'edge_right', 0)
                walk_left  = cloud_top.left + c_edge_l
                walk_right = cloud_top.right - c_edge_r
                if center_x < walk_left or center_x > walk_right:
                    continue  # player misses the cloud edge
                # Apply per-cloud Y offset to bounce trigger
                y_off = getattr(cloud, 'player_y_offset', 0)
                if y_off != 0:
                    self.y += y_off
                # Launch upward — stronger than normal jump
                self.vel_y    = -cloud.bounce_force
                self.on_ground = False
                self.state     = "JUMPING"
                self.update_rect()
                break
    
    def check_barrel_collision(self, barrels):
        """Handle barrel collision: land on top to stand, or get pushed sideways."""
        player_rect = self.get_rect()
        # Extend 2px below feet so standing-on-edge still detects overlap
        feet_probe = pygame.Rect(player_rect.x, player_rect.y,
                                  player_rect.width, player_rect.height + 2)
        
        for barrel in barrels:
            # Use a narrower top collision zone matching
            # the visual barrel top width (not full rect width)
            barrel_top_zone = pygame.Rect(
                barrel.rect.x + barrel.solid_x_offset + BARREL_EDGE_LEFT,
                barrel.rect.y  + barrel.solid_y_offset,
                max(1, barrel.solid_w - BARREL_EDGE_LEFT - BARREL_EDGE_RIGHT),
                6
            )
            prev_feet = self.y + PLAYER_HEIGHT - self.vel_y * 0.016
            if (feet_probe.colliderect(barrel_top_zone) and
                    prev_feet <= barrel.rect.top + 8 and
                    self.vel_y >= 0):
                self.y = barrel.rect.top - PLAYER_HEIGHT + getattr(barrel, 'player_y_offset', 0)
                self.vel_y = 0
                self.on_ground = True
                self.update_rect()
                continue
            
            # Side collision — uses same edge offsets as the top zone
            # so the side rect doesn't extend beyond the walkable top area
            # Skip side push entirely if player is near/above barrel top
            # (falling off edge — let gravity handle it)
            barrel_side_rect = pygame.Rect(
                barrel.rect.x + barrel.solid_x_offset + BARREL_EDGE_LEFT,
                barrel.rect.y  + barrel.solid_y_offset,
                max(1, barrel.solid_w - BARREL_EDGE_LEFT - BARREL_EDGE_RIGHT),
                barrel.rect.height - barrel.solid_y_offset)
            player_feet_y = self.y + PLAYER_HEIGHT
            near_top = player_feet_y <= barrel.rect.top + barrel.solid_y_offset + barrel.rect.height // 2
            if not near_top and player_rect.colliderect(barrel_side_rect):
                overlap_left  = (player_rect.right -
                                 barrel_side_rect.left)
                overlap_right = (barrel_side_rect.right -
                                 player_rect.left)
                if overlap_left < overlap_right:
                    self.x -= overlap_left
                    self.vel_x = 0
                else:
                    self.x += overlap_right
                    self.vel_x = 0
                self.update_rect()
    
    def check_single_obstacle_collision(self, obstacle):
        """Same as barrel collision but for any single obstacle (like the destructible box)."""
        player_rect = self.get_rect()
        # Extend 2px below feet so standing-on-edge still detects overlap
        feet_probe = pygame.Rect(player_rect.x, player_rect.y,
                                  player_rect.width, player_rect.height + 2)

        # Top landing
        # Use solid bounds if available, fallback to inset
        sx_off = getattr(obstacle, 'solid_x_offset', 6)
        sw     = getattr(obstacle, 'solid_w',
                         obstacle.rect.width - 12)
        sy_off = getattr(obstacle, 'solid_y_offset', 0)

        top_zone = pygame.Rect(
            obstacle.rect.x + sx_off + BOX_EDGE_LEFT,
            obstacle.rect.y + sy_off,
            max(1, sw - BOX_EDGE_LEFT - BOX_EDGE_RIGHT),
            6
        )
        prev_feet = self.y + PLAYER_HEIGHT - self.vel_y * 0.016
        if (feet_probe.colliderect(top_zone) and
                prev_feet <= obstacle.rect.top + 8 and
                self.vel_y >= 0):
            self.y = obstacle.rect.top - PLAYER_HEIGHT + getattr(obstacle, 'player_y_offset', 0)
            self.vel_y = 0
            self.on_ground = True
            self.update_rect()
            return

        # Side push — uses same edge offsets as top zone
        # Skip side push if player is near/above box top
        # (falling off edge — let gravity handle it)
        obs_side_rect = pygame.Rect(
            obstacle.rect.x + sx_off + BOX_EDGE_LEFT,
            obstacle.rect.y + sy_off,
            max(1, sw - BOX_EDGE_LEFT - BOX_EDGE_RIGHT),
            obstacle.rect.height - sy_off)
        player_feet_y = self.y + PLAYER_HEIGHT
        near_top = player_feet_y <= obstacle.rect.top + sy_off + obstacle.rect.height // 2
        if not near_top and player_rect.colliderect(obs_side_rect):
            overlap_left  = (player_rect.right -
                             obs_side_rect.left)
            overlap_right = (obs_side_rect.right -
                             player_rect.left)
            if overlap_left < overlap_right:
                self.x -= overlap_left
            else:
                self.x += overlap_right
            self.vel_x = 0
            self.update_rect()
    
    def check_pickups(self, health_group, ammo_group):
        """Walk over health packs or ammo boxes to collect them."""
        # Update rect before collision check
        self.update_rect()
        
        # Health pickups
        hits = pygame.sprite.spritecollide(self, health_group, False)
        for pack in hits:
            if self.health < self.max_health:
                self.heal(pack.value)
                pack.kill()
                if self.audio_manager:
                    self.audio_manager.play_sound("pickup_health")

        # Ammo pickups
        hits = pygame.sprite.spritecollide(self, ammo_group, False)
        for pack in hits:
            if self.ammo < self.max_ammo:
                self.ammo = self.max_ammo
                pack.kill()
                if self.audio_manager:
                    self.audio_manager.play_sound("pickup_ammo")
    
    def draw(self, surface, camera):
        """Draw the player. Handles invulnerability flicker and spawn fade-in effect."""
        if not self.alive:
            # Still draw ragdoll / death animation parts
            self.body.draw(surface, self.x, self.y, self.facing)
            return
        self.update_rect()
        
        # Invulnerability flicker — skip draw every other 100ms
        if self.is_invulnerable:
            import time
            if int(time.monotonic() * 10) % 2 == 0:
                return
        
        # Materialize fade-in
        if self.materialize_alpha < 255:
            temp = pygame.Surface((int(self.width + 48), int(self.height + 48)), pygame.SRCALPHA)
            self.body.draw(temp, 24, 24, self.facing)
            temp.set_alpha(self.materialize_alpha)
            surface.blit(temp, (self.x - 24, self.y - 24))
        else:
            self.body.draw(surface, self.x, self.y, self.facing)

