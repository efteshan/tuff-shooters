# src/game.py

import pygame
import random
from src.constants import (
    SCREEN_W, SCREEN_H, VIRTUAL_W, VIRTUAL_H, SKY_COLOR, GROUND_Y,
    CLIFF_DEATH_Y, CONTROLS, P1_COLOR, P2_COLOR, PLAYER_WIDTH, PLAYER_HEIGHT,
    load_or_placeholder, GIF_BLOOD_STRIP, GIF_BLOOD_FRAMES,
    GIF_KO_STRIP, GIF_KO_FRAMES, IMG_MENU_BG, MAX_AMMO,
    KNOCKBACK_FORCE, BOX_X,
    RESPAWN_DELAY, INVULN_DURATION, MAX_KILLS_TO_WIN,
    HEAD_SIZE_BASE, HEAD_SIZE_STEP
)
from src.camera import Camera
from src.player import Player
from src.arena import Ground, create_arena
from src.pickups import PickupSpawnManager, ShotgunPickup, BazookaPickup, preload_pickup_images
from src.particles import ParticleSystem
from src.bullet import ShotgunPellet, Rocket, Explosion
from src.ui import HUD, KOScreen
from src.menu import MainMenu, PauseMenu, GameOverMenu, DropFacesMenu
from src.animation import SkeletalBody
from src.audio import AudioManager


