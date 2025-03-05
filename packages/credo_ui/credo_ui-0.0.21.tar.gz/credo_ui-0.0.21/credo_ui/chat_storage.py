import sqlite3
import uuid
import json
from datetime import datetime
import os


class ChatStorage:
    def __init__(self, db_path="chats.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the SQLite database with necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create chats table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')

        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
        ''')

        conn.commit()
        conn.close()

    def create_chat(self, title="Current Chat"):
        """Create a new chat and return its ID"""
        chat_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO chats (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (chat_id, title, now, now)
        )

        conn.commit()
        conn.close()

        return chat_id

    def add_message(self, chat_id, role, content):
        """Add a message to a chat"""
        message_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update the chat's updated_at timestamp
        cursor.execute(
            "UPDATE chats SET updated_at = ? WHERE id = ?",
            (now, chat_id)
        )

        # Insert the new message
        cursor.execute(
            "INSERT INTO messages (id, chat_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (message_id, chat_id, role, content, now)
        )

        conn.commit()
        conn.close()

        return message_id

    def get_chat(self, chat_id):
        """Get chat metadata by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
        chat = cursor.fetchone()

        conn.close()

        if chat:
            return dict(chat)
        return None

    def get_messages(self, chat_id):
        """Get all messages for a chat"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp", (chat_id,))
        messages = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return messages

    def get_all_chats(self):
        """Get all chats, ordered by most recently updated"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM chats ORDER BY updated_at DESC")
        chats = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return chats

    def update_chat_title(self, chat_id, title):
        """Update a chat's title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE chats SET title = ? WHERE id = ?",
            (title, chat_id)
        )

        conn.commit()
        conn.close()

    def delete_chat(self, chat_id):
        """Delete a chat and all its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete all messages in the chat
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))

        # Delete the chat itself
        cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))

        conn.commit()
        conn.close()

