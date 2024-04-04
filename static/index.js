const voiceSelect = document.querySelector("select")
voiceSelect?.addEventListener("change", () => {
    localStorage.setItem("voice", voiceSelect.value)
})
speechSynthesis.addEventListener("voiceschanged", updateVoices)
updateVoices()
function updateVoices() {
    if (!voiceSelect) throw new ReferenceError("Could not find voice select element")

    const selected =
        localStorage.getItem("voice") ?? voiceSelect.selectedOptions[0]?.value

    voiceSelect.replaceChildren(
        ...speechSynthesis
            .getVoices()
            .filter((voice) => ["en", "en-US"].includes(voice.lang))
            .sort(
                (one, two) =>
                    +two.default - +one.default || one.name.localeCompare(two.name),
            )
            .map((voice) =>
                Object.assign(document.createElement("option"), {
                    textContent: voice.name,
                    value: voice.voiceURI,
                }),
            ),
    )

    const selectedIndex = [...voiceSelect.children].findIndex(
        (child) => child instanceof HTMLOptionElement && child.value == selected,
    )
    voiceSelect.selectedIndex = Math.max(0, selectedIndex)
}