class Game:
    """Master game controller with state machine."""
    
    def __init__(self, screen):
        self.screen = screen
        self.state = "STATE_MENU"
        self.hit_stop = 0.0  # added for screen freeze on big hits
        
        # Initialize Audio Manager and load sounds
        self.audio_manager = AudioManager()
        self._load_audio()
        
        # Load assets
        self._load_assets()
        
        # Initialize camera
        self.camera = Camera()
        
        # Initialize fonts
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 72)
        
        # Initialize menus
        self.menu = MainMenu(self.menu_bg, self.font_large, self.font_medium)
        self.menu.audio_manager = self.audio_manager
        self.pause_menu = PauseMenu(self.font_medium)
        self.pause_menu.audio_manager = self.audio_manager
        self.game_over_menu = GameOverMenu(self.font_large, self.font_medium)
        self.game_over_menu.audio_manager = self.audio_manager
        self.drop_faces_menu = DropFacesMenu(self.font_large, self.font_medium)
        self.drop_faces_menu.audio_manager = self.audio_manager
        
        # Custom face surfaces (set via Drop Faces menu)
        self.p1_custom_face = None
        self.p2_custom_face = None
        self.p1_head_base = 1.0
        self.p2_head_base = 1.0
        
        # Initialize HUD
        self.hud = HUD(self.font_small)
        
        # Initialize K.O. screen
        self.ko_screen = KOScreen(GIF_KO_STRIP, GIF_KO_FRAMES)
        
        # Initialize arena
        self.platforms, self.barrels, self.box, self.bg_clouds, self.trampoline_clouds = create_arena(self.arena_assets)
        self.ground = Ground(self.arena_assets['ground'])
        
        # Initialize sprite groups
        self.bullet_group = pygame.sprite.Group()
        self.shotgun_group = pygame.sprite.Group()
        self.health_group = pygame.sprite.Group()
        self.ammo_group = pygame.sprite.Group()
        
        # Initialize particle system
        self.particles = ParticleSystem(GIF_BLOOD_STRIP, GIF_BLOOD_FRAMES)
        
        # Initialize pickup spawn manager
        self.spawn_manager = PickupSpawnManager(self.platforms)
        
        # Initialize players
        self.p1 = Player(1, 320, CONTROLS["p1"], self.p1_assets)
        self.p2 = Player(2, 920, CONTROLS["p2"], self.p2_assets)
        self.p1.game = self
        self.p1.audio_manager = self.audio_manager
        self.p2.game = self
        self.p2.audio_manager = self.audio_manager
        
        self.p1_score = 0
        self.p2_score = 0
        
        # Pause button rect
        self.pause_btn_rect = pygame.Rect(SCREEN_W//2 - 50, 10, 100, 36)
        
        # Start with menu music
        self.audio_manager.play_music()

    def _load_audio(self):
        """Load all audio files."""
        self.audio_manager.load_sound("shoot", "assets/sounds/shoot.wav")
        self.audio_manager.load_sound("knife_swoosh", "assets/sounds/knife_swoosh.wav")
        self.audio_manager.load_sound("impact", "assets/sounds/impact.wav")
        self.audio_manager.load_sound("player_death", "assets/sounds/player_death.wav")
        self.audio_manager.load_sound("pickup", "assets/sounds/pickup.wav")
        self.audio_manager.load_sound("menu_click", "assets/sounds/menu_click.wav")
        self.audio_manager.load_sound("game_over", "assets/sounds/game_over.wav")
        self.audio_manager.load_music("assets/sounds/menu_music.wav")

    
    def _load_assets(self):
        """Load all game assets with placeholders."""
        # Player 1 assets
        self.p1_assets = {
            'head': load_or_placeholder('assets/sprites/p1_head.png', (20, 20), P1_COLOR),
            'torso': load_or_placeholder('assets/sprites/p1_torso.png', (24, 32), P1_COLOR),
            'arm_r': load_or_placeholder('assets/sprites/p1_arm_right.png', (8, 24), P1_COLOR),
            'arm_l': load_or_placeholder('assets/sprites/p1_arm_left.png', (8, 24), P1_COLOR),
            'leg_r': load_or_placeholder('assets/sprites/p1_leg_right.png', (10, 28), P1_COLOR),
            'leg_l': load_or_placeholder('assets/sprites/p1_leg_left.png', (10, 28), P1_COLOR),
        }
        
        # Player 2 assets
        self.p2_assets = {
            'head': load_or_placeholder('assets/sprites/p2_head.png', (20, 20), P2_COLOR),
            'torso': load_or_placeholder('assets/sprites/p2_torso.png', (24, 32), P2_COLOR),
            'arm_r': load_or_placeholder('assets/sprites/p2_arm_right.png', (8, 24), P2_COLOR),
            'arm_l': load_or_placeholder('assets/sprites/p2_arm_left.png', (8, 24), P2_COLOR),
            'leg_r': load_or_placeholder('assets/sprites/p2_leg_right.png', (10, 28), P2_COLOR),
            'leg_l': load_or_placeholder('assets/sprites/p2_leg_left.png', (10, 28), P2_COLOR),
        }
        
        # Arena assets
        self.arena_assets = {
            'platform': load_or_placeholder('assets/sprites/platform.png', (200, 20), (100, 70, 50)),
            'ground': load_or_placeholder('assets/sprites/ground_tile.png', (100, 80), (80, 60, 40)),
        }
        
        # Pickup assets
        self.pickup_images = {
            'health_pack': load_or_placeholder('assets/pickups/health_pack.png', (30, 30), (60, 200, 60)),
            'ammo_box': load_or_placeholder('assets/pickups/ammo_box.png', (30, 30), (200, 200, 60)),
        }
        # Preload custom pickup images now (avoids lag on first spawn)
        preload_pickup_images()
        
        # Menu background
        self.menu_bg = load_or_placeholder('assets/ui/menu_bg.png', (SCREEN_W, SCREEN_H), (40, 40, 60))
    
    def handle_event(self, event):
        """Handle pygame events."""
        if self.state == "STATE_MENU":
            action = self.menu.handle_event(event)
            if action == "play":
                self.reset_game()
                self.p1_score = 0
                self.p2_score = 0
                self.state = "STATE_PLAYING"
                self.hud.is_paused = False
            elif action == "drop_faces":
                self.state = "STATE_DROP_FACES"
        
        elif self.state == "STATE_DROP_FACES":
            action = self.drop_faces_menu.handle_event(event)
            if action == "done":
                # Store chosen faces and head base scales
                self.p1_custom_face = self.drop_faces_menu.p1_face
                self.p2_custom_face = self.drop_faces_menu.p2_face
                self.p1_head_base = self.drop_faces_menu.p1_head_base
                self.p2_head_base = self.drop_faces_menu.p2_head_base
                self.state = "STATE_MENU"
        
        elif self.state == "STATE_PLAYING":
            # Check pause button click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pause_btn_rect.collidepoint(event.pos):
                    self.state = "STATE_PAUSED"
                    self.hud.is_paused = True
            # Check Escape key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "STATE_PAUSED"
                self.hud.is_paused = True
        
        elif self.state == "STATE_PAUSED":
            action = self.pause_menu.handle_event(event)
            if action == "continue":
                self.state = "STATE_PLAYING"
                self.hud.is_paused = False
            elif action == "new":
                self.reset_game()
                self.p1_score = 0
                self.p2_score = 0
                self.state = "STATE_PLAYING"
                self.hud.is_paused = False
            elif action == "exit":
                self.p1_score = 0
                self.p2_score = 0
                self.state = "STATE_MENU"
                self.hud.is_paused = False

        elif self.state == "STATE_GAME_OVER":
            action = self.game_over_menu.handle_event(event)
            if action == "new":
                self.reset_game()
                self.p1_score = 0
                self.p2_score = 0
                self.state = "STATE_PLAYING"
                self.hud.is_paused = False
            elif action == "exit":
                self.p1_score = 0
                self.p2_score = 0
                self.state = "STATE_MENU"
                self.hud.is_paused = False
    
    def update(self, dt):
        """Update game state."""
        if self.state == "STATE_MENU" or self.state == "STATE_DROP_FACES":
            return
        
        if self.state == "STATE_PAUSED" or self.state == "STATE_GAME_OVER":
            return
        
        # STATE_PLAYING
        self._update_playing(dt)

    def add_hit_stop(self, duration: float):
        """Freeze game logic briefly for dramatic impact."""
        self.hit_stop = max(self.hit_stop, duration)
        
    def _update_playing(self, dt):
        """Update game logic during play state."""
        # Hit stop freezes game logic for a moment to emphasize heavy impacts
        if self.hit_stop > 0:
            self.hit_stop -= dt
            
            # We still need to update the camera (screen shake should continue to decay)
            p1_cx = self.p1.x + self.p1.width / 2
            p2_cx = self.p2.x + self.p2.width / 2
            self.camera.update(p1_cx, p2_cx, dt)
            return

        keys = pygame.key.get_pressed()
        
        # Update players
        for player in [self.p1, self.p2]:
            if player.alive:
                player.handle_input(keys, dt)
                player.apply_physics(dt)
                player.check_platform_collision(self.platforms)
                player.check_barrel_collision(self.barrels)
                # Box collision — treat like barrel (solid obstacle)
                if not self.box.destroyed:
                    player.check_single_obstacle_collision(self.box)
                player.check_trampoline_collision(
                    self.trampoline_clouds)
                player.check_pickups(self.health_group, self.ammo_group)
                # Weapon pickup check
                if player.alive:
                    hits = pygame.sprite.spritecollide(
                        player, self.shotgun_group, False)
                    for wp in hits:
                        if isinstance(wp, ShotgunPickup) and not player.has_shotgun:
                            player.pickup_shotgun()
                            wp.kill()
                        elif isinstance(wp, BazookaPickup) and not player.has_bazooka:
                            player.pickup_bazooka()
                            wp.kill()
                # Cliff death — player fell off edge of ground
                if player.alive and player.rect.bottom >= CLIFF_DEATH_Y:
                    player.take_cliff_death()
                
                # Fall damage — only on landing on GROUND, not platforms
                if player.alive:
                    if player.on_ground and not player._was_on_ground:
                        ground_level_y = GROUND_Y - player.height
                        on_actual_ground = abs(player.y - ground_level_y) < 10
                        fall_height = player.y - player._highest_y
                        if on_actual_ground and fall_height > 200:
                            t = min(1.0, (fall_height - 200) / 300)
                            dmg = int(5 + t * 10)
                            player.health = max(0, player.health - dmg)
                            self.camera.add_shake(2, 0.15)
                            if player.health <= 0:
                                player.die(hit_dir=0)
                                self._handle_kill(player.player_id, is_self_death=True)
                        player._highest_y = player.y
                    player._was_on_ground = player.on_ground
        
        # Respawn logic — dead players respawn after delay
        for player in [self.p1, self.p2]:
            if not player.alive and player.respawn_timer >= 0:
                player.respawn_timer -= dt
                # Keep ragdoll animating
                player.body.update(player.state, player.vel_x, player.on_ground, dt, player.vel_y)
                if player.respawn_timer <= 0:
                    self._respawn_player(player)
            
            # Invulnerability countdown
            if player.is_invulnerable:
                player.invuln_timer -= dt
                if player.invuln_timer <= 0:
                    player.is_invulnerable = False
            
            # Materialize fade-in (0→255 over 0.3s)
            if player.alive and player.materialize_alpha < 255:
                player._materialize_timer += dt
                player.materialize_alpha = min(255, int(player._materialize_timer / 0.3 * 255))
        
        # Update knife combat
        if self.p1.alive:
            self.p1.update_knife(self.p2, self.particles, dt)
        if self.p2.alive:
            self.p2.update_knife(self.p1, self.particles, dt)
        
        # Update bullets
        self.bullet_group.update(dt)
        self.check_bullet_collisions()
        
        # Update pickups
        self.health_group.update(dt)
        self.ammo_group.update(dt)
        self.spawn_manager.update(dt, self.health_group, self.ammo_group, self.pickup_images)
        
        # Update particles
        self.particles.update(dt)
        
        # Update destructible box respawn timer
        self.box.update(dt)
        # Update shotgun pickups (lifetime countdown)
        self.shotgun_group.update(dt)
        
        # Update skeletal bodies
        for player in [self.p1, self.p2]:
            player.body.update(player.state, player.vel_x, player.on_ground, dt, player.vel_y)
        
        # Update camera
        p1_cx = self.p1.x + self.p1.width / 2
        p2_cx = self.p2.x + self.p2.width / 2
        self.camera.update(p1_cx, p2_cx, dt)
    
    def check_bullet_collisions(self):
        """Check bullet collisions with players and barrels."""
        
        # Process Explosions first for splash damage
        for bullet in list(self.bullet_group):
            if isinstance(bullet, Explosion):
                if not bullet.has_damaged:
                    bullet.has_damaged = True
                    for player in [self.p1, self.p2]:
                        if not player.alive:
                            continue
                        
                        dist = ((bullet.x - (player.x + player.width/2))**2 + 
                                (bullet.y - (player.y + player.height/2))**2)**0.5
                        
                        if dist <= bullet.radius:
                            kb_dir = 1 if player.x > bullet.x else -1
                            killed = player.take_damage(bullet.damage, player.rect.center, KNOCKBACK_FORCE * 1.5 * kb_dir)
                            if killed:
                                self._handle_kill(player.player_id, is_self_death=False)
                continue
            # Check normal bullets/rockets
            collided = False
            
            # vs Barrels
            for barrel in self.barrels:
                if bullet.rect.colliderect(barrel.rect):
                    collided = True
                    break
            
            # vs DestructibleBox
            if not collided and not self.box.destroyed:
                if bullet.rect.colliderect(self.box.rect):
                    collided = True
                    dmg = (bullet.get_effective_damage(bullet.x)
                           if isinstance(bullet, ShotgunPellet)
                           else bullet.damage)
                    result = self.box.take_damage(dmg)
                    if result == 'destroyed':
                        self.camera.add_shake(10.0, 0.3)
                        self._spawn_shotgun_from_box()
            
            # vs Players
            hit_player = None
            if not collided:
                for player in [self.p1, self.p2]:
                    if player.player_id == bullet.owner_id:
                        continue
                    if not player.alive:
                        continue
                    if bullet.rect.colliderect(player.get_rect()):
                        collided = True
                        hit_player = player
                        break
            
            if collided:
                if isinstance(bullet, Rocket):
                    # Spawn explosion
                    exp = Explosion(bullet.rect.centerx, bullet.rect.centery, bullet.owner_id)
                    self.bullet_group.add(exp)
                    self.camera.add_shake(15.0, 0.4)
                    self.audio_manager.play_sound("impact") # Add explosion sound later
                else:
                    if hit_player:
                        kb_dir = 1 if bullet.vel_x > 0 else -1
                        killed = hit_player.take_damage(bullet.damage, hit_player.rect.center, KNOCKBACK_FORCE * 0.3 * kb_dir)
                        self.particles.spawn_blood(bullet.rect.centerx, bullet.rect.centery)
                        if killed:
                            self._handle_kill(hit_player.player_id, is_self_death=False)
                    self.audio_manager.play_sound("impact")
                
                bullet.kill()
                bullet.alive = False
    
    def _handle_kill(self, victim_id, is_self_death=False):
        """Handle a player kill: streak logic, respawn timer, win check."""
        victim = self.p1 if victim_id == 1 else self.p2
        killer = self.p2 if victim_id == 1 else self.p1
        
        # Reset victim's streak
        victim_base = self.p1_head_base if victim_id == 1 else self.p2_head_base
        victim.head_streak = 0
        victim.head_scale = victim_base
        victim.body.current_head_scale = victim_base
        
        if not is_self_death:
            # Reward killer
            killer_base = self.p2_head_base if victim_id == 1 else self.p1_head_base
            killer.head_streak += 1
            killer.head_scale = killer_base + killer.head_streak * HEAD_SIZE_STEP
            killer.body.current_head_scale = killer.head_scale
            
            # Increment score
            if victim_id == 1:
                self.p2_score += 1
            else:
                self.p1_score += 1
            
            # Win check
            if killer.head_streak >= MAX_KILLS_TO_WIN:
                self.state = "STATE_GAME_OVER"
                return
        
        # Start respawn timer on victim
        victim.respawn_timer = RESPAWN_DELAY
    
    def _respawn_player(self, player):
        """Teleport player back to start and make invulnerable."""
        player.x = float(player.start_x)
        player.y = float(GROUND_Y - PLAYER_HEIGHT)
        player.vel_x = 0.0
        player.vel_y = 0.0
        player.health = 100
        player.ammo = MAX_AMMO
        player.alive = True
        player.state = "IDLE"
        player.facing = 1 if player.player_id == 1 else -1
        custom_face = self.p1_custom_face if player.player_id == 1 else self.p2_custom_face
        assets = self.p1_assets if player.player_id == 1 else self.p2_assets
        player.body = SkeletalBody(player.player_id, assets, custom_face=custom_face)
        player.body.current_head_scale = player.head_scale
        player.knife_cooldown = 0.0
        player.shoot_held_last = False
        player.knife_held_last = False
        player.knife_hit_pending = False
        player.on_ground = True
        player.dash_cooldown = 0.0
        player.is_dashing = False
        player.hit_stun_timer = 0.0
        player.has_shotgun = False
        player.has_bazooka = False
        player._highest_y = player.y
        player._was_on_ground = True
        player.is_invulnerable = True
        player.invuln_timer = INVULN_DURATION
        player.materialize_alpha = 0
        player._materialize_timer = 0.0
        player.respawn_timer = -1.0
        player.update_rect()
    
    def _spawn_shotgun_from_box(self):
        """Drop a shotgun or bazooka pickup at the box position."""
        
        self.shotgun_group.empty()
        
        if random.random() < 0.3: # 30% chance for bazooka
            sg = BazookaPickup(BOX_X, GROUND_Y)
            self.shotgun_group.add(sg)
            print(f"[BAZOOKA] Spawned at ({BOX_X}, {GROUND_Y}) ")
        else:
            sg = ShotgunPickup(BOX_X, GROUND_Y)
            self.shotgun_group.add(sg)
            print(f"[SHOTGUN] Spawned at ({BOX_X}, {GROUND_Y}) ")
    
    def reset_game(self):
        """Full match reset."""
        # Reset Player 1
        self.p1.x = 320.0
        self.p1.y = float(GROUND_Y - PLAYER_HEIGHT)
        self.p1.vel_x = 0.0
        self.p1.vel_y = 0.0
        self.p1.health = 100
        self.p1.ammo = MAX_AMMO
        self.p1.alive = True
        self.p1.state = "IDLE"
        self.p1.facing = 1
        self.p1.body = SkeletalBody(1, self.p1_assets, custom_face=self.p1_custom_face)
        self.p1.knife_cooldown = 0.0
        self.p1.shoot_held_last = False
        self.p1.knife_held_last = False
        self.p1.knife_hit_pending = False
        self.p1.on_ground = True
        self.p1.dash_cooldown = 0.0
        self.p1.is_dashing = False
        self.p1.hit_stun_timer = 0.0
        self.p1.has_shotgun = False
        self.p1.has_bazooka = False
        self.p1._highest_y = self.p1.y
        self.p1._was_on_ground = True
        self.p1.head_streak = 0
        self.p1.head_scale = self.p1_head_base
        self.p1.is_invulnerable = False
        self.p1.invuln_timer = 0.0
        self.p1.respawn_timer = -1.0
        self.p1.materialize_alpha = 255
        self.p1._materialize_timer = 0.0
        self.p1.update_rect()
        self.p1.body.current_head_scale = self.p1_head_base
        
        # Reset Player 2
        self.p2.x = 920.0
        self.p2.y = float(GROUND_Y - PLAYER_HEIGHT)
        self.p2.vel_x = 0.0
        self.p2.vel_y = 0.0
        self.p2.health = 100
        self.p2.ammo = MAX_AMMO
        self.p2.alive = True
        self.p2.state = "IDLE"
        self.p2.facing = -1
        self.p2.body = SkeletalBody(2, self.p2_assets, custom_face=self.p2_custom_face)
        self.p2.knife_cooldown = 0.0
        self.p2.shoot_held_last = False
        self.p2.knife_held_last = False
        self.p2.knife_hit_pending = False
        self.p2.on_ground = True
        self.p2.dash_cooldown = 0.0
        self.p2.is_dashing = False
        self.p2.hit_stun_timer = 0.0
        self.p2.has_shotgun = False
        self.p2.has_bazooka = False
        self.p2._highest_y = self.p2.y
        self.p2._was_on_ground = True
        self.p2.head_streak = 0
        self.p2.head_scale = self.p2_head_base
        self.p2.is_invulnerable = False
        self.p2.invuln_timer = 0.0
        self.p2.respawn_timer = -1.0
        self.p2.materialize_alpha = 255
        self.p2._materialize_timer = 0.0
        self.p2.update_rect()
        self.p2.body.current_head_scale = self.p2_head_base
        
        # Clear all active projectiles and pickups
        self.bullet_group.empty()
        # Reset destructible box
        self.box._respawn()
        # Clear shotgun pickups
        self.shotgun_group.empty()
        # Reset shotgun state on both players
        self.p1.has_shotgun = False
        self.p1.shotgun_ammo = 0
        self.p1.shotgun_cooldown = 0.0
        self.p2.has_shotgun = False
        self.p2.shotgun_ammo = 0
        self.p2.shotgun_cooldown = 0.0
        self.health_group.empty()
        self.ammo_group.empty()
        
        # Reset particle system
        self.particles.active_sparks.clear()
        
        # Reset spawn timers
        self.spawn_manager.health_timer = random.uniform(10.0, 15.0)
        self.spawn_manager.ammo_timer = random.uniform(5.0, 7.0)
        
        # Camera is handled by update method, no need to reset zoom values
    
    def draw(self):
        """Draw current game state."""
        if self.state == "STATE_MENU":
            self.menu.draw(self.screen)
            return
        
        if self.state == "STATE_DROP_FACES":
            self.drop_faces_menu.draw(self.screen, self.menu_bg)
            return
        
        # Draw game (for PLAYING, PAUSED, and KO states)
        self._draw_playing()
        
        # Draw HUD on real screen
        self.hud.draw(self.screen, self.p1, self.p2)
        
        # Draw overlays
        if self.state == "STATE_PAUSED":
            self.pause_menu.draw(self.screen)
        elif self.state == "STATE_KO":
            self.ko_screen.draw(self.screen)
        elif self.state == "STATE_GAME_OVER":
            winner_name = "PLAYER 1" if self.p1_score > self.p2_score else "PLAYER 2"
            self.game_over_menu.draw(self.screen, winner_name)
    
    def _draw_playing(self):
        """Draw game world to virtual surface, then apply camera to screen."""
        # Get the virtual surface from the camera
        virtual_surface = self.camera.virtual_surface
        
        # Clear virtual surface
        virtual_surface.fill(SKY_COLOR)
        
        # Draw ground
        self.ground.draw(virtual_surface, self.camera)
        
        # Draw background clouds first (behind everything)
        for cloud in self.bg_clouds:
            cloud.draw(virtual_surface)
        for cloud in self.trampoline_clouds:
            cloud.draw(virtual_surface)
        
        # Draw platforms
        for plat in self.platforms:
            plat.draw(virtual_surface, self.camera)
        
        # Draw barrels
        for barrel in self.barrels:
            barrel.draw(virtual_surface, self.camera)
        
        # Draw destructible box
        self.box.draw(virtual_surface, self.camera)
        
        # Draw pickups
        for pack in self.health_group:
            pack.draw(virtual_surface, self.camera)
        for pack in self.ammo_group:
            pack.draw(virtual_surface, self.camera)
        
        # Draw shotgun pickups
        for sg in self.shotgun_group:
            sg.draw(virtual_surface, self.camera)
        
        # Draw bullets
        for bullet in self.bullet_group:
            bullet.draw(virtual_surface, self.camera)
        
        # Draw players
        self.p1.draw(virtual_surface, self.camera)
        self.p2.draw(virtual_surface, self.camera)
        
        # Draw particles
        self.particles.draw(virtual_surface, self.camera)
        
        # Apply camera transformation to real screen
        self.camera.render(self.screen)
        
