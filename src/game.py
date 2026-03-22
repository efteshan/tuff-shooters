# src/game.py

import pygame
import random
from src.constants import (
    SCREEN_W, SCREEN_H, VIRTUAL_W, VIRTUAL_H, SKY_COLOR, GROUND_Y,
    CLIFF_DEATH_Y, CONTROLS, P1_COLOR, P2_COLOR, PLAYER_WIDTH, PLAYER_HEIGHT,
    load_or_placeholder, GIF_BLOOD_STRIP, GIF_BLOOD_FRAMES,
    GIF_KO_STRIP, GIF_KO_FRAMES, IMG_MENU_BG, MAX_AMMO
)
from src.camera import Camera
from src.player import Player
from src.arena import Ground, create_arena
from src.pickups import PickupSpawnManager
from src.particles import ParticleSystem
from src.ui import HUD, KOScreen
from src.menu import MainMenu, PauseMenu, GameOverMenu
from src.animation import SkeletalBody
from src.audio import AudioManager


class Game:
    """Master game controller with state machine."""
    
    def __init__(self, screen):
        self.screen = screen
        self.state = "STATE_MENU"
        
        # Bug fix #2: K.O. triggered flag
        self.ko_triggered = False
        
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
        if self.state == "STATE_MENU":
            return
        
        if self.state == "STATE_KO":
            self.ko_screen.update(dt)
            if self.ko_screen.done:
                self.reset_game()
                self.state = "STATE_PLAYING"
                self.hud.is_paused = False
            return
        
        if self.state == "STATE_PAUSED" or self.state == "STATE_GAME_OVER":
            return
        
        # STATE_PLAYING
        self._update_playing(dt)
    
    def _update_playing(self, dt):
        """Update game logic during play state."""
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
                # Shotgun pickup check
                if player.alive:
                    hits = pygame.sprite.spritecollide(
                        player, self.shotgun_group, False)
                    for sg in hits:
                        if not player.has_shotgun:
                            player.pickup_shotgun()
                            sg.kill()
                # Cliff death — player fell off edge of ground
                if player.alive and player.rect.bottom >= CLIFF_DEATH_Y:
                    player.take_cliff_death()
        
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
            player.body.update(player.state, player.vel_x, player.on_ground, dt)
        
        # Update camera
        p1_cx = self.p1.x + self.p1.width / 2
        p2_cx = self.p2.x + self.p2.width / 2
        self.camera.update(p1_cx, p2_cx, dt)
    
    def check_bullet_collisions(self):
        """Check bullet collisions with players and barrels."""
        for bullet in list(self.bullet_group):
            # vs Barrels
            for barrel in self.barrels:
                if bullet.rect.colliderect(barrel.rect):
                    bullet.kill()
                    self.audio_manager.play_sound("impact")
                    break
            
            if not bullet.alive:
                continue
            
            # vs DestructibleBox
            if not self.box.destroyed:
                if bullet.rect.colliderect(self.box.rect):
                    from src.bullet import ShotgunPellet
                    dmg = (bullet.get_effective_damage(bullet.x)
                           if isinstance(bullet, ShotgunPellet)
                           else bullet.damage)
                    result = self.box.take_damage(dmg)
                    # Mark bullet dead BEFORE checking result
                    # prevents multiple pellets hitting box same frame
                    bullet.kill()
                    bullet.alive = False
                    if result == 'destroyed':
                        self._spawn_shotgun_from_box()
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
                    self.audio_manager.play_sound("impact")
                    bullet.kill()
                    if killed:
                        self._trigger_ko(player.player_id)
                    break
    
    def _trigger_ko(self, loser_id):
        """Trigger K.O. state. Bug fix #2: prevent double trigger."""
        if not self.ko_triggered:
            self.ko_triggered = True

            if loser_id == 1:
                self.p2_score += 1
            else:
                self.p1_score += 1

            if self.p1_score >= 3 or self.p2_score >= 3:
                self.state = "STATE_GAME_OVER"
                self.hud.is_paused = False
            else:
                self.ko_screen.reset()
                self.state = "STATE_KO"
                self.hud.is_paused = False
    
    def _spawn_shotgun_from_box(self):
        """Drop a shotgun pickup at the box position."""
        from src.pickups import ShotgunPickup
        from src.constants import BOX_X, GROUND_Y
        # Always clear any existing shotgun pickup before spawning new one
        # Prevents stacking/invisible duplicate pickups on repeated box bursts
        self.shotgun_group.empty()
        sg = ShotgunPickup(BOX_X, GROUND_Y)
        self.shotgun_group.add(sg)
        print(f"[SHOTGUN] Spawned at ({BOX_X}, {GROUND_Y}) "
              f"rect={sg.rect} lifetime={sg.lifetime}")
    
    def reset_game(self):
        """Full match reset."""
        # Bug fix #2: Reset K.O. flag
        self.ko_triggered = False
        
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
        self.p1.body = SkeletalBody(1, self.p1_assets)
        self.p1.knife_cooldown = 0.0
        self.p1.shoot_held_last = False
        self.p1.knife_held_last = False
        self.p1.knife_hit_pending = False
        self.p1.on_ground = True
        self.p1.update_rect()
        
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
        self.p2.body = SkeletalBody(2, self.p2_assets)
        self.p2.knife_cooldown = 0.0
        self.p2.shoot_held_last = False
        self.p2.knife_held_last = False
        self.p2.knife_hit_pending = False
        self.p2.on_ground = True
        self.p2.update_rect()
        
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
        
