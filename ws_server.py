import asyncio
import websockets
import json

# 存储所有连接的客户端
clients = set()
# 存储房间
rooms = {}


async def handler(websocket, path):
    # 加入客户端
    clients.add(websocket)
    player = None
    room_id = 'gomoku'  # 简单起见，固定房间号

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"收到消息: {data}")

                # 处理加入房间
                if data.get('type') == 'join':
                    if room_id not in rooms:
                        rooms[room_id] = []
                    rooms[room_id].append(websocket)
                    player = 'black' if len(rooms[room_id]) == 1 else 'white'
                    await websocket.send(json.dumps({
                        'type': 'init',
                        'player': player
                    }))
                    print(f"玩家加入: {player}, 当前房间人数: {len(rooms[room_id])}")
                    continue

                # 广播消息给同房间的其他人
                if room_id in rooms:
                    for client in rooms[room_id]:
                        if client != websocket and client.open:
                            try:
                                await client.send(message)
                            except:
                                pass

            except json.JSONDecodeError:
                print("收到无效JSON")

    except websockets.exceptions.ConnectionClosed:
        print("连接断开")
    finally:
        # 清理断开连接的客户端
        clients.remove(websocket)
        if room_id in rooms and websocket in rooms[room_id]:
            rooms[room_id].remove(websocket)
        if room_id in rooms and len(rooms[room_id]) == 0:
            del rooms[room_id]


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket 服务器启动，监听端口 8765")
        await asyncio.Future()  # 永久运行


if __name__ == "__main__":
    asyncio.run(main())