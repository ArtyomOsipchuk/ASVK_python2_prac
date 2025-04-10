#!/usr/bin/env python3
"""Setup of server for Multi User Dungeon."""
import asyncio
import cowsay
import shlex
from io import StringIO
from random import choice
import threading
import time
import socket


class MUDServer:
    """Server for Multy User Dungeon."""

    running = True
    clients = {}
    names = set()
    dungeon = [[0 for i in range(10)] for j in range(10)]
    # dungeon[y][x] = hp, name, message
    pos = {}
    # pos = {name: [x, y]}
    monsters_pos = set()
    # monsters_pos = set(tuple(x, y))

    def wandering_monster(self, admin_name, timeout):
        """Move monster randomly."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 1337))
        msg = f"{admin_name}\n"
        s.sendall(bytes(msg.encode()))
        s.recv(4096).rstrip().decode()
        del self.pos[admin_name]
        while self.running:
            time.sleep(timeout)
            if not self.monsters_pos:
                continue
            fight = []
            while self.running:
                pos = choice([i for i in self.monsters_pos])
                vectors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                verb = ["up", "down", "right", "left"]
                x, y = choice(vectors)
                verb = verb[vectors.index((x, y))]
                x, y = (pos[0] + x) % 10, (pos[1] + y) % 10
                if self.dungeon[y][x] == 0:
                    self.dungeon[y][x] = self.dungeon[pos[1]][pos[0]]
                    self.dungeon[pos[1]][pos[0]] = 0
                    self.monsters_pos.remove(pos)
                    self.monsters_pos.add((x, y))
                    for player, cell in self.pos.items():
                        if cell == [x, y]:
                            fight.append(player)
                    break
            msg = f"sudo {self.dungeon[y][x][1]} {verb} {' '.join(fight)}\n"
            s.sendall(bytes(msg.encode()))

    def encounter(self, y, x):
        """Render monster encounders by python-cowsay module."""
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
        """Host async server to handle messages."""
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
                            ans = "Отказано в подключении. Такой пользователь уже есть\n"
                            print('SENDED>>', [ans])
                            writer.write(bytes(ans.encode()))
                            break
                        else:
                            me = message
                            self.pos[me] = [0, 0]
                            self.clients[me] = queue
                            self.names.add(message)
                            ans = f"Добро пожаловать в MUD, {me}!\n"
                            print('SENDED>>', [ans])
                            writer.write(bytes(ans.encode()))
                            await writer.drain()
                            for out in self.clients.values():
                                if out != self.clients[me]:
                                    ans = f"{me} присоединился к рейду!\n"
                                    print('MULTISENDED>>', [ans])
                                    await out.put(ans)
                    elif message.startswith('move '):
                        move, x, y = shlex.split(message)
                        y, x = int(y), int(x)
                        self.pos[me] = [(self.pos[me][0] + x) % 10, (self.pos[me][1] + y) % 10]
                        pos = self.pos[me]
                        ans = f"Moved to {pos[0]} {pos[1]}\n"
                        if self.dungeon[pos[1]][pos[0]]:
                            ans += "Moved to ...\n"
                            ans += self.encounter(pos[1], pos[0]) + '\n'
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                    elif message.startswith('addmon '):
                        # "addmon {name} {hp} {y} {x} {hello}\n"
                        addmob, name, hp, y, x, hello = shlex.split(message)
                        y, x = int(y), int(x)
                        ans = f"Added monster {name} to ({x}, {y}) saying {hello}\n"
                        self.monsters_pos.add((x, y))
                        if self.dungeon[y][x]:
                            ans += "\nReplaced the old monster\n"
                        self.dungeon[y][x] = [int(hp), name, hello]
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                        ans = f"Player {me} added monster {name} to ({x}, {y}) saying {hello}\n"
                        for out in self.clients.values():
                            if out != self.clients[me]:
                                print('MULTISENDED>>', [ans])
                                await out.put(ans)
                    elif message.startswith('attack '):
                        attack, name, damage, weapon = shlex.split(message)
                        damage = int(damage)
                        pos = self.pos[me]
                        ans = ''
                        if not self.dungeon[pos[1]][pos[0]] or self.dungeon[pos[1]][pos[0]][1] != name:
                            ans = f'No {name} here\n'
                            print('SENDED>>', [ans])
                            writer.write(bytes(ans.encode()))
                            await writer.drain()
                        else:
                            hp, name, _ = self.dungeon[pos[1]][pos[0]]
                            ans = f"Attacked {name} with {weapon}, damage {damage} hp\n"
                            hp = max(hp - damage, 0)
                            self.dungeon[pos[1]][pos[0]][0] = hp
                            if hp:
                                ans += f'{name} now has {hp}\n'
                            else:
                                ans += f'{name} died\n'
                                self.monsters_pos.remove((pos[0], pos[1]))
                                self.dungeon[pos[1]][pos[0]] = 0
                            print('SENDED>>', [ans])
                            writer.write(bytes(ans.encode()))
                            await writer.drain()
                            if hp:
                                ans = f"Player {me} attacked {name} with {weapon}, dealing {damage} damage. Now {name} has {hp} hp.\n"
                            else:
                                ans = f"Player {me} attacked {name} with {weapon}, dealing fatal {damage} damage. {name} is dead now.\n"
                            for out in self.clients.values():
                                if out != me:
                                    print('MULTISENDED>>', [ans])
                                    await out.put(ans)
                    elif message == "quit":
                        ans = "До новых встреч на просторах MUD!\n"
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        ans = f"Пользователь {me} покинул подземелье...\n"
                        for out in self.clients.values():
                            print('MULTISENDED>>', [ans])
                            await out.put(ans)
                        del self.clients[me]
                        self.names.remove(me)
                        me = None
                        return
                    elif message.startswith("sudo "):
                        sudo, name, verb, *names = shlex.split(message)
                        ans = f"{name} moved one cell {verb}\n"
                        for out in self.clients.values():
                            print('MULTISENDED>>', [ans])
                            await out.put(ans)
                        if names:
                            x, y = self.pos[names[0]]
                            ans_fight = '\n' + self.encounter(y, x)
                            for i in names:
                                print('SENDED>>', [ans_fight])
                                await self.clients[i].put(ans_fight)
                    elif message.startswith("sayall "):
                        sayall, *msg = shlex.split(message)
                        ans = f"{me}: {msg[0]}\n"
                        for out in self.clients.values():
                            print('MULTISENDED>>', [ans])
                            await out.put(ans)
                    elif message == 'help':
                        ans = '''Команды:
                        help — вы здесь
                        up \\ down \\ left \\ right — движения по данжу
                        attack <name> [with <weapon>] — атаковать монстра
                        addmon — добавить монстра
                        sayall — <строка> (либо одно слово, либо строка в кавычках)
                        quit — выбраться из подземелья\n'''
                        print('SENDED>>', [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                    else:
                        ans = "Неизвестная команда.\
                                Введите 'help' для вывода списка команд.\n"
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
        self.running = False
        await writer.wait_closed()


async def main():
    """Start server on localhost."""
    m = MUDServer()
    server = await asyncio.start_server(m.server, '0.0.0.0', 1337)
    timeout = 10
    admin_name = 'admin'
    # Бродячие монстры выключены для режима отладки
    # timer = threading.Thread(target=m.wandering_monster, args=(admin_name, timeout))
    # timer.start()
    async with server:
        await server.serve_forever()
    timer.cancel()

if __name__ == "__main__":
    asyncio.run(main())
