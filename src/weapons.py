"""
Weapon data and logic for Duel-Strike.
"""
from src.constants import (
    BULLET_DAMAGE, MAX_AMMO,
    SHOTGUN_PELLETS, SHOTGUN_SPREAD_DEG, SHOTGUN_PELLET_DAMAGE,
    SHOTGUN_PELLET_SPEED, SHOTGUN_MAX_RANGE, SHOTGUN_COOLDOWN, SHOTGUN_AMMO,
    BAZOOKA_SPEED, BAZOOKA_DAMAGE, BAZOOKA_SPLASH_DAMAGE, BAZOOKA_SPLASH_RADIUS, BAZOOKA_COOLDOWN, BAZOOKA_AMMO
)

GUN_DATA = {
    "name":          "Pistol",
    "damage":        BULLET_DAMAGE,
    "ammo_capacity": MAX_AMMO,
    "fire_rate":     0.0,
}

KNIFE_DATA = {
    "name":     "Combat Knife",
    "damage":   10,
    "range":    55,
    "cooldown": 0.35,
}

SHOTGUN_DATA = {
    "name":           "Shotgun",
    "pellets":        SHOTGUN_PELLETS,
    "spread_deg":     SHOTGUN_SPREAD_DEG,
    "pellet_damage":  SHOTGUN_PELLET_DAMAGE,
    "pellet_speed":   SHOTGUN_PELLET_SPEED,
    "max_range":      SHOTGUN_MAX_RANGE,
    "cooldown":       SHOTGUN_COOLDOWN,
    "ammo_capacity":  SHOTGUN_AMMO,
}

BAZOOKA_DATA = {
    "name":           "Bazooka",
    "speed":          BAZOOKA_SPEED,
    "damage":         BAZOOKA_DAMAGE,
    "splash_damage":  BAZOOKA_SPLASH_DAMAGE,
    "splash_radius":  BAZOOKA_SPLASH_RADIUS,
    "cooldown":       BAZOOKA_COOLDOWN,
    "ammo_capacity":  BAZOOKA_AMMO,
}
