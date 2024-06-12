import sqlite3

DATABASE = 'chatbot.db'

def init_db():
    with sqlite3.connect(DATABASE) as db:
        c = db.cursor()
        c.execute("DROP TABLE IF EXISTS users;")
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        c.execute("DROP TABLE IF EXISTS models;")
        c.execute('''
        CREATE TABLE IF NOT EXISTS models (
            modelid INTEGER PRIMARY KEY,
            modelname TEXT NOT NULL UNIQUE
        )
        ''')
        c.execute("DROP TABLE IF EXISTS chats;")
        c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            conversation_id INTEGER,
            user_id INTEGER,
            model_id INTEGER,
            chat TEXT,
            feedback TEXT,
            time DATETIME,
            FOREIGN KEY(conversation_id) REFERENCES conversations(conversationid),
            FOREIGN KEY(user_id) REFERENCES users(userid),
            FOREIGN KEY(model_id) REFERENCES models(modelid)
        )
        ''')
        c.execute("DROP TABLE IF EXISTS conversations;")
        c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            conversationid INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(userid)
        )
        ''')
        c.execute("INSERT INTO models (modelname) VALUES ('text-davinci-003')")
        db.commit()

if __name__ == '__main__':
    init_db()
