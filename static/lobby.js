import io from "https://cdn.socket.io/4.7.5/socket.io.esm.min.js";
const socket = io();
socket.on("message", handleMessage);
function handleMessage(message) {
	console.log(message);
}
socket.send({ action: "join", room: "G3RK0D", player: "b" });
