# /home/ntlpt59/MAIN/Packages/credo_ui/credo_ui/app.py
import asyncio
import streamlit as st
import streamlit_shadcn_ui as ui
from litegen import LLM, LLMSearch

from credo_ui.utils import async_stream_processor, sync_stream_processor, setup_api_and_details
from credo_ui.ui import render_titles
from credo_ui.sidebar import Sidebar
from credo_ui.utils import setup_chat_session, process_and_store_message, render_chat_history

def app():
    # Check if form was submitted in previous run and clear the text area
    if 'submitted' in st.session_state and st.session_state.submitted:
        st.session_state.textarea1 = ""
        st.session_state.submitted = False


    if 'textarea1' not in st.session_state:
        st.session_state.textarea1 = ""

    sidebar = Sidebar(st)
    chat_manager = setup_chat_session(st)


    render_titles(st)
    sidebar.render_sidebar_info()

    setup_api_and_details(st)


    llm = LLM()
    search = LLMSearch(llm=llm,enable_think_tag=True,search_parallel=False)

    history_area = st.container(height=440, border=False)

    render_chat_history(st, history_area)

    textcols = st.columns([0.8, 0.2])


    textarea_value = ui.textarea(
        # default_value="tell me a joke",
        placeholder="Type your message here...",
        key="textarea1")

    cols = st.columns([1.5,1.5,1.5, 1,1], gap="small")
    # cols = st.columns([1,1,1,1,1], gap="small")

    with cols[0]:
        use_deep_search = ui.switch(key='c1', label="DeepSearch")

    with cols[1]:
        use_search = ui.switch(key='c2', label="Search")

    with cols[2]:
        use_deep_research = ui.switch(key='c3', label="DeepResearch")


    with cols[3]:
        is_submit = ui.button('Submit', key='submit_button')

    with cols[4]:
        if ui.button('New Chat', key='new_chat_button'):
            chat_manager.create_new_chat(st.session_state)
            st.rerun()



    if is_submit:
        response_text=""
        with history_area:
            expander_title = "Synthesizing..." if use_deep_search else "Thinking..."
            thinking_expander = st.expander(expander_title, expanded=False,icon=":material/psychology:")
            thinking_placeholder = thinking_expander.empty()
            regular_placeholder = st.empty()

            if use_deep_search:
                # We need to run the async function
                async def run_async_search():
                    await async_stream_processor(
                        search(textarea_value),
                        thinking_placeholder,
                        regular_placeholder,
                        response_text
                    )


                # Use asyncio_runner to run the async function
                import nest_asyncio

                nest_asyncio.apply()

                # Create a new event loop and run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_text=loop.run_until_complete(run_async_search())
            else:
                # Use the sync processor for regular LLM streaming
                final_text=sync_stream_processor(
                    llm.completion(textarea_value, stream=True),
                    thinking_placeholder,
                    regular_placeholder,
                    response_text
                )

            process_and_store_message(st, textarea_value, final_text)


if __name__ == '__main__':
    app()