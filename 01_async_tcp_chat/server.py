"""
Project: Asynchronous Multi-Client TCP Chat
Author: Pra P.
Description:
    Asynchronous TCP chat server using Python's asyncio.
    Supports multiple concurrent clients and chat rooms.
    Handles client disconnects and message broadcasting gracefully.

Usage:
    Run `python server.py`
"""

import asyncio

rooms = {}  # {room_name: set of (writer, username)}
clients = {}  # {writer: username}

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    writer.write(b"Enter your username: ")
    await writer.drain()
    username = (await reader.readline()).decode().strip()
    clients[writer] = username
    writer.write(f"Welcome {username}! Use /join <room> to enter a chat room.\n".encode())
    await writer.drain()
    print(f"[+] {username} connected from {addr}")

    joined_room = None

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            msg = data.decode().strip()

            if msg.startswith("/join "):
                room_name = msg.split(" ", 1)[1]
                if joined_room:
                    rooms[joined_room].discard((writer, username))
                rooms.setdefault(room_name, set()).add((writer, username))
                joined_room = room_name
                writer.write(f"Joined room '{room_name}'.\n".encode())

            elif msg.startswith("/leave"):
                if joined_room and writer in [w for w, _ in rooms[joined_room]]:
                    rooms[joined_room].discard((writer, username))
                    writer.write(f"Left room '{joined_room}'.\n".encode())
                    joined_room = None
                else:
                    writer.write(b"You are not in any room.\n")

            elif msg.startswith("/msg "):
                if not joined_room:
                    writer.write(b"Join a room first with /join <room>\n")
                    continue
                message = msg.split(" ", 1)[1]
                await broadcast(joined_room, f"[{username}] {message}\n", exclude=writer)

            elif msg.startswith("/rooms"):
                all_rooms = ", ".join(rooms.keys()) or "No active rooms"
                writer.write(f"Active rooms: {all_rooms}\n".encode())

            elif msg.startswith("/quit"):
                writer.write(b"Goodbye!\n")
                await writer.drain()
                break

            else:
                writer.write(b"Commands: /join, /leave, /msg, /rooms, /quit\n")

            await writer.drain()

    except asyncio.CancelledError:
        pass
    finally:
        print(f"[-] {username} disconnected.")
        if joined_room and joined_room in rooms:
            rooms[joined_room].discard((writer, username))
        clients.pop(writer, None)
        writer.close()
        await writer.wait_closed()


async def broadcast(room_name, message, exclude=None):
    """Send message to all clients in a room except optionally one."""
    for w, _ in list(rooms.get(room_name, [])):
        if w is exclude:
            continue
        try:
            w.write(message.encode())
            await w.drain()
        except ConnectionError:
            rooms[room_name].discard((w, clients.get(w, "unknown")))


async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)
    addr = server.sockets[0].getsockname()
    print(f"💬 Chat Server running on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
