import pygame
import sys
import os

from game.board import Board
from game.judge import check_win, is_board_full
from ui.renderer import draw_board, show_status, show_winner_popup, draw_pass_button
from ui.menu import draw_menu, draw_connecting, Button
from network.client import GameClient

# ========== 常量 ==========
BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 30
WIDTH = MARGIN * 2 + (BOARD_SIZE - 1) * CELL_SIZE
HEIGHT = WIDTH
VALID_RADIUS = 15
FONT_PATH = 'C:/Windows/Fonts/simhei.ttf'

# 让棋按钮位置
PASS_BUTTON_X = WIDTH - 130
PASS_BUTTON_Y = 5
PASS_BUTTON_WIDTH = 110
PASS_BUTTON_HEIGHT = 20

# ========== 游戏状态 ==========
MENU = 0
LOCAL = 1
NETWORK = 2
CONNECTING = 3

# ========== 全局变量 ==========
# pass_button_rect = None  # 让棋按钮矩形

# ========== 初始化 ==========
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('五子棋')

if not os.path.exists(FONT_PATH):
    print(f"错误：找不到字体文件 {FONT_PATH}")
    sys.exit()

font_large = pygame.font.Font(FONT_PATH, 60)
font_medium = pygame.font.Font(FONT_PATH, 36)
font_small = pygame.font.Font(FONT_PATH, 28)

# ========== 游戏状态变量 ==========
state = MENU
buttons = []

# 本地游戏变量
local_board = Board(BOARD_SIZE)
local_game_over = False
local_winner = None

# 网络游戏变量
network_client = None
network_player = None

clock = pygame.time.Clock()


# ========== 辅助函数 ==========
def get_chinese_player(player):
    return "黑棋" if player == "black" else "白棋"


def reset_local_game():
    global local_board, local_game_over, local_winner
    local_board.reset()
    local_game_over = False
    local_winner = None


def start_network_game():
    global network_client, network_player, state
    state = CONNECTING
    network_client = GameClient(server_host='127.0.0.1', server_port=8888)
    network_player = network_client.connect()
    if network_player:
        state = NETWORK
        network_client.on_update = lambda: None  # 简单回调
        print("网络连接成功！")  # 增加这一行，方便查看状态
    else:
        state = MENU
        print("网络连接失败，返回菜单")

#让棋逻辑（统一处理
def try_pass():
    """尝试让棋，返回是否成功"""
    global state, local_board, network_client
    if state == LOCAL:
        if local_board.can_pass():
            success, remaining = local_board.pass_turn()
            if success:
                print(f"让棋成功，剩余 {remaining} 次")
                return True
            else:
                print("让棋失败")
                return False
        else:
            if local_board.pass_count >= local_board.max_pass:
                print("让棋次数已用完")
            elif local_board.last_was_pass:
                print("对手刚让完棋，你必须落子")
            else:
                print("无法让棋")
            return False
    elif state == NETWORK and network_client:
        if network_client.can_pass():
            network_client.send_pass()
            return True
        else:
            print("网络模式无法让棋")
            return False
    else:
        print(f"当前状态 {state} 不支持让棋")
        return False

