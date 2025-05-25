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
import gettext
import locale as loc
import os
import sys
from pathlib import Path


class MUDServer:
    """Server for Multy User Dungeon."""

    timeout = 10
    admin_name = "ADMIN"
    running = True
    clients = {}
    names = set()
    dungeon = [[0 for i in range(10)] for j in range(10)]
    # dungeon[y][x] = hp, name, message
    pos = {}
    # pos = {queue_name: [x, y]}
    locales = {}
    # locales = {name: locale}
    monsters_pos = set()
    # monsters_pos = set(tuple(x, y))
    locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
    LOCALES = {
        "ru_RU.UTF-8": gettext.translation("MUD", locales_dir, ["ru"]),
        "en_US.UTF-8": gettext.NullTranslations(),
    }

    def _(self, text, locale):
        """Return translated text."""
        return self.LOCALES[locale].gettext(text)

    def ngettext(self, text, ntext, n, locale):
        """Return translated text with plurals."""
        return self.LOCALES[locale].ngettext(text, ntext, n)

    def __init__(self, *args):
        """Init method."""
        self.timer = threading.Thread(
            target=self.wandering_monster, args=(self.admin_name, self.timeout)
        )
        self.timer.start()
        self.pause_wandering = threading.Event()
        super().__init__(*args)

    def wandering_monster(self, admin_name, timeout):
        """Move monster randomly."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 1337))
        msg = f"{admin_name}\n"
        s.sendall(bytes(msg.encode()))
        s.recv(4096).rstrip().decode()
        del self.pos[admin_name]
        while self.running:
            time.sleep(timeout)
            if self.pause_wandering.is_set():
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
            else:
                time.sleep(timeout * 2)

    def encounter(self, y, x):
        """Render monster encounders by python-cowsay module."""
        hp, name, message = self.dungeon[y][x]
        if name == "jgsbat":
            jgsbat = cowsay.read_dot_cow(
                StringIO(
                    """    ,_                    _,
            ) '-._  ,_    _,  _.-' (
            )  _.-'.|\\ \b\\--//|.'-._  (
             )'   .'\\/o\\/o\\/'.   `(
              ) .' . \\====/ . '. (
               )  / <<    >> \\  (
                '-._/``  ``\\_.-'
          jgs     __\\ \b\\'--'//__
                 (((""`  `"")))"""
                )
            )
            return cowsay.cowsay(message, cowfile=jgsbat)
        elif name == "gamer":
            gamer_dir = Path(__file__).parent / ".." / "custom_monsters" / "gamer.txt"
            with open(gamer_dir) as f:
                gamer = cowsay.read_dot_cow(StringIO("".join(f.readlines())))
            return cowsay.cowsay(message, cowfile=gamer)
        else:
            return cowsay.cowsay(message, cow=name)

    async def server(self, reader, writer):
        """Host async server to handle messages."""
        me = None
        locale = "en_US.UTF-8"
        queue = asyncio.Queue()
        send = asyncio.create_task(reader.readline())
        receive = asyncio.create_task(queue.get())
        while not reader.at_eof():
            done, pending = await asyncio.wait(
                [send, receive], return_when=asyncio.FIRST_COMPLETED
            )
            for q in done:
                if q is send:
                    send = asyncio.create_task(reader.readline())
                    message = q.result().decode().strip()
                    print("RECEIVED>>", [message])
                    if not message:
                        continue
                    if not me:
                        if message in self.names:
                            ans = self._(
                                "Connection refused. User with nick {} already exists\n",
                                locale,
                            ).format(message)
                            print("SENDED>>", [ans])
                            writer.write(bytes(ans.encode()))
                            break
                        else:
                            me = message
                            self.pos[me] = [0, 0]
                            self.clients[me] = queue
                            self.locales[queue] = locale
                            self.names.add(message)
                            ans = self._("Welcome to MUD, {}!\n", locale).format(me)
                            print("SENDED>>", [ans])
                            writer.write(bytes(ans.encode()))
                            await writer.drain()
                            for out in self.clients.values():
                                if out != self.clients[me]:
                                    ans = self._(
                                        "{} connected to raid!\n", self.locales[out]
                                    ).format(me)
                                    print("MULTISENDED>>", [ans])
                                    await out.put(ans)
                    elif message.startswith("move "):
                        move, x, y = shlex.split(message)
                        y, x = int(y), int(x)
                        self.pos[me] = [
                            (self.pos[me][0] + x) % 10,
                            (self.pos[me][1] + y) % 10,
                        ]
                        pos = self.pos[me]
                        ans = self._("Moved to {} {}\n", locale).format(pos[0], pos[1])
                        if self.dungeon[pos[1]][pos[0]]:
                            ans += self._("Moved to ...\n", locale)
                            ans += self.encounter(pos[1], pos[0]) + "\n"
                        print("SENDED>>", [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                    elif message.startswith("locale "):
                        locl, new_locale = shlex.split(message)
                        if new_locale in self.LOCALES:
                            locale = new_locale
                            ans = self._("Set up locale: {}\n", locale).format(locale)
                            self.locales[self.clients[me]] = locale
                        else:
                            ans = self._(
                                "Only ru_RU.UTF-8 and en_EN.UTF-8 locales are available\n",
                                locale,
                            )
                        print("SENDED>>", [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                    elif message.startswith("addmon "):
                        # "addmon {name} {hp} {y} {x} {hello}\n"
                        addmob, name, hp, y, x, hello = shlex.split(message)
                        y, x = int(y), int(x)
                        ans = self._(
                            "Added monster {} to ({}, {}) saying {}\n", locale
                        ).format(name, x, y, hello)
                        self.monsters_pos.add((x, y))
                        if self.dungeon[y][x]:
                            ans += self._("\nReplaced the old monster\n", locale)
                        self.dungeon[y][x] = [int(hp), name, hello]
                        print("SENDED>>", [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                        for out in self.clients.values():
                            if out != self.clients[me]:
                                ans = self.ngettext(
                                    "Player {} added monster {} with {} hitpoint to ({}, {}) saying {}\n",
                                    "Player {} added monster {} with {} hitpoints to ({}, {}) saying {}\n",
                                    hp,
                                    self.locales[out],
                                ).format(me, name, hp, x, y, hello)
                                print("MULTISENDED>>", [ans])
                                await out.put(ans)
                    elif message.startswith("movemonsters "):
                        movemonsters, option = shlex.split(message)
                        for out in self.clients.values():
                            if option == "off":
                                self.pause_wandering.clear()
                                ans = self._(
                                    "Moving monsters: off\n", self.locales[out]
                                )
                            else:
                                self.pause_wandering.set()
                                ans = self._("Moving monsters: on\n", self.locales[out])
                            print("MULTISENDED>>", [ans])
                            await out.put(ans)
                    elif message.startswith("attack "):
                        attack, name, damage, weapon = shlex.split(message)
                        damage = int(damage)
                        pos = self.pos[me]
                        ans = ""
                        if (
                            not self.dungeon[pos[1]][pos[0]]
                            or self.dungeon[pos[1]][pos[0]][1] != name
                        ):
                            ans = self._("No {} here\n", locale).format(name)
                            print("SENDED>>", [ans])
                            writer.write(bytes(ans.encode()))
                            await writer.drain()
                        else:
                            hp, name, _ = self.dungeon[pos[1]][pos[0]]
                            ans = self.ngettext(
                                "Attacked {} with {}, damage {} hitpoint\n",
                                "Attacked {} with {}, damage {} hitpoints\n",
                                damage,
                                locale,
                            ).format(name, weapon, damage)
                            hp = max(hp - damage, 0)
                            self.dungeon[pos[1]][pos[0]][0] = hp
                            if hp:
                                ans += self.ngettext(
                                    "{} now has {} hitpoint\n",
                                    "{} now has {} hitpoints\n",
                                    hp,
                                    locale,
                                ).format(name, hp)
                            else:
                                ans += self._("{} died\n", locale).format(name)
                                self.monsters_pos.remove((pos[0], pos[1]))
                                self.dungeon[pos[1]][pos[0]] = 0
                            print("SENDED>>", [ans])
                            writer.write(bytes(ans.encode()))
                            await writer.drain()
                            for out in self.clients.values():
                                if out != self.clients[me]:
                                    if hp:
                                        ans = self.ngettext(
                                            "Player {} attacked {} with {}, dealing {} point of damage.\n",
                                            "Player {} attacked {} with {}, dealing {} points of damage.\n",
                                            damage,
                                            self.locales[out],
                                        ).format(
                                            me, name, weapon, damage
                                        ) + self.ngettext(
                                            "Now {} has {} hitpoint.\n",
                                            "Now {} has {} hitpoints.\n",
                                            hp,
                                            self.locales[out],
                                        ).format(
                                            name, hp
                                        )
                                    else:
                                        ans = self.ngettext(
                                            "Player {} attacked {} with {}, dealing fatal {} point of damage. {} is dead now.\n",
                                            "Player {} attacked {} with {}, dealing fatal {} points of damage. {} is dead now.\n",
                                            damage,
                                            self.locales[out],
                                        ).format(me, name, weapon, damage, name)
                                    print("MULTISENDED>>", [ans])
                                    await out.put(ans)
                    elif message == "quit":
                        ans = self._(
                            "Goodbye, {}! See you later in fields of MUD!\n", locale
                        ).format(me)
                        print("SENDED>>", [ans])
                        writer.write(bytes(ans.encode()))
                        for out in self.clients.values():
                            ans = self._(
                                "User {} leave the dungeon...\n", self.locales[out]
                            ).format(me)
                            print("MULTISENDED>>", [ans])
                            await out.put(ans)
                        del self.clients[me]
                        self.names.remove(me)
                        me = None
                        return
                    elif message.startswith("sudo "):
                        sudo, name, verb, *names = shlex.split(message)
                        for out in self.clients.values():
                            ans = self._(
                                "{} moved one cell {}\n", self.locales[out]
                            ).format(name, verb)
                            print("MULTISENDED>>", [ans])
                            await out.put(ans)
                        if names:
                            x, y = self.pos[names[0]]
                            ans_fight = "\n" + self.encounter(y, x)
                            for i in names:
                                print("SENDED>>", [ans_fight])
                                await self.clients[i].put(ans_fight)
                    elif message.startswith("sayall "):
                        sayall, *msg = shlex.split(message)
                        ans = f"{me}: {msg[0]}\n"
                        for out in self.clients.values():
                            print("MULTISENDED>>", [ans])
                            await out.put(ans)
                    elif message == "help":
                        ans = self._(
                            """Commands:
                            help - you're here
                            up \\ down \\ left \\ right — movement
                            attack <name> [with <weapon>] — attack monster
                            addmon <name> hello <message> hp <hp> coords <x> <y> — add monster
                            sayall <string> — (use brackets if not one word)
                            quit — leave the dungeon\n""",
                            locale,
                        )
                        print("SENDED>>", [ans])
                        writer.write(bytes(ans.encode()))
                        await writer.drain()
                    else:
                        ans = self._(
                            "Unknown command.\
                                Enter 'help' for command list.\n",
                            locale,
                        )
                        print("SENDED>>", [ans])
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
    server = await asyncio.start_server(m.server, "0.0.0.0", 1337)
    async with server:
        await server.serve_forever()


def start_server():
    """Start server for testing with no output."""
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")
    asyncio.run(main())

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
