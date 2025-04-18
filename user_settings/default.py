# settings.py
import math

# --- Screen/Layout Settings ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
FPS = 60

# --- Map Settings ---
CORRIDOR_WIDTH = 4
MAP_WIDTH = 25  # Odd number preferred
MAP_HEIGHT = 25  # Odd number preferred

# --- Visualization Scaling ---
VIEW_SCALE = 28  # Pixels per map cell for rendering the map

# --- Player Settings ---
PLAYER_FOV = math.radians(65)
PLAYER_MOVE_SPEED = 3.0  # Cells per second
PLAYER_ROT_SPEED = math.radians(120)  # Radians per second
PLAYER_RADIUS = 0.21  # relative to a map cell, for collision

# --- Raycasting Settings ---
NUM_RAYS = 45  # Number of rays within FOV
RAY_MAX_DISTANCE = 16.0  # Cells
RAY_STEP_SIZE = 0.02  # Cells

# --- Sprite/Object Settings ---
SPRITE_RADIUS = 0.18  # Map cells

# --- NPC (Fake Player) Settings ---
FAKE_PLAYER_SPEED = 2.0  # Cells per second
FAKE_PLAYER_RADIUS = 0.19

# --- Colors ---
COLOR_BG = (40, 40, 40)
COLOR_GRID = (64, 64, 64)
COLOR_WALL = (28, 25, 54)
COLOR_FLOOR = (82, 82, 96)

COLOR_PLAYER = (255, 240, 80)
COLOR_PLAYER_DIR = (200, 170, 50)
COLOR_RAY = (53, 167, 244)
COLOR_RAY_HIT = (255, 80, 80)
COLOR_STATIC_SPRITE = (122, 255, 110)
COLOR_FAKE_PLAYER = (246, 144, 255)
COLOR_NPC_DIR = (200, 90, 200)

# --- Font Settings ---
FONT_NAME = "consolas"
FONT_SIZE = 20