"""AI Agent - Combines A* and Logistic Regression for decision making (No KNN)."""
from config import WEIGHT_ASTAR, WEIGHT_LR, BOARD_SIZE
from astar import evaluate_move


class AIAgent:
    def __init__(self, board, ml_models, bfs_table):
        self.board = board
        self.models = ml_models
        self.bfs_table = bfs_table
        self.last_decision = {}

    def choose_dice(self, current_pos, dice_options):
        """Choose the best dice value from two options.
        Formula: Score = 0.6 * A* + 0.4 * Logistic Regression
        """
        scores = {}
        details = {}

        for dice in dice_options:
            dest = current_pos + dice

            if dest > BOARD_SIZE:
                scores[dice] = -1
                details[dice] = {'valid': False}
                continue

            if dest == BOARD_SIZE:
                scores[dice] = 999
                details[dice] = {'valid': True, 'win': True}
                continue

            dest = self.board.get_final_position(dest)

            # 1. A* Score (lower cost = better, invert and normalize)
            astar_cost = evaluate_move(self.board, current_pos, dice)
            max_cost = 20.0
            astar_score = max(0, 1 - (astar_cost / max_cost))

            # 2. Logistic Regression Win Probability
            lr_score = self.models.predict_win_probability(dest, self.board)

            # Weighted combination (A* + LR only)
            final_score = (
                WEIGHT_ASTAR * astar_score +
                WEIGHT_LR * lr_score
            )

            scores[dice] = final_score
            details[dice] = {
                'valid': True,
                'win': False,
                'destination': dest,
                'astar_score': round(astar_score, 3),
                'lr_score': round(lr_score, 3),
                'final_score': round(final_score, 3)
            }

        best_dice = max(scores, key=scores.get)

        self.last_decision = {
            'dice_options': dice_options,
            'chosen': best_dice,
            'details': details
        }

        return best_dice

    def should_use_shield(self, cell):
        """Decide whether to use shield using K-Means zone info."""
        current_zone = self.models.get_kmeans_zone(cell)
        snake_drop = cell - self.board.snakes.get(cell, cell)

        if snake_drop > 30:
            return True
        if current_zone == 'danger' and snake_drop > 15:
            return True

        return False
