import {parseCategory, roundIndex, ROUNDS, speak} from "./util.js"
import {send} from "./websocket.js"
const STATES = ["", "loss", "gain"]

const table = /** @type {HTMLDivElement} */ (document.querySelector("#question"))
const category = parseCategory(
    document.querySelector("#category")?.textContent?.trim() ?? "",
)
const question = table.querySelector("p")
const answer = document.querySelector("#answer")
const isLast = document.body.classList.contains("last-question")
const playerForm = /** @type {HTMLFormElement} */ (document.querySelector(".players"))

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

        const action = /** @type {HTMLInputElement} */ (
            Array.from(playerForm.children).at(-1)
        )
        action.value = "handle-wagers"

        const time = 15
        await speak(`You have ${time} seconds to put down a wager.`)
        await new Promise((resolve) => setTimeout(resolve, time * 1000))
        // TODO: show the timer on each player

        await speak("Here is your clue.")
        table.classList.remove("daily-double")
    } else if (isLast) {
        await new Promise((resolve) => setTimeout(resolve, 2000))
    }

    await revealQuestion()

    setTimeout(revealAnswer, 10_000)
} else {
    document.body.classList.add("final-jeopardy")
    await speak(`It's time for ${ROUNDS[roundIndex]}!`)

    const time = 15
    await speak(
        `The category is ${category}. You have ${time} seconds to put down a wager.`,
    )
    await new Promise((resolve) => setTimeout(resolve, time * 1000))
    // TODO: show the timer on each player

    await speak("Here is your clue.")
    await revealQuestion()

    await speak("You have 30 seconds. Good luck.")
    await new Audio("/static/fj.mp3").play().catch(console.error)
    await new Promise((resolve) => setTimeout(resolve, 30_000))

    await revealAnswer()

    const [action, button, ...players] =
        /** @type {[HTMLInputElement, HTMLButtonElement, ...HTMLDivElement[]]} */ (
            Array.from(playerForm.children).reverse()
        )
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

async function revealQuestion() {
    document.body.classList.remove("last-question")
    question?.classList.remove("hidden")
    send({action: "ready"})
    await speak(question?.textContent?.trim() ?? "")
}
async function revealAnswer() {
    answer?.classList.remove("hidden")
    await speak(answer?.textContent?.trim() ?? "")
    document.body.classList.remove("final-jeopardy")
}
