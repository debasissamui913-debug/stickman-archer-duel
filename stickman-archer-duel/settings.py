import os
from enum import Enum, auto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
DATA_DIR = os.path.join(BASE_DIR, "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GAME_TITLE = "Archer Duel"
FPS = 60


COLOR_SKY = (128, 200, 155)          
COLOR_GROUND_LINE = (30, 90, 55)
COLOR_BLACK = (20, 20, 20)
COLOR_WHITE = (255, 255, 255)
COLOR_ACCENT = (219, 172, 89)
COLOR_COIN = (240, 190, 60)
COLOR_HEADSHOT = (255, 210, 60)
COLOR_BLOCKED = (140, 150, 160)
COLOR_MISS = (200, 200, 200)
COLOR_HEALTH_GOOD = (86, 196, 110)
COLOR_HEALTH_LOW = (214, 69, 69)
COLOR_BUTTON = (52, 58, 72)
COLOR_BUTTON_HOVER = (219, 172, 89)
COLOR_OVERLAY = (10, 12, 16, 180)
COLOR_TEXT_DIM = (60, 80, 65)


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    LEVEL_COMPLETE = auto()
    LEVEL_FAILED = auto()
    SHOP = auto()
    SETTINGS = auto()
    HOW_TO_PLAY = auto()


GRAVITY = 950.0                
GROUND_Y = SCREEN_HEIGHT - 140
DRAG_MAX_LENGTH = 170           
POWER_MIN_SPEED = 260
POWER_MAX_SPEED = 980
ARROW_RADIUS = 5
ARROW_TRAIL_LENGTH = 14

PLAYER_X = 160
HEAD_RADIUS = 13
BODY_HIT_RADIUS = 24           
HEAD_OFFSET = 78                
BODY_CENTER_OFFSET = 45         

BASE_OPPONENT_DISTANCE = 420      
DISTANCE_INCREMENT = 35          
MAX_OPPONENT_X = SCREEN_WIDTH - 160   
WIND_START_DISTANCE = MAX_OPPONENT_X - PLAYER_X   
WIND_MAX_FORCE = 220              
WIND_LEVEL_RAMP = 25              
ARROWS_PER_LEVEL = 3


PLAYER_MAX_HP = 100
OPPONENT_MAX_HP = 100
DAMAGE_BODY = 25
DAMAGE_HEAD = 50



ENEMY_ACCURACY_ERROR_START = 18.0   
ENEMY_ACCURACY_ERROR_MIN = 5.0      
ENEMY_ACCURACY_LEVEL_STEP = 0.7     
ENEMY_SHOT_BASE_ANGLE = 42.0        
ENEMY_TURN_DELAY = 0.6              


ENEMY_DAMAGE_RAMP_PER_LEVEL = 0.0
ENEMY_DAMAGE_RAMP_CAP = 1.0

COIN_PER_HIT = 2
COIN_LEVEL_WIN = 8                  

SHIELD_HEAD_GUARD_CHANCE = 0.35     

BOSS_LEVEL_INTERVAL = 0              
BOSS_HP_MULTIPLIER = 2.0
BOSS_DOUBLE_SHOT = True
BOSS_COIN_MULTIPLIER = 3

PLAYER_TURN_TIME_LIMIT = 8.0        
PLAYER_TURN_WARNING_TIME = 2.5     

STREAK_COIN_BONUS_PER_WIN = 0
STREAK_MAX_BONUS = 0

SHIELD_UP_DURATION = 1.5
SHIELD_UP_DURATION_MAX = 1.5         
SHIELD_DOWN_DURATION = 1.7
SHIELD_DOWN_DURATION_MIN = 1.7       
SHIELD_LEVEL_RAMP = 20
SHIELD_WARNING_TIME = 0.35        

COIN_BASE_REWARD = 10
COIN_HEADSHOT_BONUS = 15
COIN_PER_ARROW_SAVED = 5          


SHOP_ITEMS = [
    {"id": "classic",   "name": "Classic",     "cost": 0,   "bow_color": (60, 40, 20),  "arrow_color": (235, 235, 235)},
    {"id": "crimson",   "name": "Crimson",     "cost": 60,  "bow_color": (120, 20, 20), "arrow_color": (230, 70, 70)},
    {"id": "azure",     "name": "Azure",       "cost": 60,  "bow_color": (20, 50, 110), "arrow_color": (90, 170, 240)},
    {"id": "emerald",   "name": "Emerald",     "cost": 90,  "bow_color": (20, 90, 45),  "arrow_color": (80, 220, 130)},
    {"id": "gold",      "name": "Golden",      "cost": 150, "bow_color": (150, 120, 20),"arrow_color": (255, 210, 60)},
    {"id": "shadow",    "name": "Shadow",      "cost": 200, "bow_color": (25, 25, 30),  "arrow_color": (120, 60, 200)},
    {"id": "godly",     "name": "Godly",       "cost": 0,   "bow_color": (255, 220, 100), "arrow_color": (110, 245, 255), "code_required": True},
]
DEFAULT_SKIN_ID = "classic"

SHIELD_ITEMS = [
    {"id": "guardian_shield", "name": "Guardian Shield", "cost": 35, "color": (110, 220, 245)},
]


PLAYER_COLOR_ITEMS = [
    {"id": "black",  "name": "Classic Black", "cost": 0,   "color": (20, 20, 20)},
    {"id": "navy",   "name": "Navy",          "cost": 50,  "color": (30, 45, 90)},
    {"id": "crimson_body", "name": "Crimson", "cost": 80,  "color": (110, 25, 30)},
    {"id": "forest", "name": "Forest",        "cost": 80,  "color": (25, 70, 35)},
    {"id": "royal",  "name": "Royal Purple",  "cost": 120, "color": (70, 30, 110)},
    {"id": "golden_body", "name": "Golden",   "cost": 180, "color": (150, 115, 20)},
]
DEFAULT_PLAYER_COLOR_ID = "black"


BACKGROUND_THEMES = [
    {
        "id": "meadow", "name": "Meadow", "cost": 0,
        "sky_top": (140, 205, 235), "sky_bottom": (196, 230, 205),
        "hill_far": (150, 205, 165), "hill_near": (120, 185, 140),
        "ground_top": (128, 200, 155), "ground_bottom": (95, 165, 115),
    },
    {
        "id": "sunset", "name": "Sunset", "cost": 100,
        "sky_top": (255, 170, 120), "sky_bottom": (255, 210, 160),
        "hill_far": (210, 130, 110), "hill_near": (170, 90, 90),
        "ground_top": (200, 140, 100), "ground_bottom": (150, 95, 70),
    },
    {
        "id": "dusk", "name": "Dusk", "cost": 140,
        "sky_top": (70, 60, 110), "sky_bottom": (140, 110, 150),
        "hill_far": (80, 70, 110), "hill_near": (55, 48, 85),
        "ground_top": (90, 80, 110), "ground_bottom": (55, 50, 75),
    },
    {
        "id": "snow", "name": "Snowfield", "cost": 160,
        "sky_top": (200, 220, 235), "sky_bottom": (230, 240, 245),
        "hill_far": (220, 230, 235), "hill_near": (200, 215, 225),
        "ground_top": (235, 240, 245), "ground_bottom": (205, 215, 220),
    },
]
DEFAULT_BACKGROUND_ID = "meadow"

DEFAULT_PLAYER_NAME = "Player"
DEFAULT_OPPONENT_NAME = "Rival"


SOUND_ENABLED_DEFAULT = True
SOUND_VOLUME_DEFAULT = 0.7

SOUND_FILES = {
    "bow_shoot": "bow_shoot.wav",
    "arrow_hit": "arrow_hit.wav",
    "headshot": "headshot.wav",
    "blocked": "blocked.wav",
    "miss": "miss.wav",
    "coin_collect": "coin_collect.wav",
    "button_click": "button_click.wav",
    "level_complete": "level_complete.wav",
    "level_failed": "level_failed.wav",
    "purchase": "purchase.wav",
}
