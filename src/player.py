# src/player.py

import pygame
from src.physics import PhysicsObject
from src.animation import SkeletalBody
from src.constants import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, JUMP_FORCE, FAST_FALL_SPEED,
    GROUND_Y, GROUND_LEFT, GROUND_RIGHT, CLIFF_DEATH_Y,
    KNIFE_RANGE, KNIFE_DAMAGE, KNIFE_COOLDOWN, MAX_AMMO
)


class Player(PhysicsObject, pygame.sprite.Sprite):
    """Player character with combat and movement capabilities."""
    
    def __init__(self, player_id: int, start_x: int, controls: dict, assets: dict):
        PhysicsObject.__init__(self, start_x, GROUND_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.sprite.Sprite.__init__(self)
        
        # Identity
        self.player_id = player_id
        self.controls = controls
        
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
        
        # Shotgun state
        self.has_shotgun = False
        self.shotgun_ammo = 0
        self.shotgun_cooldown = 0.0
        
        # Skeletal body
        self.body = SkeletalBody(player_id, assets)
        
        # Reference to game (will be set by game.py)
        self.game = None
        self.audio_manager = None
    
    def update_rect(self):
        """Update rect to match current position."""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def handle_input(self, keys, dt):
        """Process player input."""
        if not self.alive:
            return
        
        ctrl = self.controls
        moving = False
        
        # Horizontal movement
        if keys[ctrl["left"]]:
            self.vel_x = -PLAYER_SPEED
            self.facing = -1
            moving = True
            if self.on_ground:
                self.state = "WALKING"
        elif keys[ctrl["right"]]:
            self.vel_x = PLAYER_SPEED
            self.facing = 1
            moving = True
            if self.on_ground:
                self.state = "WALKING"
        else:
            self.vel_x = 0
            if self.on_ground and self.state == "WALKING":
                self.state = "IDLE"
        
        # Jump — only when on ground
        if keys[ctrl["jump"]] and self.on_ground:
            self.vel_y = -JUMP_FORCE
            self.on_ground = False
            self.state = "JUMPING"
        
        # Crouch / Fast Fall
        if keys[ctrl["crouch"]]:
            if self.on_ground:
                self.state = "CROUCHING"
            else:
                self.vel_y = FAST_FALL_SPEED
        
        # Shoot — detect NEW press this frame (not held)
        if keys[ctrl["shoot"]] and not self.shoot_held_last:
            if self.has_shotgun and self.shotgun_ammo > 0:
                self.try_shotgun()
            else:
                self.try_shoot()
        self.shoot_held_last = keys[ctrl["shoot"]]
        
        # Knife — detect NEW press this frame
        if keys[ctrl["knife"]] and not self.knife_held_last:
            self.try_knife()
        self.knife_held_last = keys[ctrl["knife"]]
        
        # Apply friction
        self.apply_friction(moving)
        
        # Update rect after all movement
        self.update_rect()
    
    def try_shoot(self):
        """Attempt to fire a bullet."""
        if self.ammo <= 0:
            return
        
        # Bug fix #3: Check ammo > 0 BEFORE decrementing
        self.ammo = max(0, self.ammo - 1)
        
        # Spawn bullet at gun-hand position
        gun_x = self.x + (PLAYER_WIDTH + 5) if self.facing == 1 else self.x - 5
        gun_y = self.y + 20
        
        # Import here to avoid circular dependency
        from src.bullet import Bullet
        bullet = Bullet(gun_x, gun_y, self.facing, self.player_id)
        if self.game:
            self.game.bullet_group.add(bullet)
        
        # Trigger gun recoil animation
        self.body.trigger_gun_recoil()
        if self.audio_manager:
            self.audio_manager.play_sound("shoot")
    
    def try_knife(self):
        """Attempt to perform knife attack."""
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
        """Fire a shotgun blast — spread of SHOTGUN_PELLETS pellets."""
        from src.constants import (
            SHOTGUN_PELLETS, SHOTGUN_SPREAD_DEG,
            SHOTGUN_COOLDOWN
        )
        from src.bullet import ShotgunPellet

        if self.shotgun_cooldown > 0 or self.shotgun_ammo <= 0:
            return

        self.shotgun_ammo -= 1
        self.shotgun_cooldown = SHOTGUN_COOLDOWN

        # If shotgun ammo hits 0, drop the shotgun
        if self.shotgun_ammo <= 0:
            self.has_shotgun = False

        # Spread: evenly distribute pellets across ±SHOTGUN_SPREAD_DEG
        gun_x = (self.x + PLAYER_WIDTH + 5
                 if self.facing == 1 else self.x - 5)
        gun_y = self.y + 25

        if SHOTGUN_PELLETS == 1:
            angles = [0]
        else:
            step = (SHOTGUN_SPREAD_DEG * 2) / (SHOTGUN_PELLETS - 1)
            angles = [-SHOTGUN_SPREAD_DEG + i * step
                      for i in range(SHOTGUN_PELLETS)]

        for angle in angles:
            pellet = ShotgunPellet(
                gun_x, gun_y, self.facing, angle, self.player_id)
            if self.game:
                self.game.bullet_group.add(pellet)

        # Trigger gun recoil animation — stronger kick
        self.body.trigger_gun_recoil()
        if self.audio_manager:
            self.audio_manager.play_sound("shoot")
    
    def update_knife(self, opponent, particle_system, dt):
        """Update knife cooldown and hit detection."""
        if self.knife_cooldown > 0:
            self.knife_cooldown -= dt
        if self.shotgun_cooldown > 0:
            self.shotgun_cooldown -= dt
        
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
                        killed = opponent.take_damage(KNIFE_DAMAGE, (hit_x, hit_y))
                        particle_system.spawn_blood(hit_x, hit_y)
                        if killed and self.game:
                            self.game._trigger_ko(opponent.player_id)
    
    def take_damage(self, amount: int, hit_pos: tuple):
        """Apply damage. Returns True if this hit killed the player."""
        if not self.alive:
            return False
        
        # Bug fix #4: Use max to prevent negative health
        self.health = max(0, self.health - amount)
        
        if self.health <= 0:
            self.die()
            return True
        return False
    
    def heal(self, amount: int):
        """Heal player. Bug fix #4: Cap at max health."""
        self.health = min(self.max_health, self.health + amount)
    
    def add_ammo(self, amount: int):
        """Add ammo. Returns True if pickup was consumed."""
        if self.ammo >= self.max_ammo:
            return False
        self.ammo = self.max_ammo
        return True
    
    def pickup_shotgun(self):
        """Pick up a shotgun from the world. Grants full shotgun ammo."""
        from src.constants import SHOTGUN_AMMO
        self.has_shotgun = True
        self.shotgun_ammo = SHOTGUN_AMMO
        self.shotgun_cooldown = 0.0
        if self.audio_manager:
            self.audio_manager.play_sound("pickup")
    
    def die(self):
        """Kill player and trigger ragdoll."""
        self.alive = False
        self.state = "DEAD"
        self.body.trigger_ragdoll(self.x, self.y, self.facing)
        if self.audio_manager:
            self.audio_manager.play_sound("player_death")
    
    def take_cliff_death(self):
        """Instantly kill player for falling off the cliff edge."""
        if not self.alive:
            return
        self.health = 0
        self.die()
        if self.game:
            self.game._trigger_ko(self.player_id)
    
    def get_knife_hitbox(self) -> pygame.Rect:
        """Get knife attack hitbox."""
        offset = PLAYER_WIDTH if self.facing == 1 else -KNIFE_RANGE
        return pygame.Rect(int(self.x) + offset, int(self.y) + 10, KNIFE_RANGE, PLAYER_HEIGHT - 20)
    
    def check_platform_collision(self, platforms):
        """Check and resolve platform collisions (one-way platforms)."""
        player_rect = self.get_rect()
        
        for plat in platforms:
            plat_rect = plat.rect
            
            # Bug fix #1: Check previous frame position to prevent fall-through
            prev_bottom = self.y + self.height - self.vel_y * 0.016  # Approximate dt
            
            if (player_rect.colliderect(plat_rect) and
                    prev_bottom <= plat_rect.top + 5 and
                    self.vel_y >= 0):
                self.y = plat_rect.top - self.height
                self.vel_y = 0
                self.on_ground = True
                self.update_rect()
                break
    
    def check_trampoline_collision(self, clouds):
        """
        If player lands on a trampoline cloud,
        launch them upward with bounce force.
        """
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
                # Launch upward — stronger than normal jump
                self.vel_y    = -cloud.bounce_force
                self.on_ground = False
                self.state     = "JUMPING"
                self.update_rect()
                break
    
    def check_barrel_collision(self, barrels):
        """Check and resolve barrel collisions (solid obstacles)."""
        player_rect = self.get_rect()
        
        for barrel in barrels:
            # Use a narrower top collision zone matching
            # the visual barrel top width (not full rect width)
            barrel_top_zone = pygame.Rect(
                barrel.rect.x + barrel.solid_x_offset,
                barrel.rect.y  + barrel.solid_y_offset,
                barrel.solid_w,
                6
            )
            prev_feet = self.y + PLAYER_HEIGHT - self.vel_y * 0.016
            if (player_rect.colliderect(barrel_top_zone) and
                    prev_feet <= barrel.rect.top + 8 and
                    self.vel_y >= 0):
                self.y = barrel.rect.top - PLAYER_HEIGHT
                self.vel_y = 0
                self.on_ground = True
                self.update_rect()
                continue
            
            # Side collision uses solid bounds rect
            barrel_side_rect = pygame.Rect(
                barrel.rect.x + barrel.solid_x_offset,
                barrel.rect.y  + barrel.solid_y_offset,
                barrel.solid_w,
                barrel.rect.height - barrel.solid_y_offset)
            if player_rect.colliderect(barrel_side_rect):
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
        """
        Solid collision with any single rect-based obstacle.
        Same logic as barrel — land on top or push sideways.
        """
        player_rect = self.get_rect()

        # Top landing
        # Use solid bounds if available, fallback to inset
        sx_off = getattr(obstacle, 'solid_x_offset', 6)
        sw     = getattr(obstacle, 'solid_w',
                         obstacle.rect.width - 12)
        sy_off = getattr(obstacle, 'solid_y_offset', 0)

        top_zone = pygame.Rect(
            obstacle.rect.x + sx_off,
            obstacle.rect.y + sy_off,
            sw,
            6
        )
        prev_feet = self.y + PLAYER_HEIGHT - self.vel_y * 0.016
        if (player_rect.colliderect(top_zone) and
                prev_feet <= obstacle.rect.top + 8 and
                self.vel_y >= 0):
            self.y = obstacle.rect.top - PLAYER_HEIGHT
            self.vel_y = 0
            self.on_ground = True
            self.update_rect()
            return

        # Side push
        obs_side_rect = pygame.Rect(
            obstacle.rect.x + sx_off,
            obstacle.rect.y + sy_off,
            sw,
            obstacle.rect.height - sy_off)
        if player_rect.colliderect(obs_side_rect):
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
        """Check and collect pickups."""
        # Update rect before collision check
        self.update_rect()
        
        # Health pickups
        hits = pygame.sprite.spritecollide(self, health_group, False)
        for pack in hits:
            if self.health < self.max_health:
                self.heal(pack.value)
                pack.kill()
                if self.audio_manager:
                    self.audio_manager.play_sound("pickup")

        # Ammo pickups
        hits = pygame.sprite.spritecollide(self, ammo_group, False)
        for pack in hits:
            if self.ammo < self.max_ammo:
                self.ammo = self.max_ammo
                pack.kill()
                if self.audio_manager:
                    self.audio_manager.play_sound("pickup")
    
    def draw(self, surface, camera):
        """Draw player body."""
        self.update_rect()
        self.body.draw(surface, self.x, self.y, self.facing)

