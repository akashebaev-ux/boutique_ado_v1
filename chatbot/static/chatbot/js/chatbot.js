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

    // Display a user message
    function addUserMessage(message) {
        const userMessage = document.createElement("div");

        userMessage.classList.add(
            "chat-message",
            "user-message"
        );

        userMessage.textContent = message;

        messages.appendChild(userMessage);

        messages.scrollTop = messages.scrollHeight;
    }

    // Handle typed message
    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const message = input.value.trim();

        if (!message) {
            return;
        }

        addUserMessage(message);

        input.value = "";
        input.focus();
    });

    // Handle quick suggestion buttons
    suggestionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const message = button.dataset.message;

            if (!message) {
                return;
            }

            addUserMessage(message);
        });
    });
});
