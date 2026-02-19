/**
 * AI College Chatbot - AJAX Chat Handler
 * Manages chat sessions, message sending, and UI updates.
 */

let currentChatId = null;

document.addEventListener('DOMContentLoaded', () => {
    const msgInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const newChatBtn = document.getElementById('newChatBtn');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('chatSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    // Send on Enter (Shift+Enter for new line)
    msgInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    msgInput.addEventListener('input', () => {
        msgInput.style.height = 'auto';
        msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';
    });

    // New chat button
    newChatBtn.addEventListener('click', createNewChat);

    // Mobile sidebar toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            sidebarOverlay.classList.toggle('show');
        });
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('show');
        });
    }

    // Chat list item clicks
    document.querySelectorAll('.chat-list-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.closest('.chat-delete')) return;
            const chatId = item.dataset.chatId;
            loadChat(chatId);
        });
    });

    // Delete buttons
    document.querySelectorAll('.chat-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const chatId = btn.dataset.chatId;
            deleteChat(chatId, btn.closest('.chat-list-item'));
        });
    });

    // Check if dashboard redirected us to a specific chat
    const pendingChatId = localStorage.getItem('loadChat');
    if (pendingChatId) {
        localStorage.removeItem('loadChat');
        loadChat(pendingChatId);
    } else if (!currentChatId) {
        showWelcome();
    }
});


function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    if (!message) return;

    // Add user message to UI
    appendMessage('user', message);
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    showTyping(true);

    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;

    // Send to API
    fetch('/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            chat_id: currentChatId
        })
    })
    .then(res => res.json())
    .then(data => {
        showTyping(false);
        sendBtn.disabled = false;

        if (data.error) {
            appendMessage('bot', 'Sorry, something went wrong. Please try again.');
            return;
        }

        // Set chat ID if new
        if (!currentChatId && data.chat_id) {
            currentChatId = data.chat_id;
            addChatToSidebar(data.chat_id, message.substring(0, 50));
        }

        appendMessage('bot', data.response);
    })
    .catch(err => {
        showTyping(false);
        sendBtn.disabled = false;
        appendMessage('bot', 'Connection error. Please check your internet and try again.');
        console.error('Chat error:', err);
    });
}


function appendMessage(sender, content) {
    const chatMessages = document.getElementById('chatMessages');

    // Remove welcome message if present
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const row = document.createElement('div');
    row.className = `message-row ${sender}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Convert markdown-like formatting to HTML
    bubble.innerHTML = formatResponse(content);

    row.appendChild(bubble);
    chatMessages.appendChild(row);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function formatResponse(text) {
    // Convert markdown-style formatting to HTML
    let html = text;

    // Tables: | header | header | pattern
    if (html.includes('|') && html.includes('---')) {
        const lines = html.split('\n');
        let inTable = false;
        let tableHtml = '';
        let processed = [];

        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
                if (trimmed.replace(/[|\-\s]/g, '') === '') {
                    // Separator row, skip
                    continue;
                }
                if (!inTable) {
                    tableHtml = '<table><thead><tr>';
                    const cells = trimmed.split('|').filter(c => c.trim());
                    cells.forEach(c => { tableHtml += `<th>${c.trim()}</th>`; });
                    tableHtml += '</tr></thead><tbody>';
                    inTable = true;
                } else {
                    const cells = trimmed.split('|').filter(c => c.trim());
                    tableHtml += '<tr>';
                    cells.forEach(c => { tableHtml += `<td>${c.trim()}</td>`; });
                    tableHtml += '</tr>';
                }
            } else {
                if (inTable) {
                    tableHtml += '</tbody></table>';
                    processed.push(tableHtml);
                    inTable = false;
                    tableHtml = '';
                }
                processed.push(trimmed);
            }
        }
        if (inTable) {
            tableHtml += '</tbody></table>';
            processed.push(tableHtml);
        }
        html = processed.join('\n');
    }

    // Bold: **text**
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic: _text_
    html = html.replace(/(?<!\w)_(.+?)_(?!\w)/g, '<em>$1</em>');

    // Links: [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

    // Line breaks
    html = html.replace(/\n/g, '<br>');

    return html;
}


function showTyping(show) {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.style.display = show ? 'block' : 'none';
        if (show) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
}


function showWelcome() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="welcome-message text-center py-5">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.6;">
                <i class="bi bi-robot"></i>
            </div>
            <h4 style="font-weight: 700; color: #1a1a2e;">College AI Assistant</h4>
            <p style="color: #6c757d; max-width: 400px; margin: 0.5rem auto 1.5rem;">
                Ask me about attendance, subjects, CGPA, exam patterns, study materials, or academic rules.
            </p>
            <div class="d-flex flex-wrap justify-content-center gap-2">
                <button class="btn btn-outline-primary btn-sm rounded-pill suggestion-btn" onclick="useSuggestion(this)">
                    What subjects are in semester 5?
                </button>
                <button class="btn btn-outline-primary btn-sm rounded-pill suggestion-btn" onclick="useSuggestion(this)">
                    My attendance is 45/60
                </button>
                <button class="btn btn-outline-primary btn-sm rounded-pill suggestion-btn" onclick="useSuggestion(this)">
                    How to calculate CGPA?
                </button>
                <button class="btn btn-outline-primary btn-sm rounded-pill suggestion-btn" onclick="useSuggestion(this)">
                    What is the exam pattern?
                </button>
            </div>
        </div>
    `;
}


