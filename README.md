# 五子棋

一个使用 Pygame 开发的五子棋双人对战小游戏。

## 如何运行

1. 安装依赖：`pip install pygame`
2. 运行游戏：`python main.py`

## 技术栈

- Python 3.11
- Pygame 2.6.1

## 特别操作：
"双人对战"模式任何情况都可
“网络对战”模式需分别四个terminal按序运行：
python ws_server.py  
.\cloudflared tunnel --url http://localhost:8765  
python -m http.server 8080  
.\ngrok http 8080