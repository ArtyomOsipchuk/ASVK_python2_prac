#!/usr/bin/env python3
import asyncio
import cowsay
from io import StringIO

admin = cowsay.read_dot_cow(StringIO(''' ,___,
 |(A)|
(._ _.)
 (oo)\\_______
 (__)\\ Admin  )\\/\\
      ||----w |
      ||     ||
'''))

clients = {}
available_cows = set(cowsay.list_cows())

def twocows(cow1, cow2):
    cow1 = cow1.split('\n')
    cow2 = cow2.split('\n')
    wid = max(len(i) for i in cow1 + cow2)
    sh = len(cow1) - len(cow2)
    if sh > 0:
        for i in range(sh):
            cow2.insert(0, ' ' * wid)
    elif sh < 0:
        for i in range(-sh):
            cow1.insert(0, ' ' * wid)
    cow = []
    for i in range(len(cow1)):
        cow.append(cow1[i].ljust(wid) + cow2[i])
    return '\n'.join(cow)

async def chat(reader, writer):
    me = None 
    queue = asyncio.Queue()
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(queue.get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                message = q.result().decode().strip()
                print([message])
                if not message:
                    continue
                if message.startswith('login '):
                    if me:
                        writer.write(bytes((cowsay.cowsay(f"Мой друг, вы уже зарегистрированы как {me}", cowfile=admin) + '\n').encode()))
                        continue
                    message = message.split()
                    if len(message) != 2:
                        writer.write(bytes((cowsay.cowsay(f"Usage: login <cow_name>", cowfile=admin) + '\n').encode()))
                        continue
                    _, cow_name = message
                    if cow_name in available_cows:
                        me = cow_name
                        clients[me] = queue
                        available_cows.remove(cow_name)
                        writer.write(bytes((twocows(cowsay.cowsay(f"Мой друг, вы успешно зарегистрировались под именем {cow_name}. Ваш аватар справа ->", cowfile=admin),
                                              cowsay.cowsay(f"Это я", cow=me)) + '\n').encode()))
                        await writer.drain()
                        for out in clients.values():
                            await out.put((twocows(cowsay.cowsay(f"{me} присоединился(ась) к чату! ->", cowfile=admin),
                                          cowsay.cowsay(f"Всем привет!", cow=me)) + '\n'))
                    else:
                        writer.write(bytes((cowsay.cowsay(f"Имя {cow_name} уже занято, невежливо выдавать себя за другую корову", cowfile=admin) + '\n').encode()))
                        await writer.drain()
                elif message == 'who':
                    writer.write(bytes((cowsay.cowsay(f"Вежливые коровы в чате: {', '.join(clients.keys())}", cowfile=admin) + '\n').encode()))
                    await writer.drain()
                elif message == 'cows':
                    writer.write(bytes((cowsay.cowsay(f"Свободные имена коров: {', '.join(available_cows)}", cowfile=admin) + '\n').encode()))
                    await writer.drain()
                elif message.startswith('say '):
                    if not me:
                        writer.write(bytes((cowsay.cowsay("Вежливые коровы начинают диалог с команды login <имя_коровы>", cowfile=admin) + '\n').encode()))
                        await writer.drain()
                        continue
                    message = message.split()
                    if len(message) < 3:
                        writer.write(bytes((cowsay.cowsay(f"Usage: say <receiver_cow_name> <message>", cowfile=admin) + '\n').encode()))
                        continue
                    _, rcv, *msg = message
                    if rcv == me:
                        writer.write(bytes((cowsay.cowsay(f"Не стоит разговаривать с самим собой", cowfile=admin) + '\n').encode()))
                        continue
                    if rcv in clients:
                        await clients[rcv].put(twocows(cowsay.cowsay(f"Приватное сообщение для меня", cow=rcv),
                                              cowsay.cowsay(' '.join(msg), cow=me) + '\n'))
                    else:
                        writer.write(bytes((cowsay.cowsay(f"Пользователь {rcv} не найден", cowfile=admin) + '\n').encode()))
                        await writer.drain()
                elif message.startswith('yield '):
                    if not me:
                        writer.write(bytes((cowsay.cowsay("Вежливые коровы начинают диалог с команды login <имя_коровы>", cowfile=admin) + '\n').encode()))
                        await writer.drain()
                        continue
                    message = message.split()
                    if len(message) < 2:
                        writer.write(bytes((cowsay.cowsay(f"Usage: yield <message>", cowfile=admin) + '\n').encode()))
                        continue
                    _, *msg = message
                    for out in clients.values():
                        await out.put((cowsay.cowsay(' '.join(msg), cow=me) + '\n'))
                elif message == "quit":
                    for out in clients.values():
                        await out.put((twocows(cowsay.cowsay(f"{me} покинул(а) чат...", cowfile=admin),
                                               cowsay.cowsay(f"Всем пока!", cow=me)) + '\n'))
                    del clients[me]
                    available_cows.add(me)
                    me = None
                elif message == 'help':
                    help_msg = '''Команды:
                    who — просмотр зарегистрированных пользователей
                    cows — просмотр свободных имён коров
                    login название_коровы — зарегистрироваться под именем название_коровы
                    say название_коровы текст сообщения — послать сообщение пользователю название_коровы
                    yield текст сообщения — послать сообщение всем зарегистрированным пользователям
                    quit — отключиться'''
                    writer.write(bytes((cowsay.cowsay(help_msg, cowfile=admin) + '\n').encode()))
                    await writer.drain()
                else:
                    writer.write(bytes((cowsay.cowsay("Неизвестная команда. Введите 'help' для списка команд.", cowfile=admin) + '\n').encode()))
                    await writer.drain()
            elif q is receive:
                receive = asyncio.create_task(queue.get())
                writer.write(bytes(f"{q.result()}\n".encode()))
                await writer.drain()
    send.cancel()
    receive.cancel()
    if me is not None:
        del clients[me]
        available_cows.add(me)
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
