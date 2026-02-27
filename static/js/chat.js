/**
 * AI College Chatbot - AJAX Chat Handler
 * Manages chat sessions, message sending, UI updates, and /services command.
 */

let currentChatId = null;

// ── Services Questions Data (70+ questions, 15 categories) ─────────────────
const SERVICES_QUESTIONS = [
    {
        category: '💰 Fees & Payment',
        questions: [
            'What is the semester fee for B.Tech CSE?',
            'What is the total 4-year course fee?',
            'What are the fee payment methods available?',
            'Can I pay fees in installments or EMI?',
            'What is the fee for Semester 7 and 8?',
            'What is GrayQuest 0% EMI option for fees?',
            'How many installments can I split the fee into?',
        ]
    },
    {
        category: '📋 Attendance',
        questions: [
            'My attendance is 45/60, what is my percentage?',
            'What is the minimum attendance required for exams?',
            'How many lectures can I skip and still be exam eligible?',
            'I attended 30 out of 50 classes, am I eligible for exams?',
            'What happens if my attendance is below 80%?',
            'How many more lectures do I need to reach 80% attendance?',
            'I have 20 lectures remaining and my attendance is 65%',
            'What is the 5-minute late rule for attendance?',
            'Can I be removed from rolls for low attendance?',
            'What attendance is needed for MYSY scholarship renewal?',
        ]
    },
    {
        category: '🏆 MYSY Scholarship',
        questions: [
            'Am I eligible for MYSY scholarship?',
            'What is the MYSY scholarship benefit amount?',
            'How do I apply for MYSY scholarship?',
            'What is the income limit for MYSY scholarship?',
            'Does MYSY scholarship cover hostel expenses?',
            'What is the book allowance under MYSY?',
        ]
    },
    {
        category: '📅 Academic Calendar',
        questions: [
            'When are the mid-semester exams in 2025-26?',
            'When are the end-semester theory exams?',
            'When are the end-semester practical exams?',
            'When does the odd semester start in 2025?',
            'When does the even semester start in 2026?',
            'When is the winter vacation 2025-26?',
            'When is the summer vacation 2026?',
        ]
    },
    {
        category: '📚 Subjects & Syllabus',
        questions: [
            'What subjects are in Semester 1?',
            'What subjects are in Semester 2?',
            'What subjects are in Semester 3?',
            'What subjects are in Semester 4?',
            'What subjects are in Semester 5?',
            'What subjects are in Semester 6?',
            'What subjects are in Semester 7?',
            'What subjects are in Semester 8?',
            'Tell me about Advanced Java Technology (AJT)',
            'What topics are covered in Machine Learning?',
            'What is the syllabus for DBMS?',
            'What is the syllabus for Operating System?',
            'Tell me about Cloud Computing subject',
        ]
    },
    {
        category: '📖 Study Materials',
        questions: [
            'Give me Semester 3 study materials link',
            'Give me Semester 5 study materials link',
            'Where can I find DBMS notes?',
            'Notes for Advanced Java Technology (AJT)',
            'Previous year papers for Operating System',
            'Study material for Cloud Computing',
            'Semester 6 drive link for study materials',
            'Where can I find Machine Learning notes?',
        ]
    },
    {
        category: '📝 Exam Format',
        questions: [
            'What is the exam pattern for theory subjects?',
            'What is CIE and ESE in exams?',
            'How are marks distributed in a 200-mark subject?',
            'What is the marking scheme for practical subjects?',
            'What is the mid-semester exam pattern?',
            'What is the difference between CIE and ESE?',
        ]
    },
    {
        category: '🎯 Grading System',
        questions: [
            'What grade do I get if I score 75 out of 100?',
            'What grade do I get if I score 145 out of 200?',
            'What grade do I get if I score 38 marks?',
            'What are all the grade letters and their grade points?',
            'What CGPA do I need for First Class with Distinction?',
            'What does Grade F mean?',
            'What does AB grade mean on my marksheet?',
            'What does the * symbol mean on my marksheet?',
            'What does the + symbol on my marksheet mean?',
        ]
    },
    {
        category: '✅ Passing Marks',
        questions: [
            'What are the passing marks for a 100-mark subject?',
            'What are the passing marks for a 200-mark subject?',
            'Passing marks for Advanced Java Technology (AJT)',
            'Minimum marks to pass Operating System',
            'Will I fail if I get 35 marks in a theory subject?',
            'Passing marks for DBMS?',
            'What is the minimum marks to pass in Machine Learning?',
            'How many marks do I need to pass a practical subject?',
        ]
    },
    {
        category: '🧮 CGPA & SGPA',
        questions: [
            'How do I calculate my CGPA?',
            'How do I calculate my SGPA for this semester?',
            'Convert 8.5 CGPA to percentage',
            'Convert 7.2 CGPA to percentage',
            'What is the CGPA formula at Indus University?',
            'What CGPA is needed for First Class?',
            'What CGPA is needed for Second Class?',
            'What CGPA is needed for Pass Class?',
        ]
    },
    {
        category: '🔄 Re-Assessment',
        questions: [
            'What is the re-assessment fee per subject?',
            'How do I apply for re-checking of marks?',
            'Can I reassess practical exam marks?',
            'What is the difference between re-assessment and re-checking?',
            'Which subjects are eligible for re-assessment?',
            'What is the re-checking fee with late fees?',
        ]
    },
    {
        category: '📗 Library',
        questions: [
            'How many books can I borrow from the library?',
            'What are the library timings?',
            'What is the fine for overdue library books?',
            'What rules must I follow in the library?',
            'Can I take journals outside the library?',
            'How do I get a No Due certificate from the library?',
        ]
    },
    {
        category: '🚦 Discipline & Rules',
        questions: [
            'What is the dress code at Indus University?',
            'Are mobile phones allowed in class?',
            'What are the hostel rules?',
            'What is the penalty for ragging?',
            'What are the rules about smoking or alcohol on campus?',
            'What are the major disciplinary penalties?',
        ]
    },
    {
        category: '💼 Placement',
        questions: [
            'What is the highest placement package from Indus University?',
            'Which companies recruit from Indus University?',
            'What is the average placement package?',
            'What training programs are offered for placement?',
            'How do I contact the placement office?',
            'What internship opportunities are available?',
        ]
    },
    {
        category: '📋 Back Paper / Supplementary',
        questions: [
            'How do I apply for a back paper exam?',
            'What is the process for supplementary exams?',
            'What happens if I fail a subject?',
        ]
    },
];


