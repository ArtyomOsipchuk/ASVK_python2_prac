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
