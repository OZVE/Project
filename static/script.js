document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Documento cargado correctamente");

    if (typeof io === "undefined") {
        console.error("❌ ERROR: socket.io no está definido.");
        return;
    }

    var socket = io();
    socket.on("connect", function () {
        console.log("✅ WebSocket conectado correctamente.");
    });

    var chatBox = document.getElementById("chat-box");
    var sendBtn = document.getElementById("sendBtn");
    var userInput = document.getElementById("userInput");


    function addMessage(sender, message) {
        var messageDiv = document.createElement("div");
        messageDiv.classList.add("alert");
        messageDiv.classList.add(sender === "user" ? "alert-primary" : "alert-secondary");
        messageDiv.classList.add(sender === "user" ? "text-end" : "text-start");
        messageDiv.innerText = message;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }


    function sendMessage() {
        var message = userInput.value.trim();
        if (message === "") return;

        console.log("📨 Enviando mensaje:", message);
        addMessage("user", message);
        socket.emit("user_message", { message: message });
        userInput.value = "";
    }


    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    socket.on("chat_update", function (data) {
        console.log("📩 Mensaje recibido:", data.message);
        addMessage(data.sender, data.message);
    });

    console.log("✅ Eventos de chat inicializados correctamente.");
});
