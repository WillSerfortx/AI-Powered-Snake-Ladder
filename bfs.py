"""BFS - Find minimum dice rolls from any cell to cell 100."""
from collections import deque
from config import BOARD_SIZE


def bfs_shortest_path(board):
    """Calculate minimum dice rolls from every cell to cell 100."""
    min_rolls = {}

    for start in range(1, BOARD_SIZE + 1):
        if start == BOARD_SIZE:
            min_rolls[start] = 0
            continue

        visited = set()
        queue = deque([(start, 0)])
        visited.add(start)
        found = False

        while queue and not found:
            current, dist = queue.popleft()

            for dice in range(1, 7):
                next_cell = current + dice
                if next_cell > BOARD_SIZE:
                    continue

                next_cell = board.get_final_position(next_cell)

                if next_cell == BOARD_SIZE:
                    min_rolls[start] = dist + 1
                    found = True
                    break

                if next_cell not in visited:
                    visited.add(next_cell)
                    queue.append((next_cell, dist + 1))

        if not found:
            min_rolls[start] = -1

    return min_rolls


def bfs_from_cell(board, start):
    """Run BFS from a specific cell and return the shortest path to 100."""
    if start == BOARD_SIZE:
        return 0, [BOARD_SIZE]

    visited = set()
    queue = deque([(start, [start])])
    visited.add(start)

    while queue:
        current, path = queue.popleft()

        for dice in range(1, 7):
            next_cell = current + dice
            if next_cell > BOARD_SIZE:
                continue

            next_cell = board.get_final_position(next_cell)

            if next_cell == BOARD_SIZE:
                return len(path), path + [BOARD_SIZE]

            if next_cell not in visited:
                visited.add(next_cell)
                queue.append((next_cell, path + [next_cell]))

    return -1, []