import io from "https://cdn.socket.io/4.7.5/socket.io.esm.min.js";
const socket = io();
socket.on("message", (message) => {
	console.log(message);
	if (!("action" in message)) return;
	switch (message.action) {
		case "join": {
			const money = Object.assign(document.createElement("p"), { className: "money" });
			money.append(
				Object.assign(document.createElement("span"), {
					className: "score",
					textContent: "$0.00",
				}),
			);

			const image = Object.assign(document.createElement("img"), {
				src: `https://api.dicebear.com/5.x/fun-emoji/png?${new URLSearchParams({
					backgroundType: "gradientLinear,solid",
					seed: message.player,
				})}`,
				alt: `${message.player}'s avatar`,
			});

			const playerDiv = Object.assign(document.createElement("div"), { className: "player" });
			playerDiv.append(
				image,
				Object.assign(document.createElement("div"), { className: "timer" }),
				money,
				Object.assign(document.createElement("p"), {
					className: "name",
					textContent: message.player,
				}),
			);
			document.querySelector(".players")?.append(playerDiv);
			break;
		}
	}
});

const playerElement = document.querySelector("[name=player]");
const playerId = playerElement instanceof HTMLMetaElement && playerElement.content;
const room = document.querySelector("h2")?.innerText;
socket.send({ action: "join", room: room, player: playerId });
