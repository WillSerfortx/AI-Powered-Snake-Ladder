"""Main Entry Point - Initialize all components and start the game."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from board import Board
from bfs import bfs_shortest_path
from simulate import simulate_games
from ml_models import MLModels
from ai_agent import AIAgent
from game import Game
from gui import GUI
from config import SIMULATION_COUNT


def main():
    print("=" * 50)
    print("  AI-Powered Snake & Ladder")
    print("=" * 50)

    # Step 1: Build the board
    print("\n[1/5] Building board graph...")
    board = Board()
    print(f"  Board created with {len(board.snakes)} snakes and {len(board.ladders)} ladders")

    # Step 2: Run BFS
    print("\n[2/5] Running BFS (shortest paths)...")
    bfs_table = bfs_shortest_path(board)
    print(f"  BFS complete. Min rolls from cell 1: {bfs_table.get(1, '?')}")

    # Step 3: Simulate games
    print(f"\n[3/5] Simulating {SIMULATION_COUNT} games...")
    training_data = simulate_games(board, num_games=SIMULATION_COUNT)

    # Step 4: Train ML models (K-Means + Logistic Regression)
    print("\n[4/5] Training ML models...")
    ml_models = MLModels()
    ml_models.train_all(training_data, board)

    # Step 5: Initialize game
    print("\n[5/5] Starting game...")
    game = Game(board)
    ai_agent = AIAgent(board, ml_models, bfs_table)
    game.ai_agent = ai_agent

    gui = GUI(game, board, ml_models, bfs_table)
    gui.game.ai_agent = ai_agent

    print("\n" + "=" * 50)
    print("  Game Ready! Launching window...")
    print("  Controls:")
    print("    SPACE = Roll dice")
    print("    1/2   = Choose dice value")
    print("    H     = Toggle heatmap")
    print("    R     = Restart (when game over)")
    print("=" * 50 + "\n")

    result = gui.run()

    if result == 'restart':
        main()


if __name__ == "__main__":
    main()