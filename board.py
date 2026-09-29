"""Board representation as a directed graph."""
from config import *


class Board:
    def __init__(self):
        self.snakes = SNAKES
        self.ladders = LADDERS
        self.graph = {}
        self._build_graph()

    def _build_graph(self):
        """Build adjacency list. For each cell 1-100, add edges for dice values 1-6."""
        for cell in range(1, BOARD_SIZE + 1):
            self.graph[cell] = []
            for dice in range(1, 7):
                next_cell = cell + dice
                if next_cell <= BOARD_SIZE:
                    next_cell = self.get_final_position(next_cell)
                    self.graph[cell].append(next_cell)

    def get_final_position(self, cell):
        """Apply snake or ladder if present at the cell."""
        if cell in self.snakes:
            return self.snakes[cell]
        elif cell in self.ladders:
            return self.ladders[cell]
        return cell

    def get_cell_features(self, cell):
        """Extract features for a cell for ML models.
        Returns: [dist_to_nearest_snake, dist_to_nearest_ladder,
                  snakes_within_6, ladders_within_6, position_pct]
        """
        snake_heads = [s for s in self.snakes.keys() if s > cell]
        dist_snake = min([s - cell for s in snake_heads]) if snake_heads else 100

        ladder_bottoms = [l for l in self.ladders.keys() if l > cell]
        dist_ladder = min([l - cell for l in ladder_bottoms]) if ladder_bottoms else 100

        snakes_ahead = sum(1 for s in snake_heads if 0 < s - cell <= 6)
        ladders_ahead = sum(1 for l in ladder_bottoms if 0 < l - cell <= 6)
        position_pct = cell / BOARD_SIZE

        return [dist_snake, dist_ladder, snakes_ahead, ladders_ahead, position_pct]

    def get_all_features(self):
        """Get features for all 100 cells. Returns list of [cell, features...]."""
        all_features = []
        for cell in range(1, BOARD_SIZE + 1):
            features = self.get_cell_features(cell)
            all_features.append([cell] + features)
        return all_features

    def cell_to_row_col(self, cell):
        """Convert cell number (1-100) to (row, col) for display."""
        cell_idx = cell - 1
        row = cell_idx // COLS
        col = cell_idx % COLS
        if row % 2 == 1:
            col = COLS - 1 - col
        return (ROWS - 1 - row, col)

    def is_snake(self, cell):
        return cell in self.snakes

    def is_ladder(self, cell):
        return cell in self.ladders