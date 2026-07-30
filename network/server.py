import socket
import threading
import json


class GameServer:
    def __init__(self, host='0.0.0.0', port=8888, board_size=15): # host='0.0.0.0' 表示允许任何电脑连接
        self.host = host
        self.port = port
        self.board_size = board_size
        self.clients = []
        self.board = [[None] * board_size for _ in range(board_size)]
        self.current_player = 'black'
        self.game_over = False
        self.server_socket = None
        self.running = False
        #让棋相关属性
        self.pass_count = 0
        self.max_pass = 3

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        self.running = True

        print(f"服务器启动，监听 {self.host}:{self.port}")
        print("等待玩家连接...")

        while len(self.clients) < 2 and self.running:
            try:
                client, addr = self.server_socket.accept()
                self.clients.append(client)
                player = 'black' if len(self.clients) == 1 else 'white'
                print(f"玩家 {len(self.clients)} 已连接: {addr}，执 {player} 棋")

                client.send(json.dumps({
                    "type": "init",
                    "data": {"player": player}
                }).encode())

                self._send_board_state()

            except Exception as e:
                print(f"连接错误: {e}")
                break

        if len(self.clients) == 2:
            print("两个玩家已连接，游戏开始！黑棋先走")
            self.broadcast({
                "type": "start",
                "data": {"message": "游戏开始，黑棋先走"}
            })
            for client in self.clients:
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()
        else:
            print("未能连接两个玩家，服务器关闭")

    def _handle_client(self, client):
        while self.running:
            try:
                data = client.recv(4096).decode()
                if not data:
                    break
                msg = json.loads(data)
                self._handle_message(msg, client)
            except json.JSONDecodeError:
                print("收到无效 JSON 消息")
            except Exception as e:
                print(f"客户端连接异常: {e}")
                break

        if client in self.clients:
            self.clients.remove(client)
            print("客户端已断开")

    def _handle_message(self, msg, client):
        msg_type = msg.get('type')

        if msg_type == 'move':
            row = msg['data']['row']
            col = msg['data']['col']
            player = msg['data']['player']

            if self.game_over:
                return
            if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
                return
            if self.board[row][col] is not None:
                return
            if player != self.current_player:
                print(f"不是 {player} 的回合")
                return

            self.board[row][col] = player
            print(f"{player} 落子 ({row}, {col})")

            if self._check_win(row, col, player):
                self.game_over = True
                print(f"{player} 获胜！")
                self.broadcast({
                    "type": "win",
                    "data": {"winner": player}
                })
            elif self._is_board_full():
                self.game_over = True
                print("平局！")
                self.broadcast({
                    "type": "win",
                    "data": {"winner": "平局"}
                })
            else:
                self.current_player = 'white' if player == 'black' else 'black'
                self._send_board_state()
            pass

        # ===== 新增：让棋处理 =====
        elif msg_type == 'pass':
            player = msg['data']['player']

            # 验证
            if self.game_over:
                return
            if player != self.current_player:
                print(f"不是 {player} 的回合")
                return

            # 检查是否可以让棋
            if self.pass_count >= self.max_pass:
                print(f"{player} 让棋失败：次数已用完")
                return

            # 执行让棋
            self.pass_count += 1
            self.current_player = 'white' if player == 'black' else 'black'
            print(f"{player} 让棋 ({self.pass_count}/{self.max_pass})")

            # 广播让棋后的状态
            self._send_board_state()
            # 额外发送让棋通知
            self.broadcast({
                "type": "pass_notify",
                "data": {
                    "player": player,
                    "pass_count": self.pass_count,
                    "max_pass": self.max_pass
                }
            })

        elif msg_type == 'reset':
            self.board = [[None] * self.board_size for _ in range(self.board_size)]
            self.current_player = 'black'
            self.game_over = False
            self._send_board_state()
            self.broadcast({
                "type": "reset",
                "data": {"message": "游戏已重置"}
            })
            self.pass_count = 0

    def _send_board_state(self):
        self.broadcast({
            "type": "sync",
            "data": {
                "board": self.board,
                "current_player": self.current_player,

                "pass_count": self.pass_count,
                "max_pass": self.max_pass
            }
        })

    def broadcast(self, message):
        data = json.dumps(message).encode()
        for client in self.clients[:]:
            try:
                client.send(data)
            except Exception:
                if client in self.clients:
                    self.clients.remove(client)

    def _check_win(self, row, col, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if count >= 5:
                return True
        return False

    def _is_board_full(self):
        for row in self.board:
            for cell in row:
                if cell is None:
                    return False
        return True

    def stop(self):
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        if self.server_socket:
            self.server_socket.close()
        print("服务器已关闭")