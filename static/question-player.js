import setMessageHandler from "./websocket.js"

await new Promise((resolve) =>
    setMessageHandler((message) => message.action === "ready" && resolve(undefined)),
)

document.body.classList.remove("last-question")
document.querySelector("#question p")?.classList.remove("hidden")
