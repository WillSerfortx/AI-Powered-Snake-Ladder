"""A* Search - Find optimal path considering snake penalties and ladder bonuses."""
import heapq
from config import BOARD_SIZE


def heuristic(cell):
    """Admissible heuristic: h(n) = (100 - n) / 6"""
    return (BOARD_SIZE - cell) / 6


def astar_search(board, start):
    """Find optimal path from start to cell 100 using A* search."""
    if start >= BOARD_SIZE:
        return 0, [BOARD_SIZE]

    open_set = []
    f_start = 0 + heuristic(start)
    heapq.heappush(open_set, (f_start, 0, start, [start]))
    best_g = {start: 0}

    while open_set:
        f_cost, g_cost, current, path = heapq.heappop(open_set)

        if current == BOARD_SIZE:
            return g_cost, path

        if g_cost > best_g.get(current, float('inf')):
            continue

        for dice in range(1, 7):
            next_cell_raw = current + dice
            if next_cell_raw > BOARD_SIZE:
                continue

            edge_cost = 1.0

            if next_cell_raw in board.snakes:
                edge_cost += 2.0
                next_cell = board.snakes[next_cell_raw]
            elif next_cell_raw in board.ladders:
                edge_cost = max(0.3, edge_cost - 0.5)
                next_cell = board.ladders[next_cell_raw]
            else:
                next_cell = next_cell_raw

            new_g = g_cost + edge_cost

            if new_g < best_g.get(next_cell, float('inf')):
                best_g[next_cell] = new_g
                f = new_g + heuristic(next_cell)
                heapq.heappush(open_set, (f, new_g, next_cell, path + [next_cell]))

    return float('inf'), []


def evaluate_move(board, current_cell, dice_value):
    """Evaluate a specific dice choice using A*."""
    next_cell = current_cell + dice_value
    if next_cell > BOARD_SIZE:
        return float('inf')
    if next_cell == BOARD_SIZE:
        return 0

    next_cell = board.get_final_position(next_cell)
    cost, _ = astar_search(board, next_cell)
    return cost