# PY-MESHAXON

The Py-Meshaxon is a mini project socket chat system.This code make by Python and socket network programing concept.

![alt text](/meshaxon.png)

## Features

- Create user and publish to lobbies
- Send message to other user in mesh server


## Tech

- [Python] - Required version 3+
- [Socket] - Create statefull connection with TCP Protocol
- [Theading] - Handle connection in multitread
- [Mutex] - Resource locking
- [Redis] - Publish / Subscribe server to server event


## Installation

Py-meshaxon requires [Python](https://www.python.org/downloads/) v3.8+ to run.

If you not redis can install [Redis](https://redis.io/docs/getting-started/installation/)

## Development

First : Run server

```sh
python3 src/server.py
```

Second : Run client

```sh
python3 src/client.py
```

## Author

@Pinyoo Thotaboot