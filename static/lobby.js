import setMessageHandler from "./websocket.js"

setMessageHandler((message) => {
    switch (message.action) {
        case "join": {
            if (typeof message.player !== "string") break

            const money = Object.assign(document.createElement("p"), {
                className: "money",
            })
            money.append(
                Object.assign(document.createElement("span"), {
                    className: "score",
                    textContent: "$0.00",
                }),
            )

            const image = Object.assign(document.createElement("img"), {
                src: `https://api.dicebear.com/5.x/fun-emoji/png?${new URLSearchParams({
                    backgroundType: "gradientLinear,solid",
                    seed: message.player,
                })}`,
                alt: `${message.player}'s avatar`,
            })

            const playerDiv = Object.assign(document.createElement("div"), {
                className: "player",
            })
            playerDiv.append(
                image,
                Object.assign(document.createElement("div"), {className: "timer"}),
                money,
                Object.assign(document.createElement("p"), {
                    className: "name",
                    textContent: message.player,
                }),
            )
            document.querySelector(".players")?.append(playerDiv)
            break
        }
    }
})
