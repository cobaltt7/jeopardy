import {roundIndex} from "./util.js"

const STATES = ["", "loss", "gain"]

const checkboxes = roundIndex < 2 ? document.querySelectorAll(".answer-button") : []
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