// ─────────────────────────────────────────────────────────────────────────────
// DOM Ready
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    const msgInput      = document.getElementById('messageInput');
    const sendBtn       = document.getElementById('sendBtn');
    const newChatBtn    = document.getElementById('newChatBtn');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar       = document.getElementById('chatSidebar');
    const sidebarOverlay= document.getElementById('sidebarOverlay');

    sendBtn.addEventListener('click', sendMessage);

    msgInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    msgInput.addEventListener('input', () => {
        msgInput.style.height = 'auto';
        msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';
    });

    newChatBtn.addEventListener('click', createNewChat);

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

    document.querySelectorAll('.chat-list-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.closest('.chat-delete')) return;
            loadChat(item.dataset.chatId);
        });
    });

    document.querySelectorAll('.chat-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChat(btn.dataset.chatId, btn.closest('.chat-list-item'));
        });
    });

    // Keyboard shortcut: Escape closes services modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeServicesModal();
    });

    const pendingChatId = localStorage.getItem('loadChat');
    if (pendingChatId) {
        localStorage.removeItem('loadChat');
        loadChat(pendingChatId);
    } else if (!currentChatId) {
        showWelcome();
    }
});


// ─────────────────────────────────────────────────────────────────────────────
// Send Message
// ─────────────────────────────────────────────────────────────────────────────

function sendMessage() {
    const input   = document.getElementById('messageInput');
    const message = input.value.trim();
    if (!message) return;

    // ── Handle slash commands ──────────────────────────────────────────────
    const cmd = message.toLowerCase();
    if (cmd === '/services' || cmd === '/questions' || cmd === '/browse') {
        input.value = '';
        input.style.height = 'auto';
        appendServicesCard();
        return;
    }

    // ── Normal message flow ────────────────────────────────────────────────
    appendMessage('user', message);
    input.value = '';
    input.style.height = 'auto';

    showTyping(true);
    document.getElementById('sendBtn').disabled = true;

    fetch('/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, chat_id: currentChatId })
    })
    .then(res => res.json())
    .then(data => {
        showTyping(false);
        document.getElementById('sendBtn').disabled = false;

        if (data.error) {
            appendMessage('bot', 'Sorry, something went wrong. Please try again.');
            return;
        }
        if (!currentChatId && data.chat_id) {
            currentChatId = data.chat_id;
            addChatToSidebar(data.chat_id, message.substring(0, 50));
        }
        appendMessage('bot', data.response);
    })
    .catch(err => {
        showTyping(false);
        document.getElementById('sendBtn').disabled = false;
        appendMessage('bot', 'Connection error. Please check your internet and try again.');
        console.error('Chat error:', err);
    });
}


