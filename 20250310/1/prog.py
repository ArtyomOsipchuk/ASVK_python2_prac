import cowsay
import sys
import cmd
from io import StringIO
import shlex

dungeon = [[0 for i in range(10)] for j in range(10)]

def encounter(y, x):
    jgsbat = cowsay.read_dot_cow(StringIO("""    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\ \b\\--//|.'-._  (
     )'   .'\\/o\\/o\\/'.   `(
      ) .' . \\====/ . '. (
       )  / <<    >> \\  (
        '-._/``  ``\\_.-'
  jgs     __\\ \b\\'--'//__
         (((""`  `"")))"""))
    hp, name, message = dungeon[y][x]
    if name == "jgsbat":
        print(cowsay.cowsay(message, cowfile=jgsbat))
    else:
        print(cowsay.cowsay(message, cow=name))

class MUD(cmd.Cmd):
    print("<<< Welcome to Python-MUD 0.1 >>>")
    prompt = ">>> "
    pos = [0, 0]

    def do_up(self, arg):
        '''moves character up'''
        self.pos[1] = (self.pos[1] + 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")  
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])

    def do_down(self, arg):
        '''moves character down'''
        self.pos[1] = (self.pos[1] - 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")  
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])

    def do_left(self, arg):
        '''moves character left'''
        self.pos[0] = (self.pos[0] - 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")  
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])
    
    def do_right(self, arg):
        '''moves character right'''
        self.pos[0] = (self.pos[0] + 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")  
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])

    def do_addmon(self, arg):
        '''addmon <>'''
        err_parse = True
        print(arg)
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
                                        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
                                        if dungeon[y][x]:
                                            print("Replaced the old monster")
                                        dungeon[y][x] = [hp, name, hello]
        if err_parse:
                print("Invalid arguments")

    def do_EOF(self, arg):
        return 1

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
    MUD().cmdloop()
