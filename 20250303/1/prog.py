import cowsay
import sys
from io import StringIO
import shlex

dungeon = [[0 for i in range(10)] for j in range(10)]
pos = [0, 0]

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

print("<<< Welcome to Python-MUD 0.1 >>>")
while (c := sys.stdin.readline()):
    c = shlex.split(c)
    movement = True
    match c:
        case ["up"]:
            pos[1] = (pos[1] + 1) % 10
            print(f"Moved to ({pos[0]}, {pos[1]})")  
        case ["down"]:
            pos[1] = (pos[1] - 1) % 10
            print(f"Moved to ({pos[0]}, {pos[1]})") 
        case ["right"]:
            pos[0] = (pos[0] + 1) % 10
            print(f"Moved to ({pos[0]}, {pos[1]})") 
        case ["left"]:
            pos[0] = (pos[0] - 1) % 10
            print(f"Moved to ({pos[0]}, {pos[1]})") 
        case ["addmon", name, *pars]:
            err_parse = True
            movement = False
            if len(pars) == 7:
                i = pars.index("coords")
                if -1 < i < 5:
                    x, y = pars[i + 1], pars[i + 2]
                    if x.isdigit() and y.isdigit():
                        y, x = int(y), int(x)
                        i = pars.index("hp")
                        if -1 < i < 6:
                            hp = pars[i + 1]
                            if hp.isdigit():
                                hp = int(hp)
                                if hp > 0:
                                    i = pars.index("hello")
                                    if -1 < i < 6:
                                        hello = pars[i + 1]
                                        if name in cowsay.list_cows() + ["jgsbat"]:
                                            err_parse = False
                                            print(f"Added monster {name} to ({x}, {y}) saying {hello}")
                                            if dungeon[y][x]:
                                                print("Replaced the old monster")
                                            dungeon[y][x] = [hp, name, hello]
            if err_parse:
                print("Invalid arguments")
        case _:
            movement = False
            print("Invalid command")
    if not movement:
        continue
    if dungeon[pos[1]][pos[0]]:
        print(f"Moved to ...")
        encounter(pos[1], pos[0])
