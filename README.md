# Jeopardy!

## Websocket docs

All messages are sent as JSON-encoded objects. All messages require an `action` property to indicate what action is being taken.

Errors are sent to the client with this format:

| Property | Type  | Description                     |
| -------- | ----- | ------------------------------- |
| `action` | `str` | Action that triggered the error |
| `error`  | `str` | Error code                      |

Invalid actions do not trigger error responses.

### `join`

Join a room

| Property | Type  | Description     |
| -------- | ----- | --------------- |
| `room`   | `str` | Room ID to join |
| `player` | `str` | Player name     |

| Error Code         | Description                               |
| ------------------ | ----------------------------------------- |
| `no_room`          | No room provided                          |
| `invalid_room`     | Room does not exist                       |
| `no_player`        | No player provided                        |
| `invalid_player`   | Player name is empty                      |
| `duplicate_player` | Player with that name already joined room |
