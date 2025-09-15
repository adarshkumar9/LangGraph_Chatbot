import sqlite3
import uuid
from datetime import datetime

CHAT_DB = "chat_history.db"

def setup_db():
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        thread_id TEXT,
        created_at TEXT,
        status TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
        session_id TEXT,
        message_type TEXT,
        content TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS evaluations (
        session_id TEXT,
        question_num INTEGER,
        score INTEGER,
        feedback TEXT
    )''')
    conn.commit()
    conn.close()

def save_message(session_id, msg):
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history VALUES (?,?,?,?)", (
        session_id,
        type(msg).__name__,
        getattr(msg, "content", str(msg)),
        datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_evaluation(session_id, question_num, score, feedback):
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute("INSERT INTO evaluations VALUES (?,?,?,?)", 
              (session_id, question_num, score, feedback))
    conn.commit()
    conn.close()

def create_session(thread_id):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute("INSERT INTO sessions VALUES (?,?,?,?)", (
        session_id, thread_id, datetime.now().isoformat(), "active"))
    conn.commit()
    conn.close()
    return session_id

def close_session(session_id):
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute("UPDATE sessions SET status='closed' WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()
