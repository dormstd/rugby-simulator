# constants.py
import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (50, 50, 200)
RED = (200, 50, 50)
GREEN = (0, 150, 0)  # Pitch color
DARK_GREEN = (0, 100, 0)  # Pitch border/details
YELLOW = (255, 255, 0)  # Ball color

# Fonts
pygame.font.init()  # Initialize font module
FONT_DEFAULT_SIZE = 24
FONT_SMALL_SIZE = 18
FONT_TINY_SIZE = 14
FONT_DEFAULT = pygame.font.Font(None, FONT_DEFAULT_SIZE)
FONT_SMALL = pygame.font.Font(None, FONT_SMALL_SIZE)
FONT_TINY = pygame.font.Font(None, FONT_TINY_SIZE)

# --- Game Settings ---
POINTS_FOR_WIN = 4
POINTS_FOR_DRAW = 2
POINTS_FOR_LOSS = 0
TRY_POINTS = 5
CONVERSION_POINTS = 2
PENALTY_POINTS = 3  # Added constant

# --- View States ---
VIEW_LEAGUE = "league"
VIEW_PLAYERS = "players"
VIEW_MATCH = "match"  # New view state

# Button dimensions
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40

# --- Match Simulation Settings ---
PITCH_RECT = pygame.Rect(100, 80, 600, SCREEN_HEIGHT - 160)
BALL_RADIUS = 5
PLAYER_RADIUS = 8
MATCH_DURATION_STEPS = 80
SIMULATION_SPEED_MS = 150  # Faster speed to make movement more apparent

# Simulation probabilities (TUNE THESE)
# BASE_MOVE_CHANCE # (Less relevant now, movement is more deterministic)
RATING_INFLUENCE = 0.005  # Keep for stat influence?
BASE_TURNOVER_CHANCE = 0.03  # Lower base chance, more dependent on tackles
BASE_PENALTY_CHANCE = 0.02  # Lower base chance
CONVERSION_SUCCESS_RATE = 0.70
PENALTY_SUCCESS_RATE = 0.75

# --- NEW Movement & Interaction Constants ---
PLAYER_DEFAULT_SPEED = 2.0  # Base pixels moved per step
PLAYER_SPEED_VARIATION = 1.0  # Max extra speed based on rating
BALL_SPEED_FACTOR = 1.2  # How much faster the carrier might be perceived
SUPPORT_DISTANCE = 50  # Ideal distance for support players
DEFENSE_AGGRESSION_RADIUS = (
    150  # How close defenders need to be to actively pursue carrier
)
TACKLE_RADIUS = PLAYER_RADIUS * 2.5  # Distance for a tackle attempt
TACKLE_SUCCESS_BASE = 0.40  # Base chance of successful tackle if ratings equal
TACKLE_STRENGTH_INFLUENCE = 0.01  # How much strength diff affects tackle success
TACKLE_SPEED_INFLUENCE = (
    0.005  # How much speed diff affects tackle success (defender speed helps)
)
