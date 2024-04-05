import {fadeOut, parseCategory, roundIndex, speak} from "./util.js"
import {send} from "./websocket.js"

if (roundIndex === 0) {
    const players = /** @type {NodeListOf<HTMLDivElement>} */ (
        document.querySelectorAll(".player")
    )
    const cells = [
        .../** @type {NodeListOf<HTMLAnchorElement>} */ (
            document.querySelectorAll("a.cell")
        ),
    ]
    for (const player of players) player.classList.add("hidden")
    for (const cell of cells) cell.classList.add("transparent")

    const song = new Audio("/static/theme.mp3")
    song.volume = 0.4
    await song.play().catch(console.error)
    await new Promise((resolve) => setTimeout(resolve, 9_000))
    await speak("This is Jeopardy!")

    await speak("Here are today's contestants:")
    for (const player of players) {
        player.classList.remove("hidden")
        await speak(
            (!player.nextElementSibling && player.previousElementSibling ?
                "and "
            :   "") + (player.querySelector(".name")?.textContent?.trim() ?? ""),
        )
    }
    await speak("Good luck!")

    await fadeOut(song)

    await new Audio("/static/fill.mp3").play().catch(console.error)
    while (cells.length) {
        await new Promise((resolve) => setTimeout(resolve, 350))
        const toShow = cells.sort(() => Math.random() - 0.5).splice(0, 5)
        for (const cell of toShow) cell.classList.remove("transparent")
    }
    await speak("Today's categories are:")
} else {
    const song = new Audio("/static/dj.mp3")
    song.volume = 0.4
    await song.play().catch(console.error)
    await new Promise((resolve) => setTimeout(resolve, 500))
    await speak("It's time for Double Jeopardy!")
    await new Promise((resolve) => setTimeout(resolve, 500))
    await Promise.all([fadeOut(song), speak("The categories are:")])
}

for (const category of document.querySelector(".row")?.children ?? []) {
    category.classList.remove("covered")
    await speak(
        (!category.nextElementSibling && category.previousElementSibling ?
            "and "
        :   "") + parseCategory(category.textContent?.trim() ?? ""),
    )
}

send({action: "ready"})
