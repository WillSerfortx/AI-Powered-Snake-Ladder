# Board
BOARD_SIZE = 100
ROWS = 10
COLS = 10

# Snakes: {head: tail}
SNAKES = {
    16: 6, 47: 26, 49: 11, 56: 53,
    62: 19, 64: 60, 87: 24, 93: 73,
    95: 75, 98: 78
}

# Ladders: {bottom: top}
LADDERS = {
    1: 38, 4: 14, 9: 31, 21: 42,
    28: 84, 36: 44, 51: 67, 71: 91,
    80: 100
}

# Pygame UI
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
BOARD_SIZE_PX = 600
CELL_SIZE = BOARD_SIZE_PX // 10
STATS_PANEL_WIDTH = 300

# Colors
BG_COLOR = (255, 248, 240)       # Cream #FFF8F0
PRIMARY = (45, 106, 79)          # Deep green #2D6A4F
SECONDARY = (231, 111, 81)       # Warm orange #E76F51
TEXT_COLOR = (61, 44, 46)        # Dark brown #3D2C2E
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 180, 80)
YELLOW = (240, 200, 50)
BLUE = (50, 100, 220)

# Heatmap colors for K-Means zones
ZONE_COLORS = {
    'danger': (255, 100, 100, 120),
    'neutral': (255, 230, 100, 120),
    'advantage': (100, 220, 100, 120),
}

# AI Weights (A* + Logistic Regression only)
WEIGHT_ASTAR = 0.6
WEIGHT_LR = 0.4

# ML Config
KMEANS_CLUSTERS = 3
SIMULATION_COUNT = 10000

# Game
SHIELDS_PER_PLAYER = 2