import {roundIndex} from "./util.js"
import setMessageHandler from "./websocket.js"

const players = /** @type {NodeListOf<HTMLDivElement>} */ (
    document.querySelectorAll("div.player")
)
const cells = [
    .../** @type {NodeListOf<HTMLElement>} */ (
        document.querySelectorAll(".cell:not(h2)")
    ),
]
if (roundIndex === 0) {
    for (const player of players) player.classList.add("hidden")
    for (const cell of cells) cell.classList.add("transparent")
}

await new Promise((resolve) =>
    setMessageHandler((message) => message.action === "ready" && resolve(undefined)),
)

for (const player of players) player.classList.remove("hidden")
for (const cell of cells) cell.classList.remove("transparent")

for (const category of document.querySelector(".row")?.children ?? [])
    category.classList.remove("covered")
