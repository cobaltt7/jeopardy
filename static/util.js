if (!speechSynthesis.getVoices().length)
    await new Promise((resolve) =>
        speechSynthesis.addEventListener("voiceschanged", resolve),
    )

console.debug("Voices loaded")

const voiceElement = document.querySelector("[name=voice]")
const selectedVoice = voiceElement instanceof HTMLMetaElement && voiceElement.content
export const voice =
    voiceElement ?
        speechSynthesis.getVoices().find((voice) => voice.voiceURI === selectedVoice)
    :   undefined

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
    ROUNDS.indexOf(
        document.querySelector("h1")?.textContent?.trim() ?? ROUNDS[0] ?? "",
    ) ?? 0

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
