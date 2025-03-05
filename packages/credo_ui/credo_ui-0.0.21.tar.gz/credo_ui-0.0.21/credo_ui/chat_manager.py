from datetime import datetime

from .chat_storage import ChatStorage

class ChatManager:
    def __init__(self, storage=None):
        """Initialize with storage backend"""
        self.storage = storage if storage else ChatStorage()

    def init_session(self, st_session):
        """Initialize or retrieve current chat from session state"""
        if 'current_chat_id' not in st_session:
            # Create a new chat
            chat_id = self.storage.create_chat()
            st_session['current_chat_id'] = chat_id
            st_session['chat_messages'] = []

        return st_session['current_chat_id'], st_session['chat_messages']

    def switch_chat(self, st_session, chat_id):
        """Switch to a different chat"""
        st_session['current_chat_id'] = chat_id
        st_session['chat_messages'] = self.get_chat_messages(chat_id)

    def create_new_chat(self, st_session):
        """Create a new chat and switch to it"""
        chat_id = self.storage.create_chat()
        st_session['current_chat_id'] = chat_id
        st_session['chat_messages'] = []
        return chat_id

    def add_message_to_current(self, st_session, role, content):
        """Add a message to the current chat"""
        chat_id = st_session['current_chat_id']

        # Add to database
        self.storage.add_message(chat_id, role, content)

        # Update session state
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        st_session['chat_messages'].append(message)

        # If this is the first user message, use it to update the chat title
        if role == "user":
            messages = self.storage.get_messages(chat_id)
            if len(messages) <= 2:  # Only the first exchange
                # Use first ~30 chars of user message as chat title
                title = content[:30] + "..." if len(content) > 30 else content
                self.storage.update_chat_title(chat_id, title)

    def get_chat_messages(self, chat_id):
        """Get all messages for a chat in a format suitable for the UI"""
        db_messages = self.storage.get_messages(chat_id)

        # Convert to the format expected by the UI
        messages = []
        for msg in db_messages:
            messages.append({
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': msg['timestamp']
            })

        return messages

    def get_all_chats(self):
        """Get all chats for display in sidebar"""
        return self.storage.get_all_chats()

    def delete_chat(self, st_session, chat_id):
        """Delete a chat"""
        self.storage.delete_chat(chat_id)

        # If the deleted chat was the current one, create a new chat
        if st_session.get('current_chat_id') == chat_id:
            self.create_new_chat(st_session)