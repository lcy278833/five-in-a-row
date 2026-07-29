from network.server import GameServer

if __name__ == '__main__':
    # 可选：修改端口
    # server = GameServer(host='0.0.0.0', port=8888)
    server = GameServer()
    try:
        server.start()
        # 保持运行
        import threading
        while server.running:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        server.stop()