# Jeopardy!

## Websocket docs

All messages are sent as JSON-encoded objects. All messages require an `action` property to indicate what action is being taken.

### Server-to-Client Events

#### `error`

-   Emitted in response to any failed action.
-   Only emitted to the client who sent the originating action.
-   Invalid actions do not trigger error responses.

| Property        | Type  | Description                     |
| --------------- | ----- | ------------------------------- |
| `failed_action` | `str` | Action that triggered the error |
| `error`         | `str` | Error code                      |

#### `join`

-   Emitted when a player joins a room.
-   Emitted to all players in it, as well as the host.
-   Not emitted to the player who joined.

| Property | Type  | Description           |
| -------- | ----- | --------------------- |
| `player` | `str` | The new player's name |

#### `close`

-   Emitted when the host closes a room
-   Emitted to all players in it, as well as the host.
-   No extra properties.

#### `disconnect`

-   Emitted when a given player or host sends a second `join` event from a different WebSocket.
-   Emitted to the player or host's original WebSocket only to indicate that that WebSocket will no longer recieve any future events.
-   No extra properties.

### Client-to-Server Events

#### `join`

Subscribe to a room

| Property | Type  | Description                |
| -------- | ----- | -------------------------- |
| `room`   | `str` | Room ID to join            |
| `player` | `str` | Supplied player or host ID |

| Error Code       | Description                   |
| ---------------- | ----------------------------- |
| `no_room`        | No room provided              |
| `invalid_room`   | Room does not exist           |
| `no_player`      | No player ID provided         |
| `invalid_player` | No player with that ID exists |
