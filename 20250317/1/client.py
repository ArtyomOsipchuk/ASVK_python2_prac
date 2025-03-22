import sys
import socket
import cowsay
import cmd
from io import StringIO
import shlex
import readline

class MUDClient(cmd.Cmd):
    print("<<< Welcome to Python-MUD 0.1 >>>")
    prompt = ">>> "

    def _pos(self):
        msg = f"pos\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        return [int(i) for i in ans.split()]
    
    def encounter(self, name, message, y, x):
        jgsbat = cowsay.read_dot_cow(StringIO("""    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\ \b\\--//|.'-._  (
     )'   .'\\/o\\/o\\/'.   `(
      ) .' . \\====/ . '. (
       )  / <<    >> \\  (
        '-._/``  ``\\_.-'
  jgs     __\\ \b\\'--'//__
         (((""`  `"")))"""))
        if name == "jgsbat":
            print(cowsay.cowsay(message, cowfile=jgsbat))
        else:
            print(cowsay.cowsay(message, cow=name))

    def do_up(self, arg):
        '''moves character up'''
        pos = self._pos()
        pos[1] = (pos[1] + 1) % 10
        print(f"Moved to ({pos[0]}, {pos[1]})")
        msg = f"move {pos[0]} {pos[1]}\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        if ans != 'nobody':
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], pos[1], pos[0])

    def do_down(self, arg):
        '''moves character down'''
        pos = self._pos()
        pos[1] = (pos[1] - 1) % 10
        print(f"Moved to ({pos[0]}, {pos[1]})")
        msg = f"move {pos[0]} {pos[1]}\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        if ans != 'nobody':
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], pos[1], pos[0])

    def do_left(self, arg):
        '''moves character left'''
        pos = self._pos()
        pos[0] = (pos[0] - 1) % 10
        print(f"Moved to ({pos[0]}, {pos[1]})")
        msg = f"move {pos[0]} {pos[1]}\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        if ans != 'nobody':
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], pos[1], pos[0])

    def do_right(self, arg):
        '''moves character right'''
        pos = self._pos()
        pos[0] = (pos[0] + 1) % 10
        print(f"Moved to ({pos[0]}, {pos[1]})")
        msg = f"move {pos[0]} {pos[1]}\n"
        s.sendall(bytes(msg.encode()))
        ans = s.recv(1024).rstrip().decode()
        if ans != 'nobody':
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], pos[1], pos[0])

    def do_EOF(self, arg):
        '''End Of File AKA exit game'''
        return 1

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

if __name__ == '__main__':
    host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
    port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    MUDClient().cmdloop()
