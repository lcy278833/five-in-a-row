import asyncio
import websockets
import json

rooms = {}


async def handler(websocket):
    room_id = 'gomoku'

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"收到消息: {data}")

                if data.get('type') == 'join':
                    if room_id not in rooms:
                        rooms[room_id] = {
                            'clients': [],
                            'board': [[None] * 15 for _ in range(15)],
                            'current_player': 'black',
                            'pass_count': 0,
                            'game_over': False,
                            'winner': None,
                            'ready': False
                        }

                    room = rooms[room_id]

                    if len(room['clients']) >= 2:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '房间已满'
                        }))
                        continue

                    player = 'black' if len(room['clients']) == 0 else 'white'
                    room['clients'].append({
                        'ws': websocket,
                        'player': player
                    })

                    print(f"玩家加入: {player}, 当前房间人数: {len(room['clients'])}")

                    # 发送初始化消息
                    await websocket.send(json.dumps({
                        'type': 'init',
                        'player': player,
                        'board': room['board'],
                        'current_player': room['current_player']
                    }))

                    # 如果已有2人，通知双方游戏开始并同步状态
                    if len(room['clients']) == 2:
                        room['ready'] = True
                        print("两个玩家已连接，游戏开始！")
                        # 广播开始消息
                        await broadcast_room(room_id, {
                            'type': 'start',
                            'message': '游戏开始！黑棋先走'
                        })
                        # 同步完整棋盘状态
                        await sync_board(room_id)

                    continue

                # 处理移动
                if data.get('type') == 'move':
                    room = rooms.get(room_id)
                    if not room:
                        continue

                    if not room['ready']:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '等待对手加入'
                        }))
                        continue

                    if room['game_over']:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '游戏已结束'
                        }))
                        continue

                    # 验证当前玩家
                    if data.get('player') != room['current_player']:
                        print(f"错误: 当前玩家是 {room['current_player']}，但 {data.get('player')} 尝试落子")
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': f'还没轮到你，当前是 {room["current_player"]}'
                        }))
                        continue

                    row = data.get('row')
                    col = data.get('col')

                    if row is None or col is None:
                        continue

                    if row < 0 or row >= 15 or col < 0 or col >= 15:
                        continue

                    if room['board'][row][col] is not None:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '该位置已有棋子'
                        }))
                        continue

                    # 执行落子
                    room['board'][row][col] = data['player']
                    print(f"{data['player']} 落子 ({row}, {col})")

                    # 检查胜负
                    if check_win(room['board'], row, col, data['player']):
                        room['game_over'] = True
                        room['winner'] = data['player']
                        print(f"{data['player']} 获胜！")
                        await broadcast_room(room_id, {
                            'type': 'win',
                            'winner': data['player']
                        })
                    else:
                        # 切换玩家
                        room['current_player'] = 'white' if room['current_player'] == 'black' else 'black'
                        print(f"切换玩家: {room['current_player']}")
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
                            'message': f'还没轮到你，当前是 {room["current_player"]}'
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
                    print(f"{data['player']} 让棋，当前玩家: {room['current_player']}")

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
                        print("游戏已重置")
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
        if room_id in rooms:
            room = rooms[room_id]
            room['clients'] = [c for c in room['clients'] if c['ws'] != websocket]
            if len(room['clients']) == 0:
                del rooms[room_id]
                print("房间已清空")


async def sync_board(room_id):
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
    room = rooms.get(room_id)
    if not room:
        return

    data = json.dumps(message)
    # 使用 clients 副本遍历，避免修改时出错
    for client_info in room['clients'][:]:
        try:
            # 新版 websockets 使用 state 属性检查连接状态
            # 如果连接正常，state 是 <State.OPEN: 1>
            if client_info['ws'].state == websockets.protocol.State.OPEN:
                await client_info['ws'].send(data)
            else:
                print(f"客户端连接已关闭，移除")
                room['clients'].remove(client_info)
        except Exception as e:
            print(f"广播消息失败: {e}")
            # 移除有问题的客户端
            if client_info in room['clients']:
                room['clients'].remove(client_info)


def check_win(board, row, col, player):
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
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已关闭")