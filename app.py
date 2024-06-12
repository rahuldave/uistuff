from flask import Flask, request, jsonify, g, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import random
from datetime import datetime
import os

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = os.urandom(24)  # Set a secret key for session management
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATABASE = 'chatbot.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    db = get_db()
    try:
        with db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        return jsonify({"status": "success"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "User already exists"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    db = get_db()
    user = db.execute("SELECT userid FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()

    if user:
        session['userid'] = user['userid']
        session['username'] = username
        return jsonify({"status": "success", "userid": user['userid']}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success"}), 200

@app.route('/api/session', methods=['GET'])
def get_session():
    if 'userid' in session:
        return jsonify({"loggedIn": True, "username": session['username']}), 200
    else:
        return jsonify({"loggedIn": False}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'userid' not in session:
        return redirect(url_for('serve_index'))

    data = request.json
    user_message = data['message']
    conversation_id = data['conversationId']
    user_id = session['userid']

    # Mock response with random Lorem Ipsum text
    lorem_ipsum_texts = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt."
    ]
    response_message = random.choice(lorem_ipsum_texts)

    db = get_db()
    with db:
        db.execute("INSERT INTO chats (conversation_id, user_id, model_id, chat, feedback, time) VALUES (?, ?, ?, ?, ?, ?)",
                   (conversation_id, 1, 1, response_message, None, datetime.now()))  # Assuming user_id 1 is the bot
        chat_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    return jsonify({"response": response_message, "id": chat_id})

@app.route('/api/feedback', methods=['POST'])
def feedback():
    if 'userid' not in session:
        return redirect(url_for('serve_index'))

    data = request.json
    chat_id = data['messageId']
    feedback = data['feedback']

    db = get_db()
    with db:
        db.execute("UPDATE chats SET feedback = ? WHERE chat_id = ?", (feedback, chat_id))

    return jsonify({"status": "success"})

@app.route('/api/feedback/<int:chat_id>', methods=['GET'])
def get_feedback(chat_id):
    db = get_db()
    feedback = db.execute("SELECT feedback FROM chats WHERE chat_id = ?", (chat_id,)).fetchone()
    if feedback:
        return jsonify({"feedback": feedback['feedback']}), 200
    else:
        return jsonify({"feedback": None}), 200

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    if 'userid' not in session:
        return redirect(url_for('serve_index'))

    data = request.json
    title = data['title']
    user_id = session['userid']

    db = get_db()
    with db:
        db.execute("INSERT INTO conversations (title, user_id) VALUES (?, ?)", (title, user_id))
        conversation_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    return jsonify({"id": conversation_id, "title": title})

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    if 'userid' not in session:
        return redirect(url_for('serve_index'))

    user_id = session['userid']
    db = get_db()
    conversations = db.execute("SELECT conversationid, title FROM conversations WHERE user_id = ?", (user_id,)).fetchall()
    return jsonify({"conversations": [{"id": row["conversationid"], "title": row["title"]} for row in conversations]})

@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
def get_chats(conversation_id):
    if 'userid' not in session:
        return redirect(url_for('serve_index'))

    db = get_db()
    chats = db.execute("SELECT chat_id, chat, user_id, feedback, time FROM chats WHERE conversation_id = ?", (conversation_id,)).fetchall()
    return jsonify({"chats": [{"id": row["chat_id"], "text": row["chat"], "user_id": row["user_id"], "feedback": row["feedback"], "time": row["time"]} for row in chats]})

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
