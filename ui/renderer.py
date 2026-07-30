import pygame

# 颜色常量
BOARD_COLOR = (188, 122, 66)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEXT_COLOR = (255, 0, 0)


def draw_board(screen, board, board_size, cell_size, margin):
    """绘制完整的棋盘和棋子"""
    screen.fill(BOARD_COLOR)
    width = screen.get_width()
    height = screen.get_height()

    # 画网格
    for i in range(board_size):
        pos = margin + i * cell_size
        #横竖线
        pygame.draw.line(screen, BLACK, (margin, pos), (width - margin, pos), 1)
        pygame.draw.line(screen, BLACK, (pos, margin), (pos, width - margin), 1)

    # 画棋子
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] is not None:
                color = BLACK if board[row][col] == 'black' else WHITE
                pos = (margin + col * cell_size, margin + row * cell_size)
                pygame.draw.circle(screen, color, pos, cell_size // 2 - 2)


def show_status(screen, text, font_path, margin):
    """在屏幕顶部显示状态文字"""
    # font = pygame.font.Font(font_path, 30)
    try:
        font = pygame.font.Font(font_path, 30)
    except:
        font = pygame.font.Font(None, 30)  # 用默认字体
    text_surface = font.render(text, True, TEXT_COLOR)
    screen.blit(text_surface, (margin, 5))


def show_winner_popup(screen, winner, width, height, font_path):
    """显示胜利弹窗"""
    # 半透明遮罩
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    # 弹窗背景
    popup_width, popup_height = 300, 150
    popup_rect = pygame.Rect(
        (width - popup_width) // 2,
        (height - popup_height) // 2,
        popup_width, popup_height
    )
    pygame.draw.rect(screen, WHITE, popup_rect)
    pygame.draw.rect(screen, BLACK, popup_rect, 2)

    # 胜利文字
    # font = pygame.font.Font(font_path, 40)
    try:
        font = pygame.font.Font(font_path, 30)
    except:
        font = pygame.font.Font(None, 30)  # 用默认字体
    text = font.render(f"{winner} 胜利！", True, (255, 0, 0))
    screen.blit(text, text.get_rect(center=(width // 2, height // 2 - 15)))

    # 提示文字
    # small_font = pygame.font.Font(font_path, 25)
    try:
        small_font = pygame.font.Font(font_path, 30)
    except:
        small_font = pygame.font.Font(None, 30)  # 用默认字体
    tip = small_font.render("按任意键重新开始", True, BLACK)
    screen.blit(tip, tip.get_rect(center=(width // 2, height // 2 + 25)))


def draw_pass_button(screen, pass_count, max_pass, x, y, width, height, font_path=None):
    """
    绘制让棋按钮
    返回: pygame.Rect 用于点击检测
    """
    try:
        font = pygame.font.Font(font_path, 18)
    except:
        font = pygame.font.Font(None, 18)

    can_pass = pass_count < max_pass
    rect = pygame.Rect(x, y, width, height)

    # 鼠标悬停效果
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)

    # 按钮背景颜色
    if can_pass:
        bg_color = (80, 200, 80) if not is_hover else (120, 255, 120)
        border_color = (0, 100, 0)
        text_color = (255, 255, 255)
    else:
        bg_color = (180, 180, 180) if not is_hover else (200, 200, 200)
        border_color = (120, 120, 120)
        text_color = (80, 80, 80)

    # 绘制按钮
    # rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)

    # 按钮文字
    text = f"让棋 ({pass_count}/{max_pass})"
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

    return rect