// ─────────────────────────────────────────────────────────────────────────────
// Message Rendering
// ─────────────────────────────────────────────────────────────────────────────

function appendMessage(sender, content) {
    const chatMessages = document.getElementById('chatMessages');

    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const row    = document.createElement('div');
    row.className = `message-row ${sender}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = formatResponse(content);

    row.appendChild(bubble);
    chatMessages.appendChild(row);

    // Tip line after every bot message
    if (sender === 'bot') {
        const tip = document.createElement('div');
        tip.className = 'chat-tip';
        tip.innerHTML =
            '💡 Type <span class="tip-cmd" onclick="triggerServicesCommand()">/services</span>' +
            ' or <span class="tip-cmd" onclick="triggerServicesCommand()">/questions</span>' +
            ' to browse all topics';
        chatMessages.appendChild(tip);
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function formatResponse(text) {
    let html = text;

    // Tables
    if (html.includes('|') && html.includes('---')) {
        const lines = html.split('\n');
        let inTable = false, tableHtml = '', processed = [];
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
                if (trimmed.replace(/[|\-\s]/g, '') === '') continue;
                if (!inTable) {
                    tableHtml = '<table><thead><tr>';
                    trimmed.split('|').filter(c => c.trim()).forEach(c => {
                        tableHtml += `<th>${c.trim()}</th>`;
                    });
                    tableHtml += '</tr></thead><tbody>';
                    inTable = true;
                } else {
                    tableHtml += '<tr>';
                    trimmed.split('|').filter(c => c.trim()).forEach(c => {
                        tableHtml += `<td>${c.trim()}</td>`;
                    });
                    tableHtml += '</tr>';
                }
            } else {
                if (inTable) {
                    tableHtml += '</tbody></table>';
                    processed.push(tableHtml);
                    inTable = false; tableHtml = '';
                }
                processed.push(trimmed);
            }
        }
        if (inTable) { tableHtml += '</tbody></table>'; processed.push(tableHtml); }
        html = processed.join('\n');
    }

    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/(?<!\w)_(.+?)_(?!\w)/g, '<em>$1</em>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    html = html.replace(/\n/g, '<br>');
    return html;
}


// ─────────────────────────────────────────────────────────────────────────────
// Typing Indicator
// ─────────────────────────────────────────────────────────────────────────────

function showTyping(show) {
    const indicator = document.getElementById('typingIndicator');
    if (!indicator) return;
    indicator.style.display = show ? 'block' : 'none';
    if (show) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}


// ─────────────────────────────────────────────────────────────────────────────
// Welcome Screen
// ─────────────────────────────────────────────────────────────────────────────

function showWelcome() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="welcome-message text-center py-5">
            <div style="font-size:3rem;margin-bottom:1rem;opacity:0.6;">
                <i class="bi bi-robot"></i>
            </div>
            <h4 style="font-weight:700;color:#1a1a2e;">College AI Assistant</h4>
            <p style="color:#6c757d;max-width:400px;margin:0.5rem auto 1.5rem;">
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
            <div class="welcome-tip">
                💡 <strong>Tip:</strong> Type
                <span class="tip-cmd" onclick="triggerServicesCommand()">/services</span>
                or
                <span class="tip-cmd" onclick="triggerServicesCommand()">/questions</span>
                to browse <strong>70+ questions</strong> I can answer instantly.
            </div>
        </div>
    `;
}


function useSuggestion(btn) {
    const input = document.getElementById('messageInput');
    input.value = btn.textContent.trim();
    sendMessage();
}


// ─────────────────────────────────────────────────────────────────────────────
// Services Card (shown in chat when /services is typed)
// ─────────────────────────────────────────────────────────────────────────────

