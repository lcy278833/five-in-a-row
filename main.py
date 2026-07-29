import pygame
import sys
import os

from game.board import Board
from game.judge import check_win, is_board_full
from ui.renderer import draw_board, show_status, show_winner_popup

# ========== 常量 ==========
BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 30
WIDTH = MARGIN * 2 + (BOARD_SIZE - 1) * CELL_SIZE
HEIGHT = WIDTH
VALID_RADIUS = 15
FONT_PATH = 'C:/Windows/Fonts/simhei.ttf'

# ========== 初始化 ==========
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('五子棋 - 本地对战')

if not os.path.exists(FONT_PATH):
    print(f"错误：找不到字体文件 {FONT_PATH}")
    sys.exit()

board = Board(BOARD_SIZE)
game_over = False
winner_name = None


def get_chinese_player(player):
    return "黑棋" if player == "black" else "白棋"


def reset_game():
    global game_over, winner_name
    board.reset()
    game_over = False
    winner_name = None


# ========== 主循环 ==========
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                reset_game()
            else:
                x, y = event.pos
                col = round((x - MARGIN) / CELL_SIZE)
                row = round((y - MARGIN) / CELL_SIZE)

                cross_x = MARGIN + col * CELL_SIZE
                cross_y = MARGIN + row * CELL_SIZE
                dx = x - cross_x
                dy = y - cross_y

                if (dx ** 2 + dy ** 2 <= VALID_RADIUS ** 2 and
                    0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and
                    board.grid[row][col] is None):

                    board.place_piece(row, col)

                    if check_win(board.grid, row, col, board.current_player):
                        winner_name = get_chinese_player(board.current_player)
                        game_over = True
                    elif is_board_full(board.grid):
                        winner_name = "平局"
                        game_over = True
                    else:
                        board.switch_player()

    # ========== 绘制 ==========
    draw_board(screen, board.grid, BOARD_SIZE, CELL_SIZE, MARGIN)

    if game_over:
        if winner_name:
            show_status(screen, f"游戏结束 - {winner_name} 获胜！", FONT_PATH, MARGIN)
            show_winner_popup(screen, winner_name, WIDTH, HEIGHT, FONT_PATH)
        else:
            show_status(screen, "游戏结束", FONT_PATH, MARGIN)
    else:
        show_status(screen, f"当前玩家：{get_chinese_player(board.current_player)}", FONT_PATH, MARGIN)

    pygame.display.flip()
    clock.tick(60)