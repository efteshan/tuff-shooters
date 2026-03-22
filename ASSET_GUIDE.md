# How to Add Game Assets (Images)

## Adding a Barrel Image

### Step 1: Find or Create a Barrel Image
You can get free game assets from these websites:
- **OpenGameArt.org** - https://opengameart.org/
- **Kenney.nl** - https://kenney.nl/assets (highly recommended for 2D game assets)
- **itch.io** - https://itch.io/game-assets/free

### Step 2: Download Your Barrel Image
1. Find a barrel sprite image (PNG format recommended)
2. The image should be approximately 40x60 pixels (or any size, it will be scaled)
3. Make sure it has a transparent background (PNG)

### Step 3: Add the Image to Your Game
1. Save your barrel image as: `assets/sprites/barrel.png`
2. The game will automatically load it next time you run it!

## Current Asset Locations

The game looks for images in these locations:

### Player Sprites
- `assets/sprites/p1_head.png` - Player 1 head
- `assets/sprites/p1_torso.png` - Player 1 torso
- `assets/sprites/p1_arm_right.png` - Player 1 right arm
- `assets/sprites/p1_arm_left.png` - Player 1 left arm
- `assets/sprites/p1_leg_right.png` - Player 1 right leg
- `assets/sprites/p1_leg_left.png` - Player 1 left leg

(Same for Player 2, replace `p1_` with `p2_`)

### Arena Sprites
- `assets/sprites/barrel.png` - Barrel obstacle (40x60 px recommended)
- `assets/sprites/platform.png` - Platform (200x20 px recommended)
- `assets/sprites/ground_tile.png` - Ground tile (100x80 px recommended)

### Pickup Sprites
- `assets/pickups/health_pack.png` - Health pack (30x30 px recommended)
- `assets/pickups/ammo_box.png` - Ammo box (30x30 px recommended)

### UI Sprites
- `assets/ui/menu_bg.png` - Menu background (1280x720 px)

### Effects
- `assets/effects/blood_strip.png` - Blood particle animation strip
- `assets/effects/ko_strip.png` - K.O. animation strip

## Quick Recommendation

For a quick start, I recommend visiting **Kenney.nl**:
1. Go to https://kenney.nl/assets/platformer-art-deluxe
2. Download the free pack
3. Extract and find barrel/crate images
4. Copy them to your `assets/sprites/` folder
5. Rename to `barrel.png`

## What Happens If You Don't Add Images?

The game works perfectly fine without images! It uses colored placeholder rectangles:
- Barrels = Brown rectangles
- Platforms = Brown rectangles
- Players = Blue/Red colored stick figures
- Pickups = Green/Yellow rectangles

The game is fully playable with or without custom graphics!
