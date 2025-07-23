if (!speechSynthesis.getVoices().length)
    await new Promise((resolve) =>
        speechSynthesis.addEventListener("voiceschanged", resolve),
    )

console.debug("Voices loaded")

const selectedVoice = localStorage.getItem("voice")
export const voice = speechSynthesis
    .getVoices()
    .find((voice) => voice.voiceURI === selectedVoice)

/** @param {string} category */
export function parseCategory(category) {
    return `"${category
        .replaceAll(/( ?_ ?){2,}/g, "-blank-")
        .replaceAll(/"([^"]{,2})" /g, "$1' ")
        .replaceAll(/["()]/g, "")
        .replaceAll(".", " ")
        .replaceAll(/\s{2,}/g, " ")
        .toLowerCase()
        .trim()}"`
}

/** @param {string} text */
export function speak(text) {
    console.debug("Speaking:", text)
    if (!voice) return
    speechSynthesis.cancel()

    const tts = new SpeechSynthesisUtterance(text)
    tts.voice = voice
    tts.lang = "en-US"
    return new Promise((resolve) => {
        tts.addEventListener("end", () => {
            resolve(void 0)
        })
        tts.addEventListener("error", (error) => {
            console.error(error)
            resolve(void 0)
        })
        speechSynthesis.speak(tts)
    })
}

export const ROUNDS = ["Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"]
export const roundIndex =
    ROUNDS.indexOf(document.querySelector("h1")?.textContent?.trim() ?? ROUNDS[0] ?? "")
    ?? 0

/** @param {HTMLAudioElement} song */
export async function fadeOut(song) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    const fadeInterval = setInterval(function () {
        const newVolume = song.volume - 0.01
        if (newVolume <= 0) {
            song.pause()
            return clearInterval(fadeInterval)
        }
        song.volume = newVolume
    }, 10)
    await new Promise((resolve) => setTimeout(resolve, 1_000))
}

/** @param {HTMLDivElement} player */
export function timer(player, time = 15_000) {
    const timer = /** @type {HTMLDivElement | null} */ (player.querySelector("div.timer"))
    if (!timer) return
    let progress = 9
    timer.style.width = "100%"
    const {promise, resolve} = Promise.withResolvers()
    const interval = setInterval(() => {
        progress -= 2
        timer.style.width = `${Math.max(0, progress) / 0.09}%`
        if (progress <= 0) {
            clearInterval(interval)
            resolve(undefined)
        }
    }, time / 10)
    return promise
}
