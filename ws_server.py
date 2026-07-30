import asyncio
import websockets
import json

# 存储房间
rooms = {}


async def handler(websocket, path):
    room_id = 'gomoku'  # 固定房间号
    player = None

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"收到消息: {data}")

                # 处理加入房间
                if data.get('type') == 'join':
                    # 如果房间不存在，创建房间
                    if room_id not in rooms:
                        rooms[room_id] = {
                            'clients': [],
                            'board': [[None] * 15 for _ in range(15)],
                            'current_player': 'black',
                            'pass_count': 0,
                            'game_over': False,
                            'winner': None
                        }

                    # 如果房间已有2人，拒绝加入
                    if len(rooms[room_id]['clients']) >= 2:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '房间已满'
                        }))
                        continue

                    # 分配颜色：第一个黑棋，第二个白棋
                    player = 'black' if len(rooms[room_id]['clients']) == 0 else 'white'
                    rooms[room_id]['clients'].append({
                        'ws': websocket,
                        'player': player
                    })

                    print(f"玩家加入: {player}, 当前房间人数: {len(rooms[room_id]['clients'])}")

                    # 发送初始化消息
                    await websocket.send(json.dumps({
                        'type': 'init',
                        'player': player,
                        'board': rooms[room_id]['board'],
                        'current_player': rooms[room_id]['current_player']
                    }))

                    # 如果已有2人，通知双方游戏开始
                    if len(rooms[room_id]['clients']) == 2:
                        await broadcast_room(room_id, {
                            'type': 'start',
                            'message': '游戏开始！黑棋先走'
                        })
                        # 同步完整棋盘状态给所有客户端
                        await sync_board(room_id)

                    continue

                # 处理移动
                if data.get('type') == 'move':
                    room = rooms.get(room_id)
                    if not room:
                        continue

                    # 验证是否轮到自己
                    if data.get('player') != room['current_player']:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '还没轮到你'
                        }))
                        continue

                    row = data.get('row')
                    col = data.get('col')

                    # 落子
                    if room['board'][row][col] is not None:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '该位置已有棋子'
                        }))
                        continue

                    room['board'][row][col] = data['player']

                    # 检查胜负
                    if check_win(room['board'], row, col, data['player']):
                        room['game_over'] = True
                        room['winner'] = data['player']
                        await broadcast_room(room_id, {
                            'type': 'win',
                            'winner': data['player']
                        })
                    else:
                        # 切换玩家
                        room['current_player'] = 'white' if room['current_player'] == 'black' else 'black'
                        # 广播棋盘状态
                        await sync_board(room_id)

                    continue

                # 处理让棋
                if data.get('type') == 'pass':
                    room = rooms.get(room_id)
                    if not room:
                        continue

                    if room['game_over']:
                        continue

                    if data.get('player') != room['current_player']:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '还没轮到你'
                        }))
                        continue

                    if room['pass_count'] >= 3:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '让棋次数已用完'
                        }))
                        continue

                    room['pass_count'] += 1
                    room['current_player'] = 'white' if room['current_player'] == 'black' else 'black'

                    await broadcast_room(room_id, {
                        'type': 'pass_notify',
                        'pass_count': room['pass_count']
                    })
                    await sync_board(room_id)

                    continue

                # 处理重置
                if data.get('type') == 'reset':
                    room = rooms.get(room_id)
                    if room:
                        room['board'] = [[None] * 15 for _ in range(15)]
                        room['current_player'] = 'black'
                        room['pass_count'] = 0
                        room['game_over'] = False
                        room['winner'] = None
                        await broadcast_room(room_id, {
                            'type': 'reset'
                        })
                        await sync_board(room_id)

                    continue

            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
            except Exception as e:
                print(f"处理消息错误: {e}")

    except websockets.exceptions.ConnectionClosed:
        print("客户端断开连接")
    finally:
        # 清理断开连接的客户端
        if room_id in rooms:
            room = rooms[room_id]
            room['clients'] = [c for c in room['clients'] if c['ws'] != websocket]
            if len(room['clients']) == 0:
                del rooms[room_id]
                print("房间已清空")


async def sync_board(room_id):
    """同步棋盘状态给房间内所有客户端"""
    room = rooms.get(room_id)
    if not room:
        return

    message = {
        'type': 'sync',
        'board': room['board'],
        'current_player': room['current_player'],
        'pass_count': room['pass_count'],
        'game_over': room['game_over']
    }
    if room['winner']:
        message['winner'] = room['winner']

    await broadcast_room(room_id, message)


async def broadcast_room(room_id, message):
    """广播消息给房间内所有客户端"""
    room = rooms.get(room_id)
    if not room:
        return

    data = json.dumps(message)
    for client_info in room['clients']:
        try:
            if client_info['ws'].open:
                await client_info['ws'].send(data)
        except Exception as e:
            print(f"广播消息失败: {e}")


def check_win(board, row, col, player):
    """检查五子连珠"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        for d in [1, -1]:
            for step in range(1, 5):
                r = row + dr * step * d
                c = col + dc * step * d
                if r < 0 or r >= 15 or c < 0 or c >= 15 or board[r][c] != player:
                    break
                count += 1
        if count >= 5:
            return True
    return False


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("=" * 50)
        print("五子棋 WebSocket 服务器已启动")
        print("监听地址: 0.0.0.0:8765")
        print("等待玩家连接...")
        print("=" * 50)
        await asyncio.Future()  # 永久运行


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已关闭")