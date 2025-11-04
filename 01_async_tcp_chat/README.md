## `01_async_tcp_chat/README.md`

# Asynchronous Multi-Client TCP Chat

## Overview
This project implements a multi-client TCP chat server using Python's `asyncio` module.  
It allows multiple clients to connect concurrently, join chat rooms, and exchange messages in real time.  
All operations are handled asynchronously for efficiency and scalability.

---

## Features
- Supports multiple concurrent clients  
- Named chat rooms (`/join <room>`)  
- Room-specific broadcast messaging  
- Clean handling of client disconnects  
- Simple text-based command protocol  
- Fully asynchronous design (non-blocking I/O)

---

## Concepts Demonstrated
- Asynchronous I/O with `asyncio`  
- TCP socket communication using `StreamReader` and `StreamWriter`  
- Connection and resource management  
- Broadcasting and message routing  
- Graceful shutdown and error handling

---

## How to Run

### 1. Start the Server
Open a terminal and run:
```bash
python server.py
````

Expected output:

```
Chat Server running on ('127.0.0.1', 8888)
```

### 2. Start One or More Clients

Open another terminal (or more) and run:

```bash
python client.py
```

You’ll be prompted for a username:

```
Enter your username: alice
```

Then join or create a room:

```
/join general
```

Now you can chat:

```
/msg general Hello everyone!
```

---

## Available Commands

| Command              | Description                |
| -------------------- | -------------------------- |
| `/join <room>`       | Join or create a chat room |
| `/leave`             | Leave the current room     |
| `/msg <room> <text>` | Send a message to a room   |
| `/rooms`             | Show all active chat rooms |
| `/quit`              | Disconnect from the server |

---

## Example Session

**Terminal 1 (Server):**

```
python server.py
Chat Server running on ('127.0.0.1', 8888)
[+] alice connected from ('127.0.0.1', 56734)
[+] bob connected from ('127.0.0.1', 56736)
```

**Terminal 2 (Client 1 — alice):**

```
/join general
/msg general Hi Bob!
```

**Terminal 3 (Client 2 — bob):**

```
/join general
[alice] Hi Bob!
/msg general Hey Alice!
```

---

## File Structure

```
01_async_tcp_chat/
│
├── server.py     # Asynchronous TCP server
├── client.py     # Chat client
└── README.md     # Project documentation
```


## Future Improvements

* Add persistent chat history
* Implement private messaging (`/pm <user> <text>`)
* Add authentication and user lists
* Create a simple WebSocket or GUI frontend
* Add TLS encryption for secure connections

---
