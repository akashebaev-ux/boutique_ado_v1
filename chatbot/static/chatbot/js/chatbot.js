document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("chatbot-toggle");
    const windowElement = document.getElementById("chatbot-window");
    const close = document.getElementById("chatbot-close");

    if (!toggle || !windowElement || !close) {
        return;
    }

    toggle.addEventListener("click", () => {
        windowElement.hidden = false;
    });

    close.addEventListener("click", () => {
        windowElement.hidden = true;
    });
});
