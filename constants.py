# constants.py
import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)  # For button hover/click later?
BLUE = (50, 50, 200)
RED = (200, 50, 50)

# Fonts
pygame.font.init()  # Initialize font module
FONT_DEFAULT_SIZE = 24
FONT_SMALL_SIZE = 18
FONT_TINY_SIZE = 14  # For player attributes if needed
FONT_DEFAULT = pygame.font.Font(None, FONT_DEFAULT_SIZE)  # Use default system font
FONT_SMALL = pygame.font.Font(None, FONT_SMALL_SIZE)
FONT_TINY = pygame.font.Font(None, FONT_TINY_SIZE)

# Game settings
POINTS_FOR_WIN = 4
POINTS_FOR_DRAW = 2
POINTS_FOR_LOSS = 0

TRY_POINTS = 5
CONVERSION_POINTS = 2

# View States
VIEW_LEAGUE = "league"
VIEW_PLAYERS = "players"

# Button dimensions (optional, but good practice)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
