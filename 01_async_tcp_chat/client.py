"""
Client for Asynchronous Multi-Client TCP Chat
Usage:
    Run `python client.py`
Then type commands like:
    /join general
    /msg general Hello everyone!
    /rooms
    /quit
"""

import asyncio
import sys

async def listen(reader):
    while True:
        data = await reader.readline()
        if not data:
            print("Server closed the connection.")
            break
        print(data.decode().rstrip())

async def send(writer):
    loop = asyncio.get_event_loop()
    while True:
        msg = await loop.run_in_executor(None, sys.stdin.readline)
        if not msg:
            break
        writer.write(msg.encode())
        await writer.drain()
        if msg.strip() == "/quit":
            break
    writer.close()

async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
    print("Connected to server at 127.0.0.1:8888")
    asyncio.create_task(listen(reader))
    await send(writer)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient closed.")
