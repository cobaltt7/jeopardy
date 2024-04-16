# Jeopardy!

## WebSocket docs

All messages are sent as JSON-encoded objects. All messages require an `action` property to indicate
what action is being taken.

### Server-to-Client Events

#### `ack`

-   Emitted in response to any successful action for debugging purposes only.
-   Should not be used in any production logic and should be considered unstable.
-   Only emitted to the client who sent the originating action.

| Property      | Type  | Description          |
| ------------- | ----- | -------------------- |
| `sent_action` | `str` | Original sent action |

#### `close`

-   Emitted when the host closes a room.
-   Emitted to all players in it, as well as the host.
-   No extra properties.

#### `disconnect`

-   Emitted when a given player or host sends a second [`join`](#join-1) event from a different
    WebSocket.
-   Emitted only to the player or host's original WebSocket.
-   Any WebSocket receiving this event will no longer recieve any future events.
-   No extra properties.

#### `error`

-   Emitted in response to any failed action.
-   Only emitted to the client who sent the originating action.

| Property        | Type                                                      | Description                     |
| --------------- | --------------------------------------------------------- | ------------------------------- |
| `failed_action` | `str`                                                     | Action that triggered the error |
| `error`         | `str` - See [below](#client-to-server-events) for details | Error code                      |

#### `join`

-   Emitted when a player joins a room.
-   Emitted to all players in it, as well as the host.
-   Not emitted to the player who joined.

| Property | Type  | Description           |
| -------- | ----- | --------------------- |
| `player` | `str` | The new player's name |

#### `ready`

-   Emitted when the host sends [`ready`](#ready-1).
-   No additional properties.

#### `reload`

-   Emitted when the room status changes.
-   Emitted to all players in it, as well as the host.
-   Reload the page and reconnect to get updated data.

| Property | Type                                     | Description          |
| -------- | ---------------------------------------- | -------------------- |
| `reason` | `Literal["start", "question", "answer"]` | The reason to reload |

### Client-to-Server Events

These properties are required with every payload. Some actions require additional properties.

| Property | Type  | Description       |
| -------- | ----- | ----------------- |
| `room`   | `str` | Room ID           |
| `auth`   | `str` | Supplied host key |

All events may fail with one of these error codes. Some actions may fail in more situations.

| Error Code       | Description                    |
| ---------------- | ------------------------------ |
| `no_room`        | No room provided               |
| `invalid_room`   | Room does not exist            |
| `no_auth`        | No authentication key provided |
| `no_action`      | No action provided             |
| `invalid_action` | Unkown action provided         |

#### `join`

-   Sent on page load.
-   Subscribes the client to all future events for a room.
-   No additional properties.

| Error Code     | Description                            |
| -------------- | -------------------------------------- |
| `invalid_auth` | Provided key does not match any player |

#### `ready`

-   Sent by the host when data is ready to be fully displayed.
-   Emits [`ready`](#ready) to the room.
-   No additional properties.

| Error Code     | Description                               |
| -------------- | ----------------------------------------- |
| `invalid_auth` | Provided key does not match the room host |