function useSuggestion(btn) {
    const input = document.getElementById('messageInput');
    input.value = btn.textContent.trim();
    sendMessage();
}


function createNewChat() {
    currentChatId = null;
    showWelcome();

    // Remove active class from all items
    document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));

    // Close mobile sidebar
    const sidebar = document.getElementById('chatSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
}


function loadChat(chatId) {
    currentChatId = chatId;

    // Update active state
    document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));
    const item = document.querySelector(`.chat-list-item[data-chat-id="${chatId}"]`);
    if (item) item.classList.add('active');

    // Close mobile sidebar
    const sidebar = document.getElementById('chatSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');

    // Load messages
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"></div></div>';

    fetch(`/api/chat/${chatId}/messages`)
        .then(res => res.json())
        .then(messages => {
            chatMessages.innerHTML = '';
            if (messages.length === 0) {
                showWelcome();
                return;
            }
            messages.forEach(m => {
                appendMessage(m.sender, m.content);
            });
        })
        .catch(err => {
            chatMessages.innerHTML = '<div class="text-center text-danger py-3">Failed to load messages.</div>';
            console.error('Load chat error:', err);
        });
}


function deleteChat(chatId, element) {
    if (!confirm('Delete this chat?')) return;

    fetch(`/api/chat/${chatId}/delete`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                element.remove();
                if (currentChatId === chatId) {
                    currentChatId = null;
                    showWelcome();
                }
            }
        })
        .catch(err => console.error('Delete error:', err));
}


function addChatToSidebar(chatId, title) {
    const chatList = document.getElementById('chatList');
    const item = document.createElement('div');
    item.className = 'chat-list-item active';
    item.dataset.chatId = chatId;
    item.innerHTML = `
        <span class="chat-title"><i class="bi bi-chat-dots me-2"></i>${escapeHtml(title)}</span>
        <span class="chat-delete" data-chat-id="${chatId}"><i class="bi bi-trash"></i></span>
    `;

    // Remove active from others
    document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));

    chatList.prepend(item);

    // Bind events
    item.addEventListener('click', (e) => {
        if (e.target.closest('.chat-delete')) return;
        loadChat(chatId);
    });
    item.querySelector('.chat-delete').addEventListener('click', (e) => {
        e.stopPropagation();
        deleteChat(chatId, item);
    });
}


function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
