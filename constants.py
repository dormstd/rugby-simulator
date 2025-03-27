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
GREEN = (0, 150, 0)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)

# Fonts
pygame.font.init() # Initialize font module
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
PENALTY_POINTS = 3

# --- View States ---
VIEW_LEAGUE = "league"
VIEW_PLAYERS = "players"
VIEW_MATCH = "match"

# Button dimensions
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40

# --- Match Simulation Settings ---
PITCH_RECT = pygame.Rect(100, 80, 600, SCREEN_HEIGHT - 160)
BALL_RADIUS = 5
PLAYER_RADIUS = 8

# Time/Step Settings
GAME_DURATION_MINUTES = 80
MATCH_DURATION_STEPS = 80 * 4 # 320 steps
SIMULATION_SPEED_MS = 100 # ms per step (Adjust for real-time speed)

# Event Probabilities (Adjusted for more steps)
BASE_TURNOVER_CHANCE = 0.01
BASE_PENALTY_CHANCE = 0.008
CONVERSION_SUCCESS_RATE = 0.70
PENALTY_SUCCESS_RATE = 0.75

# Movement & Interaction
PLAYER_DEFAULT_SPEED = 1.5
PLAYER_SPEED_VARIATION = 0.8
BALL_SPEED_FACTOR = 1.2
SUPPORT_DISTANCE = 45 # How far behind/wide support aims for
DEFENSE_AGGRESSION_RADIUS = 180 # Increased slightly?
TACKLE_RADIUS = PLAYER_RADIUS * 2.5
TACKLE_SUCCESS_BASE = 0.40
TACKLE_STRENGTH_INFLUENCE = 0.01
TACKLE_SPEED_INFLUENCE = 0.005

# --- NEW/ADJUSTED Formation/Positioning Constants ---
ATTACKING_SUPPORT_WIDTH = 35    # How wide support players try to spread
DEFENSIVE_LINE_Y_OFFSET = 20    # How far 'ahead' (towards attacker goal) def line tries to sit
DEFENSIVE_LINE_SPACING = 40   # Horizontal space between defenders in the line
SWEEPER_DEPTH_OFFSET = 60     # How far behind the main line the sweeper sits

# Passing Constants
PASS_PRESSURE_RADIUS = TACKLE_RADIUS * 2.0
BASE_PASS_CHANCE = 0.02
PASS_PRESSURE_BONUS = 0.08
PASS_MAX_DISTANCE = 100
PASS_Y_TOLERANCE = 5
PASS_SUCCESS_BASE = 0.85
PASS_ACCURACY_INFLUENCE = 0.008
PASS_DISTANCE_PENALTY = 0.003
PASS_INTERCEPTION_BASE_CHANCE = 0.01
PASS_INTERCEPTION_RADIUS = 35