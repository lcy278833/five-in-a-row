def check_win(board, row, col, player):
    """检查 (row, col) 位置是否形成五子连珠"""
    if player is None:
        return False

    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    size = len(board)

    for dr, dc in directions:
        count = 1
        # 正方向
        r, c = row + dr, col + dc
        while 0 <= r < size and 0 <= c < size and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        # 反方向
        r, c = row - dr, col - dc
        while 0 <= r < size and 0 <= c < size and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        if count >= 5:
            return True
    return False


def is_board_full(board):
    """检查棋盘是否已满（平局）"""
    for row in board:
        for cell in row:
            if cell is None:
                return False
    return True