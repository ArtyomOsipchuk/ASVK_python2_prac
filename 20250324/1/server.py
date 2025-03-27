#!/usr/bin/env python3
import asyncio
import cowsay

clients = {}
names = set()
dungeon = [[0 for i in range(10)] for j in range(10)]
# dungeon[y][x] = hp, name, message
pos = [0, 0]
# pos = [x, y]


async def MUDServer(reader, writer):
    me = None 
    queue = asyncio.Queue()
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(queue.get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                message = q.result().decode().strip()
                print('RECEIVED>>', [message])
                if not message:
                    continue
                if not me:
                    if message in names:
                        ans = "Отказано в подключении. Такой пользователь уже есть"
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        break
                    else:
                        me = message
                        clients[me] = queue
                        names.add(message)
                        ans = f"Добро пожаловать в MUD, {me}!"
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                        for out in clients.values():
                            ans = f"{me} присоединился к рейду!"
                            print('MULTISENDED>>', [ans])
                            await out.put(ans)
                elif message == 'up':
                    ans = ""
                    print('SENDED>>', [ans])
                    writer.write(bytes(ans.encode()))
                    await writer.drain()
                elif message.startswith('addmob '):
                    print(f"Added monster {name} to ({x}, {y}) saying {hello}")
                    if dungeon[y][x]:
                        print("Replaced the old monster")
                    dungeon[y][x] = [hp, name, hello]
                elif message == "quit":
                    ans = "До новых встреч на просторах MUD!"
                    print('SENDED>>', [ans])
                    writer.write(bytes(ans.encode()))
                    for out in clients.values():
                        ans = f"Пользователь {me} покинул подземелье..."
                        print('MULTISENDED>>', [ans])
                        await out.put(ans)
                    del clients[me]
                    names.remove(me)
                    me = None
                elif message == 'help':
                    ans = '''Команды:
                    help — вы здесь
                    up \ down \ left \ right — движения по данжу
                    attack — атаковать монстра
                    addmon — добавить монстра
                    quit — выбраться из подземелья'''
                    print('SENDED>>', [ans])
                    writer.write(bytes(ans.encode()))
                    await writer.drain()
                else:
                    ans = "Неизвестная команда. Введите 'help' для вывода списка команд."
                    print('SENDED>>', [ans])
                    writer.write(bytes(ans.encode()))
                    await writer.drain()
            elif q is receive:
                receive = asyncio.create_task(queue.get())
                writer.write(bytes(f"{q.result()}\n".encode()))
                await writer.drain()
    send.cancel()
    receive.cancel()
    if me is not None:
        del clients[me]
        names.remove(me)
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(MUDServer, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
