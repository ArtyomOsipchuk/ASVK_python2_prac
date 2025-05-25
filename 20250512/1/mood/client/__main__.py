#!/usr/bin/env python3
"""Client for Multi User Dungeon."""
import cmd
import threading
import time
import readline
import sys
import socket
import shlex
import cowsay
import argparse
import os
import webbrowser
from pathlib import Path
from .__common__ import *

if 'libedit' in readline.__doc__:
    # print("Found libedit readline")
    readline.parse_and_bind("bind ^I rl_complete")
else:
    # print("Found gnu readline")
    readline.parse_and_bind("tab: complete")


class CowNetcat(cmd.Cmd):
    """Netcat client version for MUD."""

    prompt = '>> '
    running = True
    
    def __init__(self, socket, command_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s = socket
        if command_file:
            self.prompt = ''
            self.onecmd = self._onecmd
            self.use_rawinput = False
            self.stdin = command_file

    def _onecmd(self, line):
        time.sleep(1)
        return super().onecmd(line)

    def do_documentation(self, arg):
        """Open documentation in browser."""
        doc_path = Path(__file__).parent.parent.parent / 'mood' / 'docs' / 'html' / 'index.html'
        webbrowser.open(f'file://{doc_path.resolve()}')

    def do_locale(self, arg):
        """Set locale."""
        msg = f"locale {arg}\n"
        self.s.sendall(bytes(msg.encode()))

    def do_movemonsters(self, arg):
        """Wander monsters on/off."""
        arg = arg.split()
        if len(arg) > 1:
            print('Usage: movemonsters <on/off>')
            return
        msg = f"movemonsters {arg[0]}\n"
        self.s.sendall(bytes(msg.encode()))

    def do_sayall(self, arg):
        """Send public message."""
        msg = f"sayall {arg}\n"
        self.s.sendall(bytes(msg.encode()))

    def do_up(self, arg):
        """Move character up."""
        msg = "move 0 1\n"
        self.s.sendall(bytes(msg.encode()))

    def do_down(self, arg):
        """Move character down."""
        msg = "move 0 -1\n"
        self.s.sendall(bytes(msg.encode()))

    def do_left(self, arg):
        """Move character left."""
        msg = "move -1 0\n"
        self.s.sendall(bytes(msg.encode()))

    def do_right(self, arg):
        """Move character right."""
        msg = "move 1 0\n"
        self.s.sendall(bytes(msg.encode()))

    def do_help(self, arg):
        """Return help message."""
        msg = "help\n"
        self.s.sendall(bytes(msg.encode()))

    def do_quit(self, arg):
        """Quit dungeon."""
        msg = "quit\n"
        self.s.sendall(bytes(msg.encode()))
        #ans = s.recv(1024).rstrip().decode()
        #print(ans)
        self.running = False
        return True

    def do_EOF(self, arg):
        """End Of File."""
        msg = 'quit\n'
        s.sendall(bytes(msg.encode()))
        self.running = False
        return True

    def do_attack(self, arg):
        """Use: attack <name> with <weapon>."""
        arg = arg.split()
        if len(arg) > 3:
            print("Too many arguments")
            return
        if len(arg) < 1:
            print("Specify monster name")
            return 
        name = arg[0]
        if len(arg) > 1 and arg[1] != 'with':
            print("Invalid arguments")
            return
        if len(arg) == 2:
            print("Attack with what?")
            return
        if len(arg) == 1:
            ww = 'sword'
            damage = 10
        else:
            weapons = ['sword', 'spear', 'axe']
            if arg[2] in weapons:
                ww = arg[2]
            else:
                print("Unknown weapon")
                return
        if ww == 'spear':
            damage = 15
        elif ww == 'axe':
            damage = 20
        msg = f"attack {name} {damage} {ww}\n"
        self.s.sendall(bytes(msg.encode()))

    def do_addmon(self, arg):
        """Use: addmon <name> hello <message> hp <hitpoints> coords <x> <y>."""
        err_parse = True
        if len(arg.split()) < 2:
            print("Invalid arguments")
            return
        name, *pars = shlex.split(arg)
        if len(pars) == 7:
            i = pars.index("hello")
            if -1 < i < 6:
                hello = pars[i + 1]
                pars[i + 1] = "-"
                i = pars.index("hp")
                if -1 < i < 6:
                    hp = pars[i + 1]
                    if hp.isdigit():
                        hp = int(hp)
                        if hp > 0:
                            i = pars.index("coords")
                            if -1 < i < 5:
                                x, y = pars[i + 1], pars[i + 2]
                                if x.isdigit() and y.isdigit():
                                    y, x = int(y), int(x)
                                    if name in cowsay.list_cows() + ["jgsbat", "gamer"]:
                                        err_parse = False
        if err_parse:
            print("Invalid arguments")
            return
        msg = f"addmon {name} {hp} {y} {x} '{hello}'\n"
        self.s.sendall(bytes(msg.encode()))

    def complete_movemonsters(self, text, line, begidx, endidx):
        """Move monsters func completion."""
        words = (line[:endidx] + ".").split()
        DICT = ['on', 'off']
        if len(words) == 2 and words[-1][:-1] in DICT:
            return [DICT[(DICT.index(words[-1][:-1]) + 1) % len(DICT)]]
        return [c for c in DICT if c.startswith(text)]
    
    def complete_locale(self, text, line, begidx, endidx):
        """Set up locale func completion."""
        words = (line[:endidx] + ".").split()
        DICT = ['ru_RU.UTF-8', 'en_US.UTF-8']
        if len(words) == 2 and words[-1][:-1] in DICT:
            return [DICT[(DICT.index(words[-1][:-1]) + 1) % len(DICT)]]
        return [c for c in DICT if c.startswith(text)]

    def complete_attack(self, text, line, begidx, endidx):
        """Attack func completion."""
        words = (line[:endidx] + ".").split()
        DICT = []
        cows = ["jgsbat"] + cowsay.list_cows()
        weapons = ["sword", "spear", "axe"]
        if len(words) == 2 and words[-1][:-1] in cows:
            return [cows[(cows.index(words[-1][:-1]) + 1) % len(cows)]]
        elif len(words) == 2:
            DICT = cows
        elif len(words) == 3:
            DICT = ['with']
        elif len(words) == 4 and words[-1][:-1] in weapons:
            w = weapons
            return [w[(w.index(words[-1][:-1]) + 1) % len(w)]]
        elif len(words) == 4 and 'with' in words:
            DICT = weapons
        return [c for c in DICT if c.startswith(text)]

    def complete_addmon(self, text, line, begidx, endidx):
        """Addmon func completion."""
        words = (line[:endidx] + ".").split()
        DICT = []
        cows = ["jgsbat", 'gamer'] + cowsay.list_cows()
        if len(words) > 2:
            if "hello" in words:
                words[words.index("hello") + 1] = "-"
            if "hp" not in words:
                DICT.append('hp')
            if "hello" not in words:
                DICT.append('hello')
            if "coords" not in words:
                DICT.append('coords')
        if len(words) == 2 and words[-1][:-1] in cows:
            return [cows[(cows.index(words[-1][:-1]) + 1) % len(cows)]]
        elif len(words) == 2:
            DICT.extend(cows)
        return [c for c in DICT if c.startswith(text)]


def spam(s, cmdline, timeout, testing_mode=False):
    """Readline buffer flushing."""
    while cmdline.running:
        time.sleep(timeout)
        ans = s.recv(4096).rstrip().decode()
        print("\n" + ans, end='')
        if not testing_mode:
            print(f"\n{cmdline.prompt}{readline.get_line_buffer()}",
                  end="", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='python3 -m mood.client',
                    description='Client for MultiUserDungeon',
                    epilog='Cool game for cool students.')
    parser.add_argument("username", help="Никнейм, чтобы мы знали, кем гордиться!")
    parser.add_argument("host", nargs='?', default='localhost', help="Адрес хост-сервера")
    parser.add_argument("port", nargs='?', type=int, default=1337, help="Порт хост-сервера")
    parser.add_argument("--file", default=None, help="Получение команд из командного файла")
    args = parser.parse_args()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((args.host, args.port))
        msg = f"{args.username}\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(4096).rstrip().decode()
        print(ans)
        if ans != f'Connection refused. User with nick {args.username} already exists':
            if args.file:
                if not os.path.exists(args.file):
                    print(f"Error: file '{args.file}' not found")
                elif not args.file.endswith('.mood'):
                    print("Error: no file formats except .mood")
                args.file = open(args.file, 'r')
            cmdline = CowNetcat(s, command_file=args.file)
            timer = threading.Thread(target=spam, args=(s, cmdline, REFRESH_TIME))
            timer.start()
            cmdline.cmdloop()
            timer.join()
            s.close()
    except ConnectionRefusedError:
        print("Connection refused.")