function appendServicesCard() {
    const chatMessages = document.getElementById('chatMessages');
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const row = document.createElement('div');
    row.className = 'message-row bot';
    row.innerHTML = `
        <div class="services-card">
            <div class="services-card-icon">📋</div>
            <div class="services-card-body">
                <strong>Browse All Topics</strong>
                <p>Explore <strong>70+ questions</strong> across fees, attendance, subjects,
                CGPA, exams, grading, placement, and more.</p>
            </div>
            <button class="btn-view-options" onclick="openServicesModal()">
                <i class="bi bi-grid-3x3-gap me-1"></i> View Options
            </button>
        </div>
    `;
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// ─────────────────────────────────────────────────────────────────────────────
// Services Modal
// ─────────────────────────────────────────────────────────────────────────────

function openServicesModal() {
    const modal = document.getElementById('servicesModal');
    modal.classList.add('open');
    document.getElementById('servicesSearch').value = '';
    renderServicesBody('');
    setTimeout(() => document.getElementById('servicesSearch').focus(), 280);
}

function closeServicesModal() {
    const modal = document.getElementById('servicesModal');
    if (modal) modal.classList.remove('open');
}

function closeServicesModalOutside(event) {
    if (event.target === document.getElementById('servicesModal')) {
        closeServicesModal();
    }
}

function renderServicesBody(filter) {
    const body  = document.getElementById('servicesBody');
    const query = (filter || '').toLowerCase().trim();
    let   html  = '';
    let   total = 0;

    for (const group of SERVICES_QUESTIONS) {
        const matching = query
            ? group.questions.filter(q => q.toLowerCase().includes(query))
            : group.questions;
        if (matching.length === 0) continue;

        total += matching.length;
        html += `<div class="services-category">`;
        html += `<div class="services-category-title">${escapeHtml(group.category)}</div>`;
        html += `<div class="services-questions-grid">`;
        for (const q of matching) {
            const safe = q.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
            html += `<button class="services-q-btn" onclick="selectQuestion('${safe}')">${escapeHtml(q)}</button>`;
        }
        html += `</div></div>`;
    }

    if (total === 0) {
        html = `
            <div class="services-no-results">
                <i class="bi bi-search" style="font-size:2rem;opacity:0.3;display:block;margin-bottom:0.5rem;"></i>
                No questions found for <strong>"${escapeHtml(filter)}"</strong>.<br>
                <small>Try a different keyword like <em>fee</em>, <em>attendance</em>, or <em>cgpa</em>.</small>
            </div>`;
    }

    body.innerHTML = html;
}

function selectQuestion(question) {
    closeServicesModal();
    const input = document.getElementById('messageInput');
    input.value = question;
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    sendMessage();
}

// Called from tip links inside messages
function triggerServicesCommand() {
    const input = document.getElementById('messageInput');
    input.value = '/services';
    sendMessage();
}


// ─────────────────────────────────────────────────────────────────────────────
// Chat Management
// ─────────────────────────────────────────────────────────────────────────────

function createNewChat() {
    currentChatId = null;
    showWelcome();
    document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));
    const sidebar = document.getElementById('chatSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
}


function loadChat(chatId) {
    currentChatId = chatId;

    document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));
    const item = document.querySelector(`.chat-list-item[data-chat-id="${chatId}"]`);
    if (item) item.classList.add('active');

    const sidebar = document.getElementById('chatSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');

    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"></div></div>';

    fetch(`/api/chat/${chatId}/messages`)
        .then(res => res.json())
        .then(messages => {
            chatMessages.innerHTML = '';
            if (messages.length === 0) { showWelcome(); return; }
            messages.forEach(m => appendMessage(m.sender, m.content));
        })
        .catch(() => {
            chatMessages.innerHTML = '<div class="text-center text-danger py-3">Failed to load messages.</div>';
        });
}


function deleteChat(chatId, element) {
    if (!confirm('Delete this chat?')) return;
    fetch(`/api/chat/${chatId}/delete`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                element.remove();
                if (currentChatId === chatId) { currentChatId = null; showWelcome(); }
            }
        })
        .catch(err => console.error('Delete error:', err));
}


function addChatToSidebar(chatId, title) {
    const chatList = document.getElementById('chatList');
    const item     = document.createElement('div');
    item.className  = 'chat-list-item active';
    item.dataset.chatId = chatId;
    item.innerHTML = `
        <span class="chat-title"><i class="bi bi-chat-dots me-2"></i>${escapeHtml(title)}</span>
        <span class="chat-delete" data-chat-id="${chatId}"><i class="bi bi-trash"></i></span>
    `;
    document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));
    chatList.prepend(item);
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