# ========== 主循环 ==========
while True:
    # 让棋按钮矩形（在绘制时更新）
    button_rect = pygame.Rect(PASS_BUTTON_X, PASS_BUTTON_Y, PASS_BUTTON_WIDTH, PASS_BUTTON_HEIGHT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if network_client:
                network_client.close()
            pygame.quit()
            sys.exit()

        #键盘事件（统一处理）
        elif event.type == pygame.KEYDOWN:
            print(f"按下了按键：{event.key}")

            if event.key == pygame.K_ESCAPE:
                if state == LOCAL or state == NETWORK:
                    state = MENU
                    if network_client:
                        network_client.close()
                        network_client = None
                elif state == MENU:
                    pygame.quit()
                    sys.exit()

            # ===== P 键让棋（所有模式通用） =====
            if event.key == pygame.K_p:
                print("P键被按下")
                try_pass()#统一调度让棋函数

        # ===== 菜单状态 =====
        if state == MENU:
            for button in buttons:
                if button.handle_event(event):
                    if button.text == "双人对战":
                        state = LOCAL
                        reset_local_game()
                    elif button.text == "网络对战":
                        start_network_game()
                    elif button.text == "退出游戏":
                        pygame.quit()
                        sys.exit()

        # ===== 本地对战状态 =====
        elif state == LOCAL:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 直接检测点击是否在按钮区域
                if button_rect.collidepoint(event.pos):
                    print("点击了让棋按钮")
                    try_pass()  # 调用统一让棋函数
                elif local_game_over:
                    reset_local_game()
                else:
                    # 正常落子逻辑
                    x, y = event.pos
                    col = round((x - MARGIN) / CELL_SIZE)
                    row = round((y - MARGIN) / CELL_SIZE)
                    cross_x = MARGIN + col * CELL_SIZE
                    cross_y = MARGIN + row * CELL_SIZE
                    dx = x - cross_x
                    dy = y - cross_y
                    if (dx ** 2 + dy ** 2 <= VALID_RADIUS ** 2 and
                            0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and
                            local_board.grid[row][col] is None):
                        local_board.place_piece(row, col)
                        if check_win(local_board.grid, row, col, local_board.current_player):
                            local_winner = get_chinese_player(local_board.current_player)
                            local_game_over = True
                        elif is_board_full(local_board.grid):
                            local_winner = "平局"
                            local_game_over = True
                        else:
                            local_board.switch_player()

        # ===== 网络对战状态 =====
        elif state == NETWORK:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if network_client is None:
                    print("未连接到服务器")
                elif network_client.game_over:
                    network_client.send_reset()
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
                        # 检查该位置是否有棋子
                        if network_client.board[row][col] is None:
                            network_client.send_move(row, col)
                        else:
                            print("该位置已有棋子")

    # ========== 绘制 ==========
    if state == MENU:
        buttons = draw_menu(screen, WIDTH, HEIGHT, font_large, font_small)
        # 绘制按钮
        for button in buttons:
            button.draw(screen)

    elif state == CONNECTING:
        draw_connecting(screen, WIDTH, HEIGHT, font_medium)

    elif state == LOCAL:
        draw_board(screen, local_board.grid, BOARD_SIZE, CELL_SIZE, MARGIN)

        # 绘制让棋按钮，并保存矩形用于点击检测
        if not local_game_over:
            button_rect = draw_pass_button(
            screen,
            local_board.pass_count,
            local_board.max_pass,
            PASS_BUTTON_X, PASS_BUTTON_Y,
            PASS_BUTTON_WIDTH, PASS_BUTTON_HEIGHT,
            FONT_PATH
        )
            # print(f"绘制让棋按钮: pass_count={local_board.pass_count},button_rect={button_rect}")  # 调试
        else:
            button_rect = None

        if local_game_over:
            if local_winner == "平局":
                show_status(screen, "平局！", FONT_PATH, MARGIN)
                show_winner_popup(screen, "平局", WIDTH, HEIGHT, FONT_PATH)
            elif local_winner:
                show_status(screen, f"游戏结束 - {local_winner} 获胜！", FONT_PATH, MARGIN)
                show_winner_popup(screen, local_winner, WIDTH, HEIGHT, FONT_PATH)
            else:
                show_status(screen, "游戏结束", FONT_PATH, MARGIN)
        else:
            # show_status(screen, f"当前玩家：{get_chinese_player(local_board.current_player)}", FONT_PATH, MARGIN)
            status = f"当前玩家：{get_chinese_player(local_board.current_player)}"
            if local_board.can_pass():
                status += ("[P键让棋]")
            show_status(screen,status,FONT_PATH,MARGIN)

    elif state == NETWORK:
        if network_client:
            draw_board(screen, network_client.board, BOARD_SIZE, CELL_SIZE, MARGIN)
            #绘制让棋按钮，游戏未结束时显示
            if not network_client.game_over:
                button_rect = draw_pass_button(
                    screen,
                    network_client.pass_count,
                    network_client.max_pass,
                    PASS_BUTTON_X, PASS_BUTTON_Y,
                    PASS_BUTTON_WIDTH, PASS_BUTTON_HEIGHT,
                    FONT_PATH
                )
            else:
                button_rect = None

            if network_client.game_over:
                if network_client.winner == "平局":
                    show_status(screen, "平局！", FONT_PATH, MARGIN)
                    show_winner_popup(screen, "平局", WIDTH, HEIGHT, FONT_PATH)
                elif network_client.winner:
                    show_status(screen, f"游戏结束 - {network_client.winner} 获胜！", FONT_PATH, MARGIN)
                    show_winner_popup(screen, network_client.winner, WIDTH, HEIGHT, FONT_PATH)
                else:
                    show_status(screen, "游戏结束", FONT_PATH, MARGIN)
            else:
                status = f"当前玩家：{get_chinese_player(network_client.current_player)}"
                if network_client.current_player == network_client.player:
                    status += " 你的回合"
                    if network_client.can_pass():
                        status += "[P键让棋]"
                else:
                    status += " 等待对手..."
                show_status(screen, status, FONT_PATH, MARGIN)

    pygame.display.flip()
    clock.tick(60)