import io from "https://cdn.socket.io/4.7.5/socket.io.esm.min.js"

const authElement = document.querySelector("[name=auth_key]")
export const authKey = authElement instanceof HTMLMetaElement && authElement.content
const roomElement = document.querySelector("[name=room]")
export const roomId = roomElement instanceof HTMLMetaElement && roomElement.content

export const socket = io()
socket.on(
    "message",
    /** @param {unknown} message */ (message) => {
        console.log(message)
        if (!message || typeof message !== "object") return
        if (!("action" in message) || typeof message.action !== "string") return
        switch (message.action) {
            case "close": {
                if (!authKey || authKey.startsWith("host-"))
                    alert("The host has closed the room.")
                location.href = location.origin
                break
            }
            case "disconnect": {
                alert(
                    "Looks like you've opened another tab! You can only join a room once. Please refresh this page to continue playing here.",
                )
                location.href = location.origin
                break
            }
            case "error": {
                if (
                    !("failed_action" in message) ||
                    typeof message.failed_action !== "string"
                )
                    break
                if (!("error" in message) || typeof message.error !== "string") break
                throw new WebSocketError({
                    action: message.failed_action,
                    error: message.error,
                })
            }
            case "reload": {
                location.href = location.origin
                break
            }
            default: {
                handler?.({...message, action: message.action})
            }
        }
    },
)

/** @param {Record<string, unknown>} data */
export function send(data) {
    if (roomId && authKey) {
        socket.send({room: roomId, auth: authKey, ...data})
        return true
    }
    return false
}

send({action: "join"})

/**
 * @typedef {(message: {action: string} & Record<string, unknown>) => void} Handler
 * @type {Handler | undefined}
 */
let handler
/** @param {Handler} newHandler */
export default function setMessageHandler(newHandler) {
    handler = newHandler
}

class WebSocketError extends Error {
    /** @param {{error: string; action: string}} obj */
    constructor({error, action}) {
        super(`${error} in action ${action}`)
        this.name = "WebSocketError"
        this.error = error
        this.action = action
    }
}
