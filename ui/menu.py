import pygame

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (70, 130, 180)
TITLE_COLOR = (50, 50, 150)


class Button:
    """按钮类：包含位置、大小、文字、点击检测"""

    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hover = False

    def draw(self, screen):
        # 鼠标悬停时变色
        color = BLUE if self.is_hover else DARK_GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def draw_menu(screen, width, height, font_large, font_small):
    """绘制主菜单"""
    screen.fill(WHITE)

    # 标题
    title = font_large.render("五 子 棋", True, TITLE_COLOR)
    title_rect = title.get_rect(center=(width // 2, 120))
    screen.blit(title, title_rect)

    # 副标题 / 提示
    tip = font_small.render("请选择游戏模式", True, GRAY)
    tip_rect = tip.get_rect(center=(width // 2, 180))
    screen.blit(tip, tip_rect)

    return [
        Button(width // 2 - 100, 250, 200, 60, "双人对战", font_small),
        Button(width // 2 - 100, 350, 200, 60, "网络对战", font_small),
        Button(width // 2 - 100, 450, 200, 60, "退出游戏", font_small),
    ]


def draw_connecting(screen, width, height, font):
    """显示连接中界面"""
    screen.fill(WHITE)
    text = font.render("正在连接服务器...", True, BLUE)
    text_rect = text.get_rect(center=(width // 2, height // 2))
    screen.blit(text, text_rect)