import {roundIndex} from "./util.js"
import setMessageHandler from "./websocket.js"

const players = /** @type {NodeListOf<HTMLDivElement>} */ (
    document.querySelectorAll(".player")
)
const cells = [
    .../** @type {NodeListOf<HTMLAnchorElement>} */ (
        document.querySelectorAll(".cell")
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
