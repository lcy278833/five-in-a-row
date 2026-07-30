class Board:
    def __init__(self, size=15):
        self.size = size
        self.grid = [[None] * size for _ in range(size)]
        self.current_player = 'black'
        self.last_move = None
        # 新增：让棋相关
        self.max_pass = 3  # 最多让 3 次
        self.pass_count = 0  # 已让棋次数
        self.last_was_pass = False  # 上一步是否让棋（防止连续让棋）

    def place_piece(self, row, col):
        """落子，返回是否成功"""
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        if self.grid[row][col] is not None:
            return False
        self.grid[row][col] = self.current_player
        self.last_move = (row, col)
        self.last_was_pass = False  # 落子后重置让棋标记
        return True

    def switch_player(self):
        self.current_player = 'white' if self.current_player == 'black' else 'black'

    def pass_turn(self):
        """
        让棋：切换玩家，增加让棋计数
        返回: (是否成功, 剩余次数)
        """
        print(f"pass_turn() 被调用: pass_count={self.pass_count}")
        if self.pass_count >= self.max_pass:
            return False, 0
        self.pass_count += 1
        self.last_was_pass = True#允许连续让棋时，这行不再被检查
        self.switch_player()
        print(f"让棋后 pass_count={self.pass_count}")
        return True, self.max_pass - self.pass_count


    def reset(self):
        self.grid = [[None] * self.size for _ in range(self.size)]
        self.current_player = 'black'
        self.last_move = None
        # 重置让棋
        self.pass_count = 0
        self.last_was_pass = False

    def get_piece(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return None

    def get_pass_remaining(self):
        """获取剩余让棋次数"""
        return self.max_pass - self.pass_count

    def can_pass(self):
        """判断是否可以让棋"""
        print(f"can_pass: pass_count={self.pass_count}, max_pass={self.max_pass}")  # 调试
        return self.pass_count < self.max_pass

# ===== 测试代码（放在 game/board.py 末尾） =====
if __name__ == '__main__':
    b = Board()
    print(f"初始: pass_count={b.pass_count}")
    success, remaining = b.pass_turn()
    print(f"让棋后: pass_count={b.pass_count}, remaining={remaining}")
    success, remaining = b.pass_turn()
    print(f"再让棋: pass_count={b.pass_count}, remaining={remaining}")
