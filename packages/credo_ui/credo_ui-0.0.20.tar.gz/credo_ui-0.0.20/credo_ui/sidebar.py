from .chat_manager import ChatManager

class Sidebar:
    def __init__(self, st):
        self.st = st  # Keep reference to streamlit
        self.sidebar = st.sidebar

        # Initialize chat manager if not already in session state
        if 'chat_manager' not in st.session_state:
            st.session_state.chat_manager = ChatManager()

        self.chat_manager = st.session_state.chat_manager




    def render_sidebar_info(self) -> None:
        """Render the complete sidebar with API config and chat history"""
        ## add settings icon like character not material
        self.sidebar.title(" Settings")
        # self.sidebar.caption("Configure your API settings here.")
        self.setup_api_and_details()


        # Render chat list
        self.render_chat_list()



    def render_chat_list(self):
        """Render the list of previous chats"""
        chats = self.chat_manager.get_all_chats()

        if not chats:
            self.sidebar.caption("No previous chats")
            return

        current_chat_id = self.st.session_state.get('current_chat_id')

        for chat in chats:
            # Create a row for each chat with the title and a delete button
            col1, col2 = self.sidebar.columns([0.8, 0.2],gap='small')

            # Highlight the current chat
            title = chat['title'] or "Untitled Chat"
            if chat['id'] == current_chat_id:
                title = f"🔹{title}"

            # Chat selection button styled as a link
            if col1.button(title, key=f"chat_{chat['id']}", use_container_width=True):
                self.chat_manager.switch_chat(self.st.session_state, chat['id'])
                # Force a rerun to refresh the UI
                self.st.rerun()

            # Delete button
            if col2.button(icon=":material/delete:", label="",key=f"delete_{chat['id']}", use_container_width=True):
                self.chat_manager.delete_chat(self.st.session_state, chat['id'])
                # Force a rerun to refresh the sidebar
                self.st.rerun()

    def setup_api_and_details(self):
        """Render sidebar with model settings and info"""
        # Get current session state
        session = self.st.session_state

        model_name_input = self.sidebar.text_input(
            label="Model Name",
            value=session.get("model_name", "hf.co/bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF:Q5_K_M"),
            placeholder = "Model Name",
            key="model_name",
            label_visibility="hidden"
        )

        api_key_input = self.sidebar.text_input(
            label="API Key",
            value=session.get("api_key", "dsollama"),
            type="password",
            key="api_key",
            label_visibility="hidden",
            placeholder="API Key",
        )

        base_url_input = self.sidebar.text_input(
            label="Base URL",
            value=session.get("base_url", "http://localhost:11434/v1"),
            key="base_url",
            label_visibility="hidden",
            placeholder="Base URL",
        )

        # Save inputs to session state
        if 'model_name' not in session:
            session["model_name"] = model_name_input
        if 'api_key' not in session:
            session["api_key"] = api_key_input
        if 'base_url' not in session:
            session["base_url"] = base_url_input