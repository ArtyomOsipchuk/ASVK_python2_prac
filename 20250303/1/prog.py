import cowsay
import sys
from io import StringIO

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
    name, message = dungeon[y][x]
    if name == "jgsbat":
        print(cowsay.cowsay(message, cowfile=jgsbat))
    else:
        print(cowsay.cowsay(message, cow=name))

while (c := sys.stdin.readline()):
    movement = True
    c = str(c).split()
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
        case ["addmon", x, y, name, hello]:
            movement = False
            if x.isdigit() and y.isdigit() and name in cowsay.list_cows() + ["jgsbat"]:
              y, x = int(y), int(x)
              print(f"Added monster {name} to ({x}, {y}) saying {hello}")
              if dungeon[y][x]:
                  print("Replaced the old monster")
              dungeon[y][x] = [name, hello]
            else:
              print("Invalid arguments")
        case _:
            movement = False
            print("Invalid command")
    if not movement:
        continue
    if dungeon[pos[1]][pos[0]]:
        print(f"Moved to ...")
        encounter(pos[1], pos[0])
