import {parseCategory, roundIndex, ROUNDS, speak, timer} from "./util.js"
import setMessageHandler, {send} from "./websocket.js"

const STATES = ["", "loss", "gain"]

const table = /** @type {HTMLDivElement} */ (document.querySelector("div#question"))
const category = parseCategory(
    document.querySelector("#category")?.textContent?.trim() ?? "",
)
const question = table.querySelector("p")
const answer = document.querySelector("#answer")
const isLast = document.body.classList.contains("last-question")
const playerForm = /** @type {HTMLFormElement} */ (
    document.querySelector("form.players")
)

const [action, ...players] = /** @type {[HTMLInputElement, ...HTMLDivElement[]]} */ (
    Array.from(playerForm.children).reverse()
)

if (roundIndex < 2) {
    const checkboxes = document.querySelectorAll(".answer-button")
    for (const checkbox of checkboxes) {
        checkbox.addEventListener("click", () => {
            const input = checkbox.previousElementSibling
            if (!(input instanceof HTMLInputElement)) return

            const oldValue = +input.value || 0
            const newValue = (oldValue + 1) % STATES.length
            const newState = STATES.at(newValue) ?? ""

            for (const otherCheckbox of newState === "gain" ? checkboxes : []) {
                if (otherCheckbox.getAttribute("data-state") !== "gain") continue

                const otherInput = otherCheckbox.previousElementSibling
                if (!(otherInput instanceof HTMLInputElement)) return

                otherInput.value = "0"
                otherCheckbox.setAttribute("data-state", "")
            }

            input.value = `${newValue}`
            checkbox.setAttribute("data-state", newState)
        })
    }

    if (isLast) await speak(`The final clue of this round.`)
    await speak(
        `${category} for ${document.querySelector("#value")?.textContent?.trim()}`,
    )
    if (document.body.getAttribute("data-daily-double") === "True") {
        const song = new Audio("/static/dd.mp3")
        song.volume = 0.4
        await song.play().catch(console.error)

        table.classList.add("daily-double")
        await speak(`It's a daily double!`)
        action.value = "handle-wagers"

        const time = 15
        await speak(`You have ${time} seconds to put down a wager.`)
        await new Promise((resolve) => setTimeout(resolve))
        // TODO: show the timer on the current player

        await speak("Here is your clue.")
        table.classList.remove("daily-double")
    } else if (isLast) {
        await new Promise((resolve) => setTimeout(resolve, 2000))
    }

    await revealQuestion()
} else {
    document.body.classList.add("final-jeopardy")
    await speak(`It's time for ${ROUNDS[roundIndex]}!`)

    const time = 15
    await speak(
        `The category is ${category}. You have ${time} seconds to put down a wager.`,
    )
    await Promise.all(players.map((player) => timer(player, time * 1000)))

    await speak("Here is your clue.")
    await revealQuestion()

    await speak("You have 30 seconds. Good luck.")
    await new Audio("/static/fj.mp3").play().catch(console.error)
    await Promise.all(players.map((player) => timer(player, 30_000)))

    await revealAnswer()
    for (const player of players.slice(1)) player.style.display = "none"
    let player = players[0]

    action.value = "handle-wagers"
    button.type = "button"
    button.textContent = "Next"
    button.addEventListener("click", () => {
        const wager = player?.querySelector(".wager input")
        if (wager instanceof HTMLInputElement && !wager.value) {
            wager.reportValidity()
            if (!wager.validity.valid) return
        }
        if (!(player?.previousElementSibling instanceof HTMLDivElement))
            return playerForm.submit()

        player.style.display = "none"
        player = player.previousElementSibling
        player.style.display = "block"
    })
}

let startTime = Date.now()
let timeLeft = 15000
/** @type {number | undefined} */
let buzzTimer
async function revealQuestion() {
    document.body.classList.remove("last-question")
    question?.classList.remove("hidden")
    send({action: "ready"})

    await speak(question?.textContent?.trim() ?? "")

    startTime = Date.now()
    setMessageHandler(async (message) => {
        switch (message.action) {
            case "buzz": {
                if (typeof message.player !== "string") break
                const player =
                    typeof message.player === "string"
                    && /** @type {HTMLDivElement | null} */ (
                        document.querySelector(
                            `div[data-player='${message.player.replaceAll("'", "\\'").replaceAll("\\", "\\\\")}']`,
                        )
                    )

                clearTimeout(buzzTimer)
                timeLeft = -(Date.now() - startTime)
                startTime = Date.now()
                if (player) {
                    const answerTimer = timer(player)
                }

                allowBuzzing()
                break
            }
        }
    })
    allowBuzzing()
}

async function allowBuzzing() {
    send({action: "allow-buzzing"})
    startTime = Date.now()
    buzzTimer = setTimeout(async () => {
        send({action: "buzz"})
        answer?.classList.remove("hidden")
        await speak(answer?.textContent?.trim() ?? "")
        playerForm.submit()
    }, timeLeft)
}
async function revealAnswer() {
    document.body.classList.remove("final-jeopardy")
    send({action: "buzz"})
    answer?.classList.remove("hidden")
    await speak(answer?.textContent?.trim() ?? "")
}
