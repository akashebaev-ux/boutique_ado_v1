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

    // ----------------------------------------
    // OPEN CHATBOT
    // ----------------------------------------

    toggle.addEventListener("click", () => {
        chatWindow.hidden = false;
        input.focus();
    });

    // ----------------------------------------
    // CLOSE CHATBOT
    // ----------------------------------------

    close.addEventListener("click", () => {
        chatWindow.hidden = true;
    });

    // ----------------------------------------
    // DJANGO CSRF COOKIE
    // ----------------------------------------

    function getCookie(name) {
        let cookieValue = null;

        if (
            document.cookie &&
            document.cookie !== ""
        ) {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (
                    cookie.startsWith(name + "=")
                ) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }

    // ----------------------------------------
    // ADD CHAT MESSAGE
    // ----------------------------------------

    function addMessage(message, sender) {
        const messageElement =
            document.createElement("div");

        messageElement.classList.add(
            "chat-message",
            sender === "user"
                ? "user-message"
                : "bot-message"
        );

        messageElement.textContent = message;

        messages.appendChild(messageElement);

        messages.scrollTop =
            messages.scrollHeight;
    }

    // ----------------------------------------
    // REMOVE OLD DYNAMIC BUTTONS
    // ----------------------------------------

    function removeDynamicButtons() {
        const groups = messages.querySelectorAll(
            ".chatbot-option-group, .chatbot-actions"
        );

        groups.forEach((group) => {
            group.remove();
        });
    }

    // ----------------------------------------
    // QUESTION OPTION BUTTONS
    // ----------------------------------------

    function addOptionButtons(options) {
        if (
            !options ||
            options.length === 0
        ) {
            return;
        }

        const group =
            document.createElement("div");

        group.classList.add(
            "chatbot-option-group"
        );

        options.forEach((option) => {
            const button =
                document.createElement("button");

            button.type = "button";

            button.classList.add(
                "chatbot-option-button"
            );

            button.textContent =
                option.label;

            button.addEventListener(
                "click",
                () => {
                    sendMessage(
                        option.value,
                        option.label
                    );
                }
            );

            group.appendChild(button);
        });

        messages.appendChild(group);

        messages.scrollTop =
            messages.scrollHeight;
    }

    // ----------------------------------------
    // FINAL YES / NO BUTTONS
    // ----------------------------------------

    function addActionButtons(action) {
        if (!action) {
            return;
        }

        const actions =
            document.createElement("div");

        actions.classList.add(
            "chatbot-actions"
        );

        // YES
        const yesButton =
            document.createElement("button");

        yesButton.type = "button";

        yesButton.classList.add(
            "chatbot-action-button"
        );

        yesButton.textContent =
            action.label || "Yes, show me";

        yesButton.addEventListener(
            "click",
            () => {
                if (
                    action.type === "navigate" &&
                    action.url
                ) {
                    window.location.href =
                        action.url;
                }
            }
        );

        // NO
        const noButton =
            document.createElement("button");

        noButton.type = "button";

        noButton.classList.add(
            "chatbot-action-button"
        );

        noButton.textContent =
            "No, thanks";

        noButton.addEventListener(
            "click",
            () => {
                actions.remove();

                addMessage(
                    "No problem! What else can I help you with?",
                    "bot"
                );

                input.focus();
            }
        );

        actions.appendChild(
            yesButton
        );

        actions.appendChild(
            noButton
        );

        messages.appendChild(
            actions
        );

        messages.scrollTop =
            messages.scrollHeight;
    }

    // ----------------------------------------
    // SEND MESSAGE TO DJANGO
    // ----------------------------------------

    async function sendMessage(
        message,
        displayMessage = message
    ) {

        removeDynamicButtons();

        addMessage(
            displayMessage,
            "user"
        );

        input.disabled = true;

        try {

            const response = await fetch(
                "/chatbot/api/message/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            getCookie(
                                "csrftoken"
                            )
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    "Chatbot request failed."
                );
            }

            // BOT RESPONSE
            addMessage(
                data.answer,
                "bot"
            );

            // QUESTION OPTIONS
            if (data.options) {
                addOptionButtons(
                    data.options
                );
            }

            // FINAL ACTION
            if (data.action) {
                addActionButtons(
                    data.action
                );
            }

        } catch (error) {

            console.error(
                "Chatbot error:",
                error
            );

            addMessage(
                "Sorry, I couldn't process your request right now.",
                "bot"
            );

        } finally {

            input.disabled = false;

            input.focus();
        }
    }

    // ----------------------------------------
    // CUSTOMER TYPES MESSAGE
    // ----------------------------------------

    form.addEventListener(
        "submit",
        (event) => {

            event.preventDefault();

            const message =
                input.value.trim();

            if (!message) {
                return;
            }

            input.value = "";

            sendMessage(message);
        }
    );

    // ----------------------------------------
    // PRODUCTS / DELIVERY / RETURNS
    // ----------------------------------------

    suggestionButtons.forEach(
        (button) => {

            button.addEventListener(
                "click",
                () => {

                    const message =
                        button.dataset.message;

                    if (!message) {
                        return;
                    }

                    sendMessage(message);
                }
            );
        }
    );
});
