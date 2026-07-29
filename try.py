import pygame
import sys
import os

# from pygame.examples.moveit import HEIGHT

pygame.init()

#设置棋盘格式
BLACK = (0,0,0)
WHITE = (255,255,255)
BOARD_COLOR = (188,122,66)#木色
TEXT_COLOR = (255,0,0)#红色

BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 30
WIDTH = HEIGHT = MARGIN * 2 + (BOARD_SIZE - 1) * CELL_SIZE
VALID_RADIUS = 15

FONT_PATH = 'C:/Windows/Fonts/simhei.ttf'

#检查字体路径是否存在
if not os.path.exists(FONT_PATH):
    print(f"wrong: please put the file into: {FONT_PATH}.")
    sys.exit()#退出程序

#游戏初始化
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('五子棋对战')

board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]#初始化棋盘
#创建一个列表，棋盘初始值为空值(None) -> 15×15二维列表
current_player = 'black'#先手玩家
game_over = False#游戏结束标志

def get_chinese_player(player):
    return "黑棋" if player == "black" else "白棋"

def check_win(row, col, player):
    directions = [(0,1), (1,0), (1,1), (-1,1)]#相对位置
    for dr, dc in directions:
        count = 1
        '''8个方向
              (-1,1)
          ▲   (1,0)
        (1,0) (1,1)
        '''
        r, c = row + dr, col + dc#实际位置--正向
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r += dr
            c += dc

        r, c = row - dr, col - dc#反向
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        if count >= 5:
            return True
    return False

def draw_board():#绘制棋盘、棋子
    screen.fill(BOARD_COLOR)
    for i in range(BOARD_SIZE):
        pos = MARGIN + i * CELL_SIZE
        #绘制横竖线
        pygame.draw.line(screen,BLACK,(MARGIN,pos),(WIDTH - MARGIN,pos))#横线--y坐标固定（都是 start），x坐标从左边到右边变化
        pygame.draw.line(screen,BLACK,(pos,MARGIN),(pos,WIDTH - MARGIN))#竖线

    #绘制棋子
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col]:#若有棋子
                # board[row][col]存的字符串(也可用0/1来记黑白棋，内存占用更小)
                color = BLACK if board[row][col] == 'black' else WHITE
                pos = (MARGIN + col * CELL_SIZE, MARGIN + row * CELL_SIZE)
                pygame.draw.circle(screen,color,pos,CELL_SIZE//2 - 2)#向下取整，pygame.draw.circle()的半径参数必须是整数，传入浮点数会报错

def show_status(text):#在屏幕顶部显示状态文字
    font = pygame.font.Font(FONT_PATH,30)
    text_surface = font.render(text,True,TEXT_COLOR)#是否开启抗锯齿，True文字边缘更平滑
    #font.render()会把文字转换成一张图片（Surface 对象），才能被blit到屏幕上
    screen.blit(text_surface,(MARGIN,5))#贴到什么位置（左上角坐标），x=MARGIN，y=5，（blit 相当于“贴图”，把文字图片绘制到屏幕的指定位置）

def show_winner_popup(winner):#胜利者弹窗
    overlay = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    overlay.fill((0,0,180))
    screen.blit(overlay,(0,0))

    popup_width = 300
    popup_height = 150
    #矩形左上角横坐标，左上角纵坐标，矩形宽，高
    popup_rect = pygame.Rect((WIDTH - popup_width) // 2, (HEIGHT - popup_height) // 2, popup_width, popup_height)
    pygame.draw.rect(screen,WHITE,popup_rect)

    font = pygame.font.Font(FONT_PATH,40)
    text = font.render(f"{winner} 胜利！", True,(255,0,0))
    screen.blit(text,text.get_rect(center=(WIDTH // 2,HEIGHT // 2 - 15)))#微调上移15px，视觉重心舒服

    #点击任意位置重新开始
    small_font = pygame.font.Font(FONT_PATH,25)
    tip_text = small_font.render("按任意键重新开始",True,BLACK)
    screen.blit(tip_text,tip_text.get_rect(center=(WIDTH // 2,HEIGHT // 2 + 25)))

def reset_game():
    global board,current_player,game_over
    board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    current_player = 'black'
    game_over = False


# ==== 主循环 ====
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:#重置
                board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
                current_player = 'black'
                game_over = False
            else:#坐标转换，计算最近交叉点
                #屏幕坐标转换为：(棋盘行列索引-边缘留白)/每个格子大小，四舍五入，得到最近交叉点
                x,y = event.pos
                col = round((x - MARGIN) / CELL_SIZE)
                row = round((y - MARGIN) / CELL_SIZE)

                #计算实际交叉点坐标
                cross_x = (MARGIN + col * CELL_SIZE)
                cross_y = (MARGIN + row * CELL_SIZE)
                #验证点击有效性，计算点击偏差
                dx = x - cross_x
                dy = y - cross_y
                distance_sq = dx ** 2 + dy ** 4
                if distance_sq <= VALID_RADIUS ** 2 and 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    if board[row][col] is None:
                        board[row][col] = current_player
                        if check_win(row,col,current_player):
                            game_over = True
                        else:
                            current_player = 'white' if current_player == 'black' else 'black'
    draw_board()
    chinese_player = get_chinese_player(current_player)
    if game_over:
        show_status(f"游戏结束 - {chinese_player} 获胜！")
        show_winner_popup(chinese_player)

    else:
        show_status(f"当前玩家：{chinese_player}")
    pygame.display.flip()

