"""Simulate random Snake & Ladder games to generate training data."""
import random
from config import BOARD_SIZE, SIMULATION_COUNT
from board import Board


def simulate_single_game(board, feature_cache):
    """Simulate one game between two random players."""
    positions = [0, 0]
    history = [[], []]
    winner = -1

    while True:
        for player in [0, 1]:
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            
            best_new_pos = positions[player]
            for d in (dice1, dice2):
                p = positions[player] + d
                if p <= BOARD_SIZE:
                    final_p = board.get_final_position(p)
                    if final_p > best_new_pos:
                        best_new_pos = final_p
            
            if best_new_pos == positions[player]:
                continue
                
            new_pos = best_new_pos
            positions[player] = new_pos
            history[player].append(new_pos)

            if new_pos == BOARD_SIZE:
                winner = player
                break

        if winner != -1:
            break

    training_data = []
    for player in [0, 1]:
        won = 1 if player == winner else 0
        for cell in history[player]:
            features = feature_cache.get(cell, [0, 0, 0, 0, cell / BOARD_SIZE])
            training_data.append(features + [won])

    return training_data


def simulate_games(board, num_games=SIMULATION_COUNT):
    """Simulate many games and collect all training data."""
    print("  Precomputing cell features...")
    feature_cache = {}
    for cell in range(1, BOARD_SIZE + 1):
        feature_cache[cell] = board.get_cell_features(cell)

    all_data = []
    for i in range(num_games):
        game_data = simulate_single_game(board, feature_cache)
        all_data.extend(game_data)

        if (i + 1) % 2000 == 0:
            print(f"  Simulated {i + 1}/{num_games} games...")

    print(f"  Total training samples: {len(all_data)}")
    return all_data


if __name__ == "__main__":
    board = Board()
    data = simulate_games(board, num_games=1000)
    print(f"Generated {len(data)} training samples")
    print(f"Sample: {data[0]}")