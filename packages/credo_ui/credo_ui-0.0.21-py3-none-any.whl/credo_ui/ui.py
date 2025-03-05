
def render_titles(st):
    st.set_page_config(layout="wide",initial_sidebar_state='collapsed')

    st.markdown("""
        <style>
        .block-container {
            padding-top: 0;
        }
        header {
            visibility: hidden;
        }
        .stApp > header {
            display: none;
        }
        .custom-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            # padding: 0.5rem 1rem;
            margin-top: -0.8rem;  /* Move it up to align with Stop/Deploy */
        }
        .title-area {
            font-size: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            width: 250px !important;
            background-color: white;  
            border-right: 1px solid #e0e0e0;
        }
    
        [data-testid="stSidebar"] h1 {
            font-size: 1.2rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
    
        }
        </style>
    """, unsafe_allow_html=True)


    # Replace the regular title with custom header
    st.markdown('<div class="custom-header"><div class="title-area">Credo</div><div></div></div>',
                unsafe_allow_html=True)


    custom_css = """
    <style>
        /* Remove button borders and background in the sidebar */
        .stSidebar button {
            border: none !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }

        /* Hover effect for better UX */
        .stSidebar button:hover {
            background-color: rgba(0, 0, 0, 0.05) !important;
        }

        /* Style for the currently selected chat */
        .stSidebar button.selected-chat {
            font-weight: bold;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
