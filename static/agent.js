document.addEventListener('DOMContentLoaded', () => {
    const availableList = document.getElementById('available-list');
    const activeList = document.getElementById('active-list');

    async function loadConversations() {
        try {
            const response = await fetch('/agent/messages');
            const data = await response.json();

            // Load available conversations
            availableList.innerHTML = '';
            if (data.available.length === 0) {
                availableList.innerHTML = '<p style="text-align: center; color: #666; font-style: italic;">No available chats at the moment.</p>';
            } else {
                data.available.forEach(conv => {
                    const convDiv = document.createElement('div');
                    convDiv.classList.add('conversation-item');
                    convDiv.innerHTML = `<h3>Chat #${conv.id}</h3>`;
                    const lastMessage = conv.messages[conv.messages.length - 1];
                    if (lastMessage) {
                        convDiv.innerHTML += `<p><strong>Last message:</strong> ${lastMessage.content.length > 50 ? lastMessage.content.substring(0, 50) + '...' : lastMessage.content}</p>`;
                        convDiv.innerHTML += `<p><strong>Time:</strong> ${new Date(lastMessage.timestamp).toLocaleString()}</p>`;
                    }
                    const takeBtn = document.createElement('button');
                    takeBtn.classList.add('take-chat-btn');
                    takeBtn.textContent = 'Take Chat';
                    takeBtn.addEventListener('click', () => takeChat(conv.id));
                    convDiv.appendChild(takeBtn);
                    availableList.appendChild(convDiv);
                });
            }

            // Load active conversations
            activeList.innerHTML = '';
            if (data.active.length === 0) {
                activeList.innerHTML = '<p style="text-align: center; color: #666; font-style: italic;">No active chats assigned to you.</p>';
            } else {
                data.active.forEach(conv => {
                    const convDiv = document.createElement('div');
                    convDiv.classList.add('conversation-item');
                    convDiv.innerHTML = `<h3>Chat #${conv.id}</h3>`;
                    const chatBox = document.createElement('div');
                    chatBox.classList.add('chat-box');
                    chatBox.style.maxHeight = '200px';
                    chatBox.style.overflowY = 'auto';
                    conv.messages.forEach(msg => {
                        const msgDiv = document.createElement('div');
                        msgDiv.classList.add('message');
                        msgDiv.innerHTML = `<strong>${msg.sender_id === 0 ? 'Bot' : 'Customer'}:</strong> ${msg.content}<br><small>${new Date(msg.timestamp).toLocaleString()}</small>`;
                        chatBox.appendChild(msgDiv);
                    });
                    convDiv.appendChild(chatBox);

                    const input = document.createElement('input');
                    input.classList.add('reply-input');
                    input.type = 'text';
                    input.placeholder = 'Type your reply here...';
                    const sendBtn = document.createElement('button');
                    sendBtn.classList.add('reply-btn');
                    sendBtn.textContent = 'Send Reply';
                    sendBtn.addEventListener('click', () => {
                        sendReply(conv.id, input.value, chatBox);
                        input.value = '';
                    });
                    input.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            sendReply(conv.id, input.value, chatBox);
                            input.value = '';
                        }
                    });
                    convDiv.appendChild(input);
                    convDiv.appendChild(sendBtn);
                    activeList.appendChild(convDiv);
                });
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    async function takeChat(convId) {
        try {
            const response = await fetch(`/agent/take_chat/${convId}`, {
                method: 'POST'
            });
            const result = await response.json();
            if (result.status === 'taken') {
                loadConversations(); // Refresh
            } else {
                alert('Failed to take chat: ' + result.error);
            }
        } catch (error) {
            console.error('Error taking chat:', error);
            alert('An error occurred while taking the chat.');
        }
    }

    async function sendReply(convId, reply, chatBox) {
        if (!reply.trim()) return;
        try {
            const response = await fetch('/agent/reply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ conversation_id: convId, reply })
            });
            const result = await response.json();
            if (result.status === 'replied') {
                const msgDiv = document.createElement('div');
                msgDiv.classList.add('message', 'agent');
                msgDiv.innerHTML = `<strong>You:</strong> ${reply}<br><small>${new Date().toLocaleString()}</small>`;
                chatBox.appendChild(msgDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                alert('Failed to send reply: ' + result.error);
            }
        } catch (error) {
            console.error('Error sending reply:', error);
            alert('An error occurred while sending the reply.');
        }
    }

    loadConversations();
    setInterval(loadConversations, 10000); // Refresh every 10 seconds
});
