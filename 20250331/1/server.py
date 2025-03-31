#!/usr/bin/env python3
import asyncio
import cowsay
import shlex
from io import StringIO

class MUDServer:
    clients = {}
    names = set()
    dungeon = [[0 for i in range(10)] for j in range(10)]
    # dungeon[y][x] = hp, name, message
    pos = [0, 0]
    # pos = [x, y]

    def encounter(self, y, x):
        jgsbat = cowsay.read_dot_cow(StringIO("""    ,_                    _,
        ) '-._  ,_    _,  _.-' (
        )  _.-'.|\\ \b\\--//|.'-._  (
         )'   .'\\/o\\/o\\/'.   `(
          ) .' . \\====/ . '. (
           )  / <<    >> \\  (
            '-._/``  ``\\_.-'
      jgs     __\\ \b\\'--'//__
             (((""`  `"")))"""))
        hp, name, message = self.dungeon[y][x]
        if name == "jgsbat":
            return cowsay.cowsay(message, cowfile=jgsbat)
        else:
            return cowsay.cowsay(message, cow=name)


    async def server(self, reader, writer):
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
                        if message in self.names:
                            ans = "Отказано в подключении. Такой пользователь уже есть"
                            print('SENDED>>', [ans])
                            writer.write(bytes(ans.encode()))
                            break
                        else:
                            me = message
                            self.clients[me] = queue
                            self.names.add(message)
                            ans = f"Добро пожаловать в MUD, {me}!"
                            print('SENDED>>', [ans])
                            writer.write(bytes(ans.encode()))
                            await writer.drain()
                            for out in self.clients.values():
                                if out != me:
                                    ans = f"{me} присоединился к рейду!"
                                    print('MULTISENDED>>', [ans])
                                    await out.put(ans)
                    elif message.startswith('move '):
                        move, x, y = shlex.split(message)
                        y, x = int(y), int(x)
                        self.pos = [(self.pos[0] + x) % 10, (self.pos[1] + y) % 10]
                        pos = self.pos
                        ans = f"Moved to {pos[0]} {pos[1]}"
                        if self.dungeon[pos[1]][pos[0]]:
                            ans += "\nMoved to ...\n"
                            ans += self.encounter(pos[1], pos[0])
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                    elif message.startswith('addmon '):
                        #"addmon {name} {hp} {y} {x} {hello}\n"
                        addmob, name, hp, y, x, hello = shlex.split(message)
                        y, x = int(y), int(x)
                        ans = f"Added monster {name} to ({x}, {y}) saying {hello}"
                        if self.dungeon[y][x]:
                            ans += "\nReplaced the old monster"
                        self.dungeon[y][x] = [hp, name, hello]
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                        ans = f"Player {name} added monster {name} to ({x}, {y}) saying {hello}"
                        for out in self.clients.values():
                                if out != me:
                                    print('MULTISENDED>>', [ans])
                                    await out.put(ans)
                    elif message.startswith('attack '):
                        attack, name, damage, weapon = shlex.split(message)
                        damage = int(damage)
                        pos = self.pos
                        ans = ''
                        if not self.dungeon[pos[1]][pos[0]] or self.dungeon[pos[1]][pos[0]][1] != name:
                            ans = f'No {name} here'
                        else:
                            hp, name, _ = self.dungeon[pos[1]][pos[0]]
                            ans = f"Attacked {name} with {weapon}, damage {damage} hp"
                            hp = max(hp - damage, 0)
                            self.dungeon[pos[1]][pos[0]][0] = hp
                            if hp:
                                ans += f'\n{name} now has {hp}'
                            else:
                                ans += f'\n{name} died'
                                self.dungeon[pos[1]][pos[0]] = 0
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                        if hp:
                            ans = f"Player {me} attacked {name} with {weapon}, dealing {damage} damage. Now {name} has {hp} hp."
                        else:
                            ans = f"Player {me} attacked {name} with {weapon}, dealing fatal {damage} damage. {name} is dead now."
                        for out in self.clients.values():
                                if out != me:
                                    print('MULTISENDED>>', [ans])
                                    await out.put(ans)
                    elif message == "quit":
                        ans = "До новых встреч на просторах MUD!"
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        ans = f"Пользователь {me} покинул подземелье..."
                        for out in self.clients.values():
                            if out != me:
                                print('MULTISENDED>>', [ans])
                                await out.put(ans)
                        del self.clients[me]
                        self.names.remove(me)
                        me = None
                    elif message == 'help':
                        ans = '''Команды:
                        help — вы здесь
                        up \\ down \\ left \\ right — движения по данжу
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
            del self.clients[me]
            self.names.remove(me)
        writer.close()
        await writer.wait_closed()

async def main():
    m = MUDServer()
    server = await asyncio.start_server(m.server, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
