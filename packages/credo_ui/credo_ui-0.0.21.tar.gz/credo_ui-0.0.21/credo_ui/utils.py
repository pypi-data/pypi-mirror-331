import os

from .chat_manager import ChatManager

def process_chunk(text, thinking_content, regular_content, in_thinking_section, pending_text):
    """Process a single chunk of text and update the state."""
    pending_text += text

    # Check for <think> tag start
    if "<think>" in pending_text and not in_thinking_section:
        parts = pending_text.split("<think>", 1)
        regular_content += parts[0]
        pending_text = "<think>" + parts[1]
        in_thinking_section = True

    # Check for </think> tag end
    if "</think>" in pending_text and in_thinking_section:
        parts = pending_text.split("</think>", 1)
        thinking_content += parts[0].replace("<think>", "", 1)+"\n"
        pending_text = parts[1]
        in_thinking_section = False

    # If not in thinking section and no tags, just add to regular
    if not in_thinking_section and "<think>" not in pending_text:
        regular_content += pending_text
        pending_text = ""

    # If in thinking section but no closing tag yet, keep in thinking
    elif in_thinking_section and "</think>" not in pending_text:
        thinking_content += pending_text+"\n"
        pending_text = ""

    return thinking_content, regular_content, in_thinking_section, pending_text


def sync_stream_processor(response_stream, thinking_placeholder, regular_placeholder, response_text=""):
    """Process regular synchronous stream."""
    thinking_content = ""
    regular_content = ""
    in_thinking_section = False
    pending_text = ""
    current_thinking = ""
    current_regular = ""
    full_response = ""  # Track the complete response

    for chunk in response_stream:
        if chunk:
            text = chunk.choices[0].delta.content if hasattr(chunk, "choices") else chunk

            thinking_content, regular_content, in_thinking_section, pending_text = process_chunk(
                text, thinking_content, regular_content, in_thinking_section, pending_text
            )

            # Update UI when content changes
            if thinking_content != current_thinking:
                thinking_content = thinking_content.replace("<think>", "")
                thinking_placeholder.markdown(thinking_content+"\n")
                current_thinking = thinking_content

            if regular_content != current_regular:
                # Only update the displayed portion, not the accumulated response
                new_content = regular_content[len(current_regular):]
                full_response += new_content  # Add the new content to our full response
                regular_placeholder.markdown(regular_content)
                current_regular = regular_content

    # Return the full response text
    return full_response


async def async_stream_processor(response_stream, thinking_placeholder, regular_placeholder, response_text=""):
    """Process async stream."""
    thinking_content = ""
    regular_content = ""
    in_thinking_section = False
    pending_text = ""
    current_thinking = ""
    current_regular = ""
    full_response = ""  # Track the complete response

    async for v in response_stream:
        text = v.content if hasattr(v, "content") else str(v)

        thinking_content, regular_content, in_thinking_section, pending_text = process_chunk(
            text, thinking_content, regular_content, in_thinking_section, pending_text
        )

        # Update UI when content changes
        if thinking_content != current_thinking:
            thinking_content = thinking_content.replace("<think>", "")
            thinking_placeholder.markdown(thinking_content+"\n")
            current_thinking = thinking_content

        if regular_content != current_regular:
            # Only update the displayed portion, not the accumulated response
            new_content = regular_content[len(current_regular):]
            full_response += new_content  # Add the new content to our full response
            regular_placeholder.markdown(regular_content)
            current_regular = regular_content

    # Return the full response text
    return full_response

def setup_api_and_details(st):
    model_name = st.session_state.get("model_name")
    api_key = st.session_state.get("api_key")
    base_url = st.session_state.get("base_url")

    if not api_key or not base_url:
        st.warning("Please provide API Key and Base URL in the sidebar.")
        st.stop()

    os.environ['OPENAI_API_KEY'] = str(api_key)
    os.environ['OPENAI_BASE_URL'] = base_url
    os.environ['OPENAI_MODEL_NAME'] = model_name


def setup_chat_session(st):
    """Initialize or retrieve current chat session"""
    # This prevents circular imports
    # Initialize chat manager if needed
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = ChatManager()

    # Initialize or get current chat
    chat_manager = st.session_state.chat_manager
    current_chat_id, messages = chat_manager.init_session(st.session_state)

    return chat_manager


def process_and_store_message(st, user_input, ai_response):
    """Store the user input and AI response in the current chat"""
    chat_manager = st.session_state.chat_manager

    # Add the user message
    chat_manager.add_message_to_current(st.session_state, "user", user_input)

    # Add the AI response
    chat_manager.add_message_to_current(st.session_state, "assistant", ai_response)


def render_chat_history(st, container):
    """Render the current chat history in the provided container"""
    if 'chat_messages' not in st.session_state:
        return

    messages = st.session_state.chat_messages

    # Clear the container first
    container.empty()

# Render each message
    for msg in messages:
        if msg['role'] == 'user':
            container.markdown(f"**{msg['content']}**")
        else:
            container.markdown(f"{msg['content']}")

        # Add a subtle divider between message pairs
        if msg['role'] == 'user':
            container.markdown("---")

