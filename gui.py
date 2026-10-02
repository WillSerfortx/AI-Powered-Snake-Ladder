"""Pygame GUI - Board visualization, heatmap, and game interaction (No KNN)."""
import pygame
import sys
from config import *
from board import Board


class GUI:
    def __init__(self, game, board, ml_models=None, bfs_table=None):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI-Powered Snake & Ladder")
        self.clock = pygame.time.Clock()

        self.game = game
        self.board = board
        self.ml_models = ml_models
        self.bfs_table = bfs_table

        # Fonts
        self.font_small = pygame.font.SysFont('Arial', 14)
        self.font_medium = pygame.font.SysFont('Arial', 18)
        self.font_large = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_title = pygame.font.SysFont('Arial', 28, bold=True)

        # Game state for GUI
        self.show_heatmap = True
        self.dice_options = (0, 0)
        self.state = 'ROLL'  # ROLL, CHOOSE, AI_TURN, ASK_SHIELD, GAME_OVER
        self.ai_turn_timer = 0
        self.pending_shield_data = None

    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.game.game_over:
                        if event.key == pygame.K_r:
                            return 'restart'

                    elif self.state == 'ROLL':
                        if event.key == pygame.K_SPACE:
                            self.dice_options = self.game.roll_dice()
                            self.state = 'CHOOSE'

                    elif self.state == 'CHOOSE':
                        if event.key == pygame.K_1:
                            self._human_move(self.dice_options[0])
                        elif event.key == pygame.K_2:
                            self._human_move(self.dice_options[1])
                            
                    elif self.state == 'ASK_SHIELD':
                        if event.key == pygame.K_y:
                            self._resolve_human_shield(True)
                        elif event.key == pygame.K_n:
                            self._resolve_human_shield(False)

                    if event.key == pygame.K_h:
                        self.show_heatmap = not self.show_heatmap

            # AI turn with delay
            if self.state == 'AI_TURN':
                self.ai_turn_timer += 1
                if self.ai_turn_timer > 60:
                    result = self.game.play_ai_turn()
                    if self.game.game_over:
                        self.state = 'GAME_OVER'
                    else:
                        self.game.next_turn()
                        self.state = 'ROLL'
                    self.ai_turn_timer = 0

            self._draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def _human_move(self, dice_value):
        """Process human player's move."""
        result = self.game.make_move(self.game.players[0], dice_value)
        self._handle_move_result(result)

    def _resolve_human_shield(self, use_shield):
        """Process human player's decision to use a shield."""
        data = self.pending_shield_data
        result = self.game.resolve_shield(
            self.game.players[0], 
            use_shield, 
            data['to'], 
            data['snake_dest']
        )
        self.pending_shield_data = None
        self._handle_move_result(result)

    def _handle_move_result(self, result):
        """Determine next state based on move result."""
        if result.get('event') == 'ask_shield':
            self.state = 'ASK_SHIELD'
            self.pending_shield_data = result
        elif self.game.game_over:
            self.state = 'GAME_OVER'
        else:
            self.game.next_turn()
            self.state = 'AI_TURN'

    def _draw(self):
        """Draw the entire screen."""
        self.screen.fill(BG_COLOR)
        self._draw_board()
        self._draw_snakes_ladders()
        self._draw_players()
        self._draw_stats_panel()
        self._draw_message_bar()

    def _draw_board(self):
        """Draw the 10x10 game board with cell numbers."""
        for cell in range(1, BOARD_SIZE + 1):
            row, col = self.board.cell_to_row_col(cell)
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            # Heatmap coloring using K-Means zones
            if self.show_heatmap and self.ml_models:
                zone = self.ml_models.get_kmeans_zone(cell)
                if zone == 'danger':
                    color = (255, 180, 180)
                elif zone == 'advantage':
                    color = (180, 255, 180)
                else:
                    color = (255, 255, 200)
            else:
                if (row + col) % 2 == 0:
                    color = WHITE
                else:
                    color = (230, 230, 230)

            pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

            # Cell number
            num_text = self.font_small.render(str(cell), True, TEXT_COLOR)
            self.screen.blit(num_text, (x + 3, y + 2))

            # Show win probability if heatmap is on
            if self.show_heatmap and self.ml_models:
                prob = self.ml_models.win_prob_map.get(cell, 0)
                prob_text = self.font_small.render(f"{prob:.0%}", True, (100, 100, 100))
                self.screen.blit(prob_text, (x + 3, y + CELL_SIZE - 16))

    def _draw_snakes_ladders(self):
        """Draw snake and ladder figures on the board."""
        import math

        for head, tail in self.board.snakes.items():
            h_row, h_col = self.board.cell_to_row_col(head)
            t_row, t_col = self.board.cell_to_row_col(tail)

            hx = h_col * CELL_SIZE + CELL_SIZE // 2
            hy = h_row * CELL_SIZE + CELL_SIZE // 2
            tx = t_col * CELL_SIZE + CELL_SIZE // 2
            ty = t_row * CELL_SIZE + CELL_SIZE // 2

            # --- Sinusoidal snake body ---
            dx = tx - hx
            dy = ty - hy
            length = math.hypot(dx, dy)
            if length == 0:
                continue
            nx = -dy / length   # normal x (perpendicular)
            ny = dx / length    # normal y

            num_points = max(40, int(length / 2))
            amplitude = 12
            waves = max(2, int(length / 80))

            snake_color = (200, 50, 50)
            snake_outline = (140, 20, 20)

            points = []
            for i in range(num_points + 1):
                t = i / num_points
                bx = hx + dx * t
                by = hy + dy * t
                offset = math.sin(t * waves * 2 * math.pi) * amplitude
                px = bx + nx * offset
                py = by + ny * offset
                points.append((int(px), int(py)))

            # Draw thicker outline then body on top
            if len(points) > 1:
                pygame.draw.lines(self.screen, snake_outline, False, points, 9)
                pygame.draw.lines(self.screen, snake_color, False, points, 6)

                # Draw diamond pattern along body
                pattern_color = (255, 180, 60)
                for i in range(4, len(points) - 4, 6):
                    pygame.draw.circle(self.screen, pattern_color, points[i], 2)

            # --- Snake head ---
            head_dir_x = dx / length
            head_dir_y = dy / length
            # Head is an elongated shape
            head_size = 10
            head_cx, head_cy = points[0]
            head_pts = [
                (int(head_cx - head_dir_x * head_size - nx * 7),
                 int(head_cy - head_dir_y * head_size - ny * 7)),
                (int(head_cx + head_dir_x * 4),
                 int(head_cy + head_dir_y * 4)),
                (int(head_cx - head_dir_x * head_size + nx * 7),
                 int(head_cy - head_dir_y * head_size + ny * 7)),
            ]
            pygame.draw.polygon(self.screen, snake_outline, head_pts)
            pygame.draw.polygon(self.screen, snake_color, head_pts, 0)

            # Eyes
            eye_offset = 4
            eye1 = (int(head_cx - head_dir_x * 4 + nx * 3),
                     int(head_cy - head_dir_y * 4 + ny * 3))
            eye2 = (int(head_cx - head_dir_x * 4 - nx * 3),
                     int(head_cy - head_dir_y * 4 - ny * 3))
            pygame.draw.circle(self.screen, YELLOW, eye1, 3)
            pygame.draw.circle(self.screen, YELLOW, eye2, 3)
            pygame.draw.circle(self.screen, BLACK, eye1, 1)
            pygame.draw.circle(self.screen, BLACK, eye2, 1)

            # Forked tongue
            tongue_start = (int(head_cx + head_dir_x * 4),
                            int(head_cy + head_dir_y * 4))
            tongue_fork1 = (int(head_cx + head_dir_x * 12 + nx * 3),
                            int(head_cy + head_dir_y * 12 + ny * 3))
            tongue_fork2 = (int(head_cx + head_dir_x * 12 - nx * 3),
                            int(head_cy + head_dir_y * 12 - ny * 3))
            tongue_mid = (int(head_cx + head_dir_x * 9),
                          int(head_cy + head_dir_y * 9))
            pygame.draw.line(self.screen, RED, tongue_start, tongue_mid, 2)
            pygame.draw.line(self.screen, RED, tongue_mid, tongue_fork1, 2)
            pygame.draw.line(self.screen, RED, tongue_mid, tongue_fork2, 2)

            # Tail tip (tapers)
            tail_pt = points[-1]
            pygame.draw.circle(self.screen, snake_color, tail_pt, 3)

        # --- Ladders ---
        for bottom, top in self.board.ladders.items():
            b_row, b_col = self.board.cell_to_row_col(bottom)
            t_row, t_col = self.board.cell_to_row_col(top)

            bx = b_col * CELL_SIZE + CELL_SIZE // 2
            by = b_row * CELL_SIZE + CELL_SIZE // 2
            tx = t_col * CELL_SIZE + CELL_SIZE // 2
            ty = t_row * CELL_SIZE + CELL_SIZE // 2

            dx = tx - bx
            dy = ty - by
            length = math.hypot(dx, dy)
            if length == 0:
                continue
            nx = -dy / length
            ny = dx / length

            rail_gap = 10  # half-width between the two rails

            # Side rails
            rail_color = (139, 90, 43)       # brown wood color
            rail_highlight = (185, 135, 80)  # lighter wood
            rail_width = 4

            r1_start = (int(bx + nx * rail_gap), int(by + ny * rail_gap))
            r1_end   = (int(tx + nx * rail_gap), int(ty + ny * rail_gap))
            r2_start = (int(bx - nx * rail_gap), int(by - ny * rail_gap))
            r2_end   = (int(tx - nx * rail_gap), int(ty - ny * rail_gap))

            pygame.draw.line(self.screen, rail_color, r1_start, r1_end, rail_width + 2)
            pygame.draw.line(self.screen, rail_highlight, r1_start, r1_end, rail_width - 1)
            pygame.draw.line(self.screen, rail_color, r2_start, r2_end, rail_width + 2)
            pygame.draw.line(self.screen, rail_highlight, r2_start, r2_end, rail_width - 1)

            # Rungs
            num_rungs = max(3, int(length / 25))
            rung_color = (160, 110, 60)
            for i in range(num_rungs + 1):
                t = i / num_rungs
                cx = bx + dx * t
                cy = by + dy * t
                p1 = (int(cx + nx * rail_gap), int(cy + ny * rail_gap))
                p2 = (int(cx - nx * rail_gap), int(cy - ny * rail_gap))
                pygame.draw.line(self.screen, rail_color, p1, p2, 3)
                pygame.draw.line(self.screen, rung_color, p1, p2, 2)

    def _draw_players(self):
        """Draw player pieces on the board."""
        for i, player in enumerate(self.game.players):
            if player.position == 0:
                continue

            row, col = self.board.cell_to_row_col(player.position)
            x = col * CELL_SIZE + (15 if i == 0 else 35)
            y = row * CELL_SIZE + 25

            color = BLUE if i == 0 else SECONDARY
            pygame.draw.circle(self.screen, color, (x, y), 10)

            label = self.font_small.render("H" if i == 0 else "AI", True, WHITE)
            self.screen.blit(label, (x - 6, y - 6))

    def _draw_stats_panel(self):
        """Draw the right-side stats panel."""
        panel_x = BOARD_SIZE_PX + 10
        panel_y = 10
        panel_w = STATS_PANEL_WIDTH - 20

        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_w, SCREEN_HEIGHT - 20), border_radius=10)
        pygame.draw.rect(self.screen, PRIMARY, (panel_x, panel_y, panel_w, SCREEN_HEIGHT - 20), 2, border_radius=10)

        x = panel_x + 15
        y = panel_y + 15

        # Title
        title = self.font_large.render("Game Stats", True, PRIMARY)
        self.screen.blit(title, (x, y))
        y += 40

        # Player positions
        for i, player in enumerate(self.game.players):
            color = BLUE if i == 0 else SECONDARY
            text = self.font_medium.render(f"{player.name}: Cell {player.position}", True, color)
            self.screen.blit(text, (x, y))
            y += 25

            shield_text = self.font_small.render(f"  Shields: {player.shields} remaining", True, TEXT_COLOR)
            self.screen.blit(shield_text, (x, y))
            y += 25

        y += 10

        # Turn info
        turn_text = self.font_medium.render(f"Turn: {self.game.turn_count}", True, TEXT_COLOR)
        self.screen.blit(turn_text, (x, y))
        y += 30

        # BFS info
        if self.bfs_table:
            for i, player in enumerate(self.game.players):
                if player.position > 0:
                    rolls = self.bfs_table.get(player.position, '?')
                    bfs_text = self.font_small.render(f"BFS min rolls ({player.name}): {rolls}", True, TEXT_COLOR)
                    self.screen.blit(bfs_text, (x, y))
                    y += 20

        y += 10

        # Current state instructions
        if self.state == 'ROLL':
            inst = self.font_medium.render("Press SPACE to roll", True, PRIMARY)
        elif self.state == 'CHOOSE':
            d1, d2 = self.dice_options
            inst = self.font_medium.render(f"Press 1 for [{d1}] or 2 for [{d2}]", True, SECONDARY)
        elif self.state == 'AI_TURN':
            inst = self.font_medium.render("AI is thinking...", True, SECONDARY)
        elif self.state == 'ASK_SHIELD':
            inst = self.font_medium.render("Press Y for Shield, N to Fall", True, RED)
        elif self.state == 'GAME_OVER':
            inst = self.font_medium.render("GAME OVER! Press R to restart", True, RED)
        else:
            inst = self.font_medium.render("", True, TEXT_COLOR)
        self.screen.blit(inst, (x, y))
        y += 35

        # AI last decision details (A* + LR only)
        if self.game.players[1].position > 0 and hasattr(self.game, 'ai_agent') and self.game.ai_agent:
            agent = self.game.ai_agent
            if agent and agent.last_decision:
                y += 5
                ai_title = self.font_medium.render("AI Decision:", True, SECONDARY)
                self.screen.blit(ai_title, (x, y))
                y += 22

                details = agent.last_decision.get('details', {})
                for dice_val, info in details.items():
                    if isinstance(info, dict) and info.get('valid') and not info.get('win'):
                        chosen = " <<" if dice_val == agent.last_decision.get('chosen') else ""
                        line = f"Dice {dice_val}: score={info.get('final_score', '?')}{chosen}"
                        d_text = self.font_small.render(line, True, TEXT_COLOR)
                        self.screen.blit(d_text, (x + 5, y))
                        y += 18

                        detail_line = f"  A*={info.get('astar_score','?')} LR={info.get('lr_score','?')}"
                        z_text = self.font_small.render(detail_line, True, (120, 120, 120))
                        self.screen.blit(z_text, (x + 5, y))
                        y += 18

        # Controls help
        y = SCREEN_HEIGHT - 80
        help_lines = [
            "H: Toggle heatmap",
            "SPACE: Roll dice",
            "1/2: Choose dice"
        ]
        for line in help_lines:
            h_text = self.font_small.render(line, True, (150, 150, 150))
            self.screen.blit(h_text, (x, y))
            y += 18

    def _draw_message_bar(self):
        """Draw the message bar at the bottom of the board."""
        bar_y = BOARD_SIZE_PX + 5
        pygame.draw.rect(self.screen, PRIMARY, (0, bar_y, BOARD_SIZE_PX, SCREEN_HEIGHT - bar_y))

        msg_text = self.font_medium.render(self.game.last_message, True, WHITE)
        self.screen.blit(msg_text, (15, bar_y + 15))