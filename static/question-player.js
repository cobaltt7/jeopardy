import {timer} from "./util.js"
import setMessageHandler, {send} from "./websocket.js"

const players = document.querySelector(".players")

const buzzer = Object.assign(document.createElement("button"), {
    class: "buzz",
    type: "button",
    disabled: true,
})
players?.append(buzzer)
buzzer.addEventListener("click", () => {
    send({action: "buzz"})
})

setMessageHandler(async (message) => {
    switch (message.action) {
        case "ready": {
            document.body.classList.remove("last-question")
            document.querySelector("#question p")?.classList.remove("hidden")
            break
        }
        case "allow-buzzing": {
            buzzer.disabled = false
        }
        case "buzz": {
            buzzer.disabled = true
            const player =
                typeof message.player === "string" &&
                /** @type {HTMLDivElement | null} */ (
                    document.querySelector(
                        `div[data-player='${message.player.replaceAll("'", "\\'").replaceAll("\\", "\\\\")}']`,
                    )
                )
            if (player) await timer(player)
            break
        }
    }
})
