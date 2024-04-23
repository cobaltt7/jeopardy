import setMessageHandler, {send} from "./websocket.js"

const button = Object.assign(document.createElement("button"), {
    class: "buzz",
    type: "button",
    disabled: true,
})
document.querySelector(".players")?.append(button)

button.addEventListener("click", () => {
    send({action: "buzz"})
})

await new Promise((resolve) =>
    setMessageHandler((message) => message.action === "ready" && resolve(undefined)),
)
setMessageHandler((message) => {
    if (message.action === "buzz") button.disabled = true
})

button.disabled = false
document.body.classList.remove("last-question")
document.querySelector("#question p")?.classList.remove("hidden")
