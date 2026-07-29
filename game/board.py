class Board:
    def __init__(self, size=15):
        self.size = size
        self.grid = [[None] * size for _ in range(size)]
        self.current_player = 'black'
        self.last_move = None

    def place_piece(self, row, col):
        """落子，返回是否成功"""
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        if self.grid[row][col] is not None:
            return False
        self.grid[row][col] = self.current_player
        self.last_move = (row, col)
        return True

    def switch_player(self):
        self.current_player = 'white' if self.current_player == 'black' else 'black'

    def reset(self):
        self.grid = [[None] * self.size for _ in range(self.size)]
        self.current_player = 'black'
        self.last_move = None

    def get_piece(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return None