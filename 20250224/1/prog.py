import cowsay

dungeon = [[0 for i in range(10)] for j in range(10)]
pos = [0, 0]

def encounter(y, x):
    print(cowsay.cowsay(dungeon[y][x]))

while (c := input()):
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
        case ["addmon", x, y, hello]:
            movement = False
            if not (x.isdigit() and y.isdigit()):
                "Invalid arguments"
                break
            y, x = int(y), int(x)
            print(f"Added monster to ({x}, {y}) saying {hello}")
            if dungeon[y][x]:
                print("Replaced the old monster")
            dungeon[y][x] = hello
        case _:
            movement = False
            print("Invalid command")
    if not movement:
        continue
    if dungeon[pos[1]][pos[0]]:
        print(f"Moved to ...")
        encounter(pos[1], pos[0])
