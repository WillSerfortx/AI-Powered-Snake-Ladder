"""Game Logic - Manages turns, dice, shields, and win condition."""
import random
from config import BOARD_SIZE, SHIELDS_PER_PLAYER
from board import Board


class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.position = 0
        self.is_ai = is_ai
        self.shields = SHIELDS_PER_PLAYER
        self.moves_history = []

    def __str__(self):
        return self.name


class Game:
    def __init__(self, board, ai_agent=None):
        self.board = board
        self.ai_agent = ai_agent
        self.players = [
            Player("Human", is_ai=False),
            Player("AI", is_ai=True)
        ]
        self.current_player_idx = 0
        self.winner = None
        self.game_over = False
        self.last_dice_options = (0, 0)
        self.last_message = "Game started! Roll the dice."
        self.turn_count = 0

    @property
    def current_player(self):
        return self.players[self.current_player_idx]

    def roll_dice(self):
        """Roll two dice values for the player to choose from."""
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        self.last_dice_options = (dice1, dice2)
        return dice1, dice2

    def make_move(self, player, dice_value):
        """Move a player by the chosen dice value."""
        # Event types: 'normal', 'snake', 'ladder', 'win', 'blocked'
        result = {
            'player': player.name,
            'from': player.position,
            'dice': dice_value,
            'to': 0,
            'event': 'normal',
            'shield_used': False
        }

        new_pos = player.position + dice_value

        if new_pos > BOARD_SIZE:
            result['to'] = player.position
            result['event'] = 'blocked'
            self.last_message = f"{player.name} rolled {dice_value} but can't move (would exceed 100)"
            return result

        if new_pos == BOARD_SIZE:
            player.position = BOARD_SIZE
            result['to'] = BOARD_SIZE
            result['event'] = 'win'
            self.winner = player
            self.game_over = True
            self.last_message = f"{player.name} reached 100 and WINS!"
            return result

        if self.board.is_snake(new_pos):
            snake_dest = self.board.snakes[new_pos]

            if not player.is_ai and player.shields > 0:
                result['event'] = 'ask_shield'
                result['snake_dest'] = snake_dest
                result['to'] = new_pos
                self.last_message = f"Snake at {new_pos}! Use shield? (Y/N)"
                return result

            use_shield = False
            if player.shields > 0:
                if player.is_ai and self.ai_agent:
                    use_shield = self.ai_agent.should_use_shield(new_pos)

            if use_shield:
                player.shields -= 1
                player.position = new_pos
                result['to'] = new_pos
                result['event'] = 'snake'
                result['shield_used'] = True
                self.last_message = f"{player.name} used a shield to block the snake at {new_pos}!"
            else:
                player.position = snake_dest
                result['to'] = snake_dest
                result['event'] = 'snake'
                self.last_message = f"{player.name} hit a snake at {new_pos}! Slid down to {snake_dest}"

        elif self.board.is_ladder(new_pos):
            ladder_dest = self.board.ladders[new_pos]
            if ladder_dest >= BOARD_SIZE:
                player.position = BOARD_SIZE
                result['to'] = BOARD_SIZE
                result['event'] = 'win'
                self.winner = player
                self.game_over = True
                self.last_message = f"{player.name} climbed a ladder to 100 and WINS!"
            else:
                player.position = ladder_dest
                result['to'] = ladder_dest
                result['event'] = 'ladder'
                self.last_message = f"{player.name} found a ladder at {new_pos}! Climbed to {ladder_dest}"

        else:
            player.position = new_pos
            result['to'] = new_pos
            result['event'] = 'normal'
            self.last_message = f"{player.name} moved to {new_pos}"

        player.moves_history.append(result)
        return result

    def resolve_shield(self, player, use_shield, snake_head, snake_dest):
        """Resolve a pending shield decision for a human player."""
        result = {
            'player': player.name,
            'from': player.position,
            'dice': 0,
            'to': snake_head,
            'event': 'snake',
            'shield_used': use_shield
        }

        if use_shield:
            player.shields -= 1
            player.position = snake_head
            self.last_message = f"{player.name} used a shield to block the snake at {snake_head}!"
        else:
            player.position = snake_dest
            result['to'] = snake_dest
            self.last_message = f"{player.name} slid down to {snake_dest}"

        player.moves_history.append(result)
        return result

    def play_ai_turn(self):
        """Execute the AI player's turn automatically."""
        ai = self.players[1]
        dice1, dice2 = self.roll_dice()

        if self.ai_agent:
            chosen = self.ai_agent.choose_dice(ai.position, (dice1, dice2))
        else:
            chosen = random.choice([dice1, dice2])

        result = self.make_move(ai, chosen)
        return result

    def next_turn(self):
        """Switch to the next player."""
        self.current_player_idx = 1 - self.current_player_idx
        self.turn_count += 1