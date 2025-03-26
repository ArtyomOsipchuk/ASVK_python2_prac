import asyncio


class MUDServer:
    dungeon = [[0 for i in range(10)] for j in range(10)]
    # self.dungeon[y][x] = hp, name, message
    pos = [0, 0]
    # pos = [x, y]

    async def echo(self, reader, writer):
        print("Player connected")
        while data := await reader.readline():
            data = data.decode()[:-1]
            print('<< ', data)
            if data.startswith("move "):
                data = data.split()
                x, y = map(int, [data[1], data[2]])
                self.pos = x, y
                if self.dungeon[y][x]:
                    hp, name, message = self.dungeon[y][x]
                    data = f'{name} {message}'
                else:
                    data = 'nobody'
                print('>> ', data)
                writer.write(bytes(data.encode()))
            elif data == "pos":
                data = f"{self.pos[0]} {self.pos[1]}"
                print('>> ', data)
                writer.write(bytes(data.encode()))
            elif data.startswith("attack "):
                data = data.split()
                name, damage = data[1], int(data[2])
                if not self.dungeon[self.pos[1]][self.pos[0]]:
                    data = 'nobody'
                else:
                    hp, m_name, msg = self.dungeon[self.pos[1]][self.pos[0]]
                    hp, damage = int(hp), int(damage)
                    if name == m_name:
                        new_hp = max(hp - damage, 0)
                        data = f"{min(damage, hp)} {new_hp}"
                        pos = self.pos
                        if new_hp:
                            self.dungeon[pos[1]][pos[0]] = new_hp, m_name, msg
                        else:
                            self.dungeon[pos[1]][pos[0]] = 0
                    else:
                        data = 'nobody'
                print('>> ', data)
                writer.write(bytes(data.encode()))
            elif data.startswith("add "):
                add, name, hp, y, x, *message = data.split()
                replaced = 0
                y, x, hp = map(int, [y, x, hp])
                if self.dungeon[y][x]:
                    replaced = 1
                self.dungeon[y][x] = hp, name, " ".join(message)
                data = f"{replaced}"
                print('>> ', data)
                writer.write(bytes(data.encode()))
            else:
                print('>WARNING< Wrong command ignored', data)
        print("Player disconnected")
        writer.close()
        await writer.wait_closed()

    async def main(self):
        server = await asyncio.start_server(self.echo, '0.0.0.0', 1337)
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(MUDServer().main())
