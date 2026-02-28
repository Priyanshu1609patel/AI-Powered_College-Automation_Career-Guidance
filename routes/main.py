"""
Main application routes: dashboard, chatbot, chat API.
"""
from flask import Blueprint, render_template, request, jsonify, session
from database import query_db, execute_db
from chatbot.engine import ChatbotEngine
from routes.auth import login_required
import uuid

main_bp = Blueprint('main', __name__)
chatbot = ChatbotEngine()


@main_bp.route('/')
def index():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return render_template('login.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']

    # Get recent chats
    recent_chats = query_db(
        """SELECT id, title, created_at FROM chats
           WHERE user_id = %s ORDER BY updated_at DESC LIMIT 5""",
        (user_id,)
    )

    # Get active notices
    notices = query_db(
        """SELECT title, notice_type, created_at FROM notices
           WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > NOW())
           ORDER BY created_at DESC LIMIT 3"""
    )

    # Get semester subjects if semester is set
    subjects = []
    if session.get('semester'):
        subjects = query_db(
            """SELECT s.subject_code, s.subject_name, s.credits
               FROM subjects s
               JOIN semesters sem ON s.semester_id = sem.id
               WHERE sem.semester_number = %s AND s.is_active = TRUE
               ORDER BY s.subject_code""",
            (session['semester'],)
        )

    return render_template(
        'dashboard.html',
        recent_chats=recent_chats,
        notices=notices,
        subjects=subjects,
    )


@main_bp.route('/chatbot')
@login_required
def chatbot_page():
    """Render the chatbot UI page."""
    user_id = session['user_id']

    # Load chat list for sidebar
    chat_list = query_db(
        "SELECT id, title, created_at FROM chats WHERE user_id = %s ORDER BY updated_at DESC LIMIT 20",
        (user_id,)
    )
    return render_template('chatbot.html', chat_list=chat_list)


@main_bp.route('/api/chat/new', methods=['POST'])
@login_required
def new_chat():
    """Create a new chat session."""
    user_id = session['user_id']
    result = execute_db(
        "INSERT INTO chats (user_id, title) VALUES (%s, 'New Chat') RETURNING id, title, created_at",
        (user_id,),
        returning=True
    )
    if result:
        chat = result[0]
        return jsonify({'id': str(chat['id']), 'title': chat['title']})
    return jsonify({'error': 'Failed to create chat'}), 500


@main_bp.route('/api/chat/<chat_id>/messages')
@login_required
def get_messages(chat_id):
    """Get all messages for a chat session."""
    user_id = session['user_id']

    # Verify chat belongs to user
    chat = query_db(
        "SELECT id FROM chats WHERE id = %s AND user_id = %s",
        (chat_id, user_id),
        one=True
    )
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    messages = query_db(
        "SELECT sender, content, created_at FROM messages WHERE chat_id = %s ORDER BY created_at ASC",
        (chat_id,)
    )
    return jsonify([
        {
            'sender': m['sender'],
            'content': m['content'],
            'time': m['created_at'].strftime('%I:%M %p') if m['created_at'] else '',
        }
        for m in messages
    ])


@main_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    """Process a user message and return bot response."""
    user_id = session['user_id']
    data = request.get_json()
    user_message = (data.get('message') or '').strip()
    chat_id = data.get('chat_id')

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    # Create chat if not provided
    if not chat_id:
        result = execute_db(
            "INSERT INTO chats (user_id, title) VALUES (%s, %s) RETURNING id",
            (user_id, user_message[:50]),
            returning=True
        )
        chat_id = str(result[0]['id']) if result else None
        if not chat_id:
            return jsonify({'error': 'Failed to create chat'}), 500
    else:
        # Update chat title if it's 'New Chat'
        chat = query_db("SELECT title FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id), one=True)
        if chat and chat['title'] == 'New Chat':
            execute_db("UPDATE chats SET title = %s WHERE id = %s", (user_message[:50], chat_id))

    # Save user message
    execute_db(
        "INSERT INTO messages (chat_id, user_id, sender, content) VALUES (%s, %s, 'user', %s)",
        (chat_id, user_id, user_message)
    )

    # Load last 6 messages as conversation history for AI context
    recent = query_db(
        "SELECT sender, content FROM messages WHERE chat_id = %s ORDER BY created_at DESC LIMIT 6",
        (chat_id,)
    ) or []
    chat_history = [
        {"role": "user" if m['sender'] == 'user' else "assistant", "content": m['content']}
        for m in reversed(recent)
    ]

    # Process with chatbot engine (AI + pattern fallback)
    result = chatbot.process(user_message, user_id=user_id, chat_history=chat_history)

    # Save bot response
    execute_db(
        "INSERT INTO messages (chat_id, user_id, sender, content, intent, confidence) VALUES (%s, %s, 'bot', %s, %s, %s)",
        (chat_id, user_id, result['response'], result['intent'], result['confidence'])
    )

    # Update chat timestamp
    execute_db("UPDATE chats SET updated_at = NOW() WHERE id = %s", (chat_id,))

    return jsonify({
        'response':         result['response'],
        'intent':           result['intent'],
        'confidence':       result['confidence'],
        'chat_id':          chat_id,
        'response_time_ms': result['response_time_ms'],
        'ai_provider':      result.get('ai_provider', 'pattern'),
    })


@main_bp.route('/api/chat/<chat_id>/delete', methods=['POST'])
@login_required
def delete_chat(chat_id):
    """Delete a chat session."""
    user_id = session['user_id']
    execute_db("DELETE FROM chats WHERE id = %s AND user_id = %s", (chat_id, user_id))
    return jsonify({'success': True})


@main_bp.route('/api/ai/status')
@login_required
def ai_status():
    """Check status of all 5 AI providers (available/blocked/no-key)."""
    from chatbot.ai_engine import provider_status
    return jsonify({'providers': provider_status()})
