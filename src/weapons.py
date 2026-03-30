# src/weapons.py — Stats and data for every weapon in the game.
# Each dict defines the properties of a weapon. Actual numbers come from constants.py.

from src.constants import (
    BULLET_DAMAGE, MAX_AMMO,
    SHOTGUN_PELLETS, SHOTGUN_SPREAD_DEG, SHOTGUN_PELLET_DAMAGE,
    SHOTGUN_PELLET_SPEED, SHOTGUN_MAX_RANGE, SHOTGUN_COOLDOWN, SHOTGUN_AMMO,
    BAZOOKA_SPEED, BAZOOKA_DAMAGE, BAZOOKA_SPLASH_DAMAGE, BAZOOKA_SPLASH_RADIUS, BAZOOKA_COOLDOWN, BAZOOKA_AMMO
)

# Default pistol — unlimited fire rate, standard damage per bullet
GUN_DATA = {
    "name":          "Pistol",
    "damage":        BULLET_DAMAGE,
    "ammo_capacity": MAX_AMMO,
    "fire_rate":     0.0,
}

# Melee weapon — short range but does decent damage with a quick cooldown
KNIFE_DATA = {
    "name":     "Combat Knife",
    "damage":   10,
    "range":    55,
    "cooldown": 0.35,
}

# Shotgun — fires multiple pellets in a spread pattern, picked up from loot box
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

# Bazooka — fires a slow rocket that explodes on impact with splash damage
BAZOOKA_DATA = {
    "name":           "Bazooka",
    "speed":          BAZOOKA_SPEED,
    "damage":         BAZOOKA_DAMAGE,
    "splash_damage":  BAZOOKA_SPLASH_DAMAGE,
    "splash_radius":  BAZOOKA_SPLASH_RADIUS,
    "cooldown":       BAZOOKA_COOLDOWN,
    "ammo_capacity":  BAZOOKA_AMMO,
}
