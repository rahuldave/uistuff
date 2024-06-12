import sqlite3
from datetime import datetime

DATABASE = 'chatbot.db'

def populate_db():
    with sqlite3.connect(DATABASE) as db:
        c = db.cursor()
        c.execute("DELETE FROM users")
        c.execute("DELETE FROM conversations")
        c.execute("DELETE FROM chats")

        c.execute("INSERT INTO users (userid, username, password) VALUES (?, ?, ?)", (1, "bot", "password"))
        bot_id = 1
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("testuser", "password"))
        user_id = c.lastrowid

        c.execute("INSERT INTO conversations (title, user_id) VALUES (?, ?)", ("Sample Conversation", user_id))
        conversation_id = c.lastrowid
        chats = [
            (conversation_id, user_id, 1, "Can you tell me about your services?", None, datetime.now()),
            (conversation_id, bot_id, 1, "Sure! We offer a range of AI-based solutions.", None, datetime.now()),
            (conversation_id, user_id, 1, "What kind of AI solutions do you provide?", None, datetime.now()),
            (conversation_id, bot_id, 1, "We provide natural language processing, computer vision, and more.", None, datetime.now())
        ]
        c.executemany("INSERT INTO chats (conversation_id, user_id, model_id, chat, feedback, time) VALUES (?, ?, ?, ?, ?, ?)", chats)
        db.commit()

if __name__ == '__main__':
    populate_db()
