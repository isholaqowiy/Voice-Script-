import sqlite3
import os

DB_NAME = "voicescript.db"

def init_db():
    """Initializes the SQLite database and creates the user settings table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'English',
            voice TEXT DEFAULT 'alloy'
        )
    ''')
    conn.commit()
    conn.close()

def get_user_settings(user_id):
    """Fetches user settings or creates default ones if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT language, voice FROM user_settings WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row:
        conn.close()
        return {"language": row[0], "voice": row[1]}
    else:
        # Create defaults
        cursor.execute("INSERT INTO user_settings (user_id, language, voice) VALUES (?, 'English', 'alloy')", (user_id,))
        conn.commit()
        conn.close()
        return {"language": "English", "voice": "alloy"}

def update_user_language(user_id, language):
    """Updates the user's preferred language."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    get_user_settings(user_id)
    cursor.execute("UPDATE user_settings SET language = ? WHERE user_id = ?", (language, user_id))
    conn.commit()
    conn.close()

def update_user_voice(user_id, voice):
    """Updates the user's preferred voice model."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    get_user_settings(user_id)
    cursor.execute("UPDATE user_settings SET voice = ? WHERE user_id = ?", (voice, user_id))
    conn.commit()
    conn.close()

