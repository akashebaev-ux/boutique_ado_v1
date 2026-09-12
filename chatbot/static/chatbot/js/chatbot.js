document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("chatbot-toggle");
    const chatWindow = document.getElementById("chatbot-window");
    const close = document.getElementById("chatbot-close");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");
    const messages = document.getElementById("chatbot-messages");

    const suggestionButtons = document.querySelectorAll(
        ".chatbot-suggestion"
    );

    if (
        !toggle ||
        !chatWindow ||
        !close ||
        !form ||
        !input ||
        !messages
    ) {
        return;
    }

    // Open chatbot
    toggle.addEventListener("click", () => {
        chatWindow.hidden = false;
        input.focus();
    });

    // Close chatbot
    close.addEventListener("click", () => {
        chatWindow.hidden = true;
    });


    // Get Django CSRF cookie
    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }


    // Add message to chatbot
    function addMessage(message, sender) {
        const messageElement = document.createElement("div");

        messageElement.classList.add(
            "chat-message",
            sender === "user"
                ? "user-message"
                : "bot-message"
        );

        messageElement.textContent = message;

        messages.appendChild(messageElement);

        messages.scrollTop = messages.scrollHeight;
    }


    // Send message to Django
    async function sendMessage(message) {
        addMessage(message, "user");

        try {
            const response = await fetch(
                "/chatbot/api/message/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Something went wrong."
                );
            }

            addMessage(data.answer, "bot");

        } catch (error) {
            console.error(error);

            addMessage(
                "Sorry, I couldn't process your request.",
                "bot"
            );
        }
    }


    // Message typed by customer
    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const message = input.value.trim();

        if (!message) {
            return;
        }

        input.value = "";

        sendMessage(message);

        input.focus();
    });


    // Quick suggestion buttons
    suggestionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const message = button.dataset.message;

            if (!message) {
                return;
            }

            sendMessage(message);
        });
    });
});
