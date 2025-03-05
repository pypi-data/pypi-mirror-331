# RCON-Host

The **RCON-Host** library allows you to accept user commands using the RCON protocol.

## Description

The **RCON-Host** library emulates the operation of the RCON server (Remote Console), providing the ability to receive
commands from clients, process them using a custom handler, and send responses. The program also supports password
authentication.

The library can be useful for testing applications running with RCON, or emulating a remote server.

## Technical requirements

- **Python** versions **3.x**.

## Installation

1. Make sure that you have Python version 3.x installed.
2. Install the library using `pip`:

   ```bash
   pip3 install rcon-host
   ```

## Usage

### 1. Importing the library

```python
from rcon_host import RCON
```

### 2. Creating a custom handler

User Handler:

- Accepts the only argument, the user's command.
- Returns a string with the answer either `None`.

Implementation example:

```python
def handler(payload):
    print(f"Command received: {payload}")
    return f"Response: {payload}"
```

### 3. Initializing the server

When creating a server instance, you can set the following parameters:

- **`host`** is the IP address where the server will be running (default: `"0.0.0.0"` — all interfaces).
- **`port`** is the port for incoming connections (by default: `19132`).
- **` password`** is the password for authentication (default: `None`, authentication is disabled).

Example:

```python
rcon = RCON(host="0.0.0.0", port=19132, password="12345678")
```

### 4. Assigning a custom handler

```python
rcon.set_handler(handler)
```

### 5. Starting the server

When `start()` is called, the server starts in a separate thread by default (`threading=True`).

```python
rcon.start(True)
```