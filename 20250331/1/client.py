import cmd
import threading
import time
import readline
import asyncio
import sys
import socket
import shlex
import cowsay

class CowNetcat(cmd.Cmd):
    promt = '>> '
    running = True
    
    def do_up(self, arg):
        '''moves character up'''
        msg = f"move 0 1\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)

    def do_down(self, arg):
        '''moves character down'''
        msg = f"move 0 -1\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)

    def do_left(self, arg):
        '''moves character left'''
        msg = f"move -1 0\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)

    def do_right(self, arg):
        '''moves character right'''
        msg = f"move 1 0\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)

    def do_help(self, arg):
        '''returns help message'''
        msg = f"help\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)

    def do_quit(self, arg):
        '''quit dungeon'''
        msg = f"quit\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)
        self.running = False
        return 1

    def do_EOF(self, arg):
        'End Of File'
        msg = f"quit\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)
        self.running = False
        return 1

    def do_attack(self, arg):
        '''attack <имя монстра> with <имя оружия>'''
        arg = arg.split()
        if len(arg) < 1 or len(arg) == 2:
            print("Invalid arguments")
            return
        name = arg[0]
        if len(arg) > 1 and arg[1] != 'with':
            print("Invalid arguments")
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
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)

    def do_addmon(self, arg):
        '''addmon <monster_name> hello <hello_string> hp <hitpoints> coords <x> <y>'''
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
                                    if name in cowsay.list_cows() + ["jgsbat"]:
                                        err_parse = False
        if err_parse:
                print("Invalid arguments")
                return
        msg = f"addmon {name} {hp} {y} {x} '{hello}'\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        print(ans)

    def complete_attack(self, text, line, begidx, endidx):
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
            return [weapons[(weapons.index(words[-1][:-1]) + 1) % len(weapons)]]
        elif len(words) == 4 and 'with' in words:
            DICT = weapons
        return [c for c in DICT if c.startswith(text)]

    def complete_addmon(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        DICT = []
        if len(words) > 2:
            if "hello" in words:
                words[words.index("hello") + 1] = "-"
            if "hp" not in words:
                DICT.append('hp')
            if "hello" not in words:
                DICT.append('hello')
            if "coords" not in words:
                DICT.append('coords')
        if len(words) == 2:
            DICT.extend(["jgsbat"] + cowsay.list_cows())
        return [c for c in DICT if c.startswith(text)]

def spam(cmdline, timeout):
    while cmdline.running:
        time.sleep(timeout)
        ans = s.recv(1024).rstrip().decode()
        print(ans)
        print(f"\n{cmdline.prompt}{readline.get_line_buffer()}", end="", flush=True)


if __name__ == '__main__':
    host = "localhost" #if len(sys.argv) < 2 else sys.argv[1]
    port = 1337 #if len(sys.argv) < 3 else int(sys.argv[2])
    if len(sys.argv) < 2:
        print("Usage: python3 mymud.py <nickname>\nУкажите никнейм, чтобы мы знали, кем гордиться!")
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        msg = f"{sys.argv[1]}\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(4096).rstrip().decode()
        print(ans)
        if ans != 'Отказано в подключении. Такой пользователь уже есть':
            cmdline = CowNetcat()
            timer = threading.Thread(target=spam, args=(cmdline, 5))
            timer.start()
            cmdline.cmdloop()
