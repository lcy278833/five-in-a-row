import pygame
import sys
import os

from network.client import GameClient
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
pygame.display.set_caption('五子棋 - 网络对战')

if not os.path.exists(FONT_PATH):
    print(f"错误：找不到字体文件 {FONT_PATH}")
    sys.exit()

# ========== 连接服务器 ==========
# 同一台电脑测试用 '127.0.0.1'
# 局域网对战改成服务器的实际 IP（如 '192.168.1.100'）
client = GameClient(server_host='127.0.0.1', server_port=8888)
player = client.connect()

if player is None:
    print("无法连接到服务器，程序退出")
    sys.exit()

print(f"你执 {player} 棋")


def get_chinese_player(player):
    return "黑棋" if player == "black" else "白棋"


# ========== 界面更新回调 ==========
def on_update():
    """当收到服务器数据时刷新界面"""
    pass


client.on_update = on_update

# ========== 主循环 ==========
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client.close()
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if client.game_over:
                # 游戏结束，点击重新开始
                client.send_reset()
            else:
                x, y = event.pos
                col = round((x - MARGIN) / CELL_SIZE)
                row = round((y - MARGIN) / CELL_SIZE)

                cross_x = MARGIN + col * CELL_SIZE
                cross_y = MARGIN + row * CELL_SIZE
                dx = x - cross_x
                dy = y - cross_y

                if (dx ** 2 + dy ** 2 <= VALID_RADIUS ** 2 and
                    0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
                    client.send_move(row, col)

    # ========== 绘制 ==========
    draw_board(screen, client.board, BOARD_SIZE, CELL_SIZE, MARGIN)

    if client.game_over:
        if client.winner == "平局":
            show_status(screen, "平局！", FONT_PATH, MARGIN)
            show_winner_popup(screen, "平局", WIDTH, HEIGHT, FONT_PATH)
        elif client.winner:
            show_status(screen, f"游戏结束 - {client.winner} 获胜！", FONT_PATH, MARGIN)
            show_winner_popup(screen, client.winner, WIDTH, HEIGHT, FONT_PATH)
        else:
            show_status(screen, "游戏结束", FONT_PATH, MARGIN)
    else:
        status = f"当前玩家：{get_chinese_player(client.current_player)}"
        if client.current_player == client.player:
            status += " 你的回合"
        else:
            status += " 等待对手..."
        show_status(screen, status, FONT_PATH, MARGIN)

    pygame.display.flip()
    clock.tick(60)#固定60帧 - 每秒最多刷新60次画面,防止CPU会一直满负荷运转，电脑发烫