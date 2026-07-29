import socket
import json
import threading


class GameClient:
    def __init__(self, server_host='127.0.0.1', server_port=8888, board_size=15):
        self.server_host = server_host
        self.server_port = server_port
        self.board_size = board_size

        self.socket = None
        self.player = None #'black' 或 'white'
        self.board = [[None] * board_size for _ in range(board_size)]
        self.current_player = 'black'
        self.game_over = False
        self.winner = None
        self.connected = False
        self.on_update = None# 回调函数，用于更新界面

    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True

            # 接收初始化消息
            data = self.socket.recv(4096).decode()#缓冲区大小-一次最多读取4096个字节(4KB)的数据
            if data:
                msg = json.loads(data)
                if msg['type'] == 'init':
                    self.player = msg['data']['player']
                    print(f"连接成功，你执 {self.player} 棋")
            # 启动接收线程
            threading.Thread(target=self._receive_messages, daemon=True).start()
            return self.player

        except ConnectionRefusedError:
            print("无法连接到服务器，请确认服务器已启动")
            return None
        except Exception as e:
            print(f"连接失败: {e}")
            return None

    def _receive_messages(self):
        """接收服务器消息的线程"""
        while self.connected:
            try:
                data = self.socket.recv(8192).decode()
                if not data:
                    break
                msg = json.loads(data)
                self._handle_message(msg)
            except json.JSONDecodeError:
                print("收到无效消息")
            except Exception as e:
                print(f"接收消息异常: {e}")
                break

        self.connected = False
        print("与服务器断开连接")

    def _handle_message(self, msg):
        """处理服务器发来的消息"""
        msg_type = msg.get('type')

        if msg_type == 'start':
            print(f"游戏开始")

        elif msg_type == 'sync': #sync: 同时，同步；协调，一致；
            self.board = msg['data']['board']
            self.current_player = msg['data']['current_player']
            if self.on_update:
                self.on_update()

        elif msg_type == 'win':
            # 同步棋盘状态
            self.game_over = True
            self.winner = msg['data']['winner']
            print(f"{self.winner} 获胜")
            if self.on_update:
                self.on_update()

        elif msg_type == 'reset':
            self.game_over = False
            self.winner = None
            print("游戏已重置")
            if self.on_update:
                self.on_update()

    def send_move(self, row, col):
        """发送落子消息到服务器"""
        if not self.connected:
            print("未连接到服务器")
            return False

        if self.game_over:
            print("游戏已结束")
            return False

        if self.player != self.current_player:
            print("还没轮到你下棋")
            return False

        if self.board[row][col] is not None:
            print("该位置已有棋子")
            return False

        msg = {
            "type": "move",
            "data": {
                "row": row,
                "col": col,
                "player": self.player
            }
        }
        try:
            self.socket.send(json.dumps(msg).encode())
            return True
        except Exception as e:
            print(f"发送失败: {e}")
            return False

    def send_reset(self):
        if not self.connected:
            return
        try:
            self.socket.send(json.dumps({"type": "reset", "data": {}}).encode())
        except Exception as e:
            print(f"发送重置请求失败: {e}")

    def close(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("连接已关闭")