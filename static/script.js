document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('send-btn');
    const escalateBtn = document.getElementById('escalate-btn');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    let conversationId = null;

    function appendMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = message;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        appendMessage(message, 'user');
        userInput.value = '';
        userInput.focus();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message, conversation_id: conversationId })
            });
            const data = await response.json();
            conversationId = data.conversation_id;
            appendMessage(data.response, 'bot');
        } catch (error) {
            appendMessage('Sorry, I\'m having trouble connecting. Please try again.', 'bot');
        }
    }

    async function escalate() {
        try {
            const response = await fetch('/escalate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ conversation_id: conversationId })
            });
            const data = await response.json();
            if (data.status === 'escalated') {
                appendMessage('Your chat has been escalated to a human agent. They will respond shortly.', 'bot');
                escalateBtn.disabled = true;
                escalateBtn.textContent = 'Escalated';
                // Show feedback container
                const feedbackContainer = document.getElementById('feedback-container');
                feedbackContainer.style.display = 'block';
                const feedbackLink = document.getElementById('feedback-link');
                feedbackLink.href = data.feedback_url || `/feedback/${conversationId}`;
            } else {
                appendMessage('Sorry, there was an issue escalating your chat. Please try again.', 'bot');
            }
        } catch (error) {
            appendMessage('Sorry, I couldn\'t escalate your chat right now. Please try again later.', 'bot');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    escalateBtn.addEventListener('click', escalate);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Focus on input when page loads
    userInput.focus();
});
