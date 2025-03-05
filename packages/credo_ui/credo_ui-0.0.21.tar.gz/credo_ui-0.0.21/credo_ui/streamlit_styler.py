import streamlit as st


class StreamlitStyler:
    """
    A framework for styling Streamlit elements using Python parameters
    instead of directly writing CSS.
    """

    def __init__(self):
        """Initialize the styler with default styles applied to the page."""
        self.applied_styles = set()

    def apply_global_styles(self,
                            font_family=None,
                            background_color=None,
                            text_color=None,
                            padding=None):
        """Apply global styles to the entire Streamlit app."""
        css = []

        if font_family:
            css.append(f"* {{font-family: {font_family} !important;}}")

        if background_color:
            css.append(f"body {{background-color: {background_color} !important;}}")

        if text_color:
            css.append(f".stMarkdown, .stText, p, h1, h2, h3 {{color: {text_color} !important;}}")

        if padding:
            css.append(f".element-container {{padding: {padding} !important;}}")

        if css:
            style_tag = f"""
            <style>
                {" ".join(css)}
            </style>
            """
            st.markdown(style_tag, unsafe_allow_html=True)
            self.applied_styles.add('global')

        return self

    def style_button(self,
                     border=None,
                     background_color=None,
                     text_color=None,
                     hover_color=None,
                     border_radius=None,
                     shadow=None,
                     padding=None):
        """Style all buttons in the app."""
        css = []

        if border is False:
            css.append("border: none !important; box-shadow: none !important;")
        elif border:
            css.append(f"border: {border} !important;")

        if background_color:
            css.append(f"background-color: {background_color} !important;")

        if text_color:
            css.append(f"color: {text_color} !important;")

        if border_radius is not None:
            css.append(f"border-radius: {border_radius}px !important;")

        if shadow is False:
            css.append("box-shadow: none !important;")
        elif shadow:
            css.append(f"box-shadow: {shadow} !important;")

        if padding:
            css.append(f"padding: {padding} !important;")

        if css:
            style_tag = f"""
            <style>
                .stButton button {{ {" ".join(css)} }}

                {f".stButton button:hover {{background-color: {hover_color} !important;}}" if hover_color else ""}
            </style>
            """
            st.markdown(style_tag, unsafe_allow_html=True)
            self.applied_styles.add('button')

        return self

    def style_sidebar(self,
                      background_color=None,
                      text_color=None,
                      width=None,
                      padding=None):
        """Style the sidebar."""
        css = []

        if background_color:
            css.append(f"background-color: {background_color} !important;")

        if text_color:
            css.append(f"color: {text_color} !important;")

        if width:
            css.append(f"width: {width} !important; max-width: {width} !important;")

        if padding:
            css.append(f"padding: {padding} !important;")

        if css:
            style_tag = f"""
            <style>
                [data-testid="stSidebar"] > div:first-child {{ {" ".join(css)} }}
            </style>
            """
            st.markdown(style_tag, unsafe_allow_html=True)
            self.applied_styles.add('sidebar')

        return self

    def style_input(self,
                    border=None,
                    background_color=None,
                    text_color=None,
                    border_radius=None,
                    padding=None):
        """Style input elements (text_input, number_input, etc.)."""
        css = []

        if border is False:
            css.append("border: none !important;")
        elif border:
            css.append(f"border: {border} !important;")

        if background_color:
            css.append(f"background-color: {background_color} !important;")

        if text_color:
            css.append(f"color: {text_color} !important;")

        if border_radius is not None:
            css.append(f"border-radius: {border_radius}px !important;")

        if padding:
            css.append(f"padding: {padding} !important;")

        if css:
            style_tag = f"""
            <style>
                .stTextInput input, .stNumberInput input, textarea {{ {" ".join(css)} }}
            </style>
            """
            st.markdown(style_tag, unsafe_allow_html=True)
            self.applied_styles.add('input')

        return self

    def style_card(self,
                   border=None,
                   background_color=None,
                   text_color=None,
                   border_radius=None,
                   shadow=None,
                   padding=None):
        """
        Style a container to look like a card.
        Note: This must be applied before creating the container.
        """
        css = []

        if border is False:
            css.append("border: none !important;")
        elif border:
            css.append(f"border: {border} !important;")

        if background_color:
            css.append(f"background-color: {background_color} !important;")

        if text_color:
            css.append(f"color: {text_color} !important;")

        if border_radius is not None:
            css.append(f"border-radius: {border_radius}px !important;")

        if shadow is False:
            css.append("box-shadow: none !important;")
        elif shadow:
            css.append(f"box-shadow: {shadow} !important;")
        else:
            # Default nice shadow if shadow=True
            css.append("box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px !important;")

        if padding:
            css.append(f"padding: {padding} !important;")
        else:
            css.append("padding: 1rem !important;")

        if css:
            style_tag = f"""
            <style>
                div[data-testid="stContainer"] {{ {" ".join(css)} }}
            </style>
            """
            st.markdown(style_tag, unsafe_allow_html=True)
            self.applied_styles.add('card')

        return self

    def style_tabs(self,
                   background_color=None,
                   active_tab_color=None,
                   text_color=None,
                   active_text_color=None,
                   border_radius=None):
        """Style the tabs widget."""
        css = []
        active_css = []

        if background_color:
            css.append(f"background-color: {background_color} !important;")

        if text_color:
            css.append(f"color: {text_color} !important;")

        if active_tab_color:
            active_css.append(f"background-color: {active_tab_color} !important;")

        if active_text_color:
            active_css.append(f"color: {active_text_color} !important;")

        if border_radius is not None:
            css.append(f"border-radius: {border_radius}px !important;")

        if css or active_css:
            style_tag = f"""
            <style>
                button[role="tab"] {{ {" ".join(css)} }}
                button[role="tab"][aria-selected="true"] {{ {" ".join(active_css)} }}
            </style>
            """
            st.markdown(style_tag, unsafe_allow_html=True)
            self.applied_styles.add('tabs')

        return self

    def style_metric(self,
                     background_color=None,
                     label_color=None,
                     value_color=None,
                     border=None,
                     border_radius=None,
                     shadow=None,
                     padding=None):
        """Style metric elements."""
        css = []
        label_css = []
        value_css = []

        if background_color:
            css.append(f"background-color: {background_color} !important;")

        if border is False:
            css.append("border: none !important;")
        elif border:
            css.append(f"border: {border} !important;")

        if border_radius is not None:
            css.append(f"border-radius: {border_radius}px !important;")

        if shadow is False:
            css.append("box-shadow: none !important;")
        elif shadow:
            css.append(f"box-shadow: {shadow} !important;")

        if padding:
            css.append(f"padding: {padding} !important;")

        if label_color:
            label_css.append(f"color: {label_color} !important;")

        if value_color:
            value_css.append(f"color: {value_color} !important;")

        if css or label_css or value_css:
            style_tag = f"""
            <style>
                [data-testid="stMetric"] {{ {" ".join(css)} }}
                [data-testid="stMetricLabel"] {{ {" ".join(label_css)} }}
                [data-testid="stMetricValue"] {{ {" ".join(value_css)} }}
            </style>
            """
            st.markdown(style_tag, unsafe_allow_html=True)
            self.applied_styles.add('metric')

        return self

    def apply_theme(self, theme="light"):
        """Apply a predefined theme to the app."""
        if theme == "light":
            return self.apply_global_styles(
                font_family='"Segoe UI", Roboto, sans-serif',
                background_color="#f8f9fa"
            ).style_button(
                border=False,
                background_color="#0066cc",
                text_color="white",
                hover_color="#0055a5",
                border_radius=8
            ).style_sidebar(
                background_color="white",
                padding="2rem 1rem"
            ).style_card(
                border=False,
                background_color="white",
                shadow=True,
                border_radius=8
            )

        elif theme == "dark":
            return self.apply_global_styles(
                font_family='"Segoe UI", Roboto, sans-serif',
                background_color="#121212",
                text_color="#e0e0e0"
            ).style_button(
                border=False,
                background_color="#bb86fc",
                text_color="#121212",
                hover_color="#9d70d8",
                border_radius=8
            ).style_sidebar(
                background_color="#1e1e1e",
                padding="2rem 1rem"
            ).style_input(
                background_color="#333333",
                text_color="#e0e0e0",
                border=False,
                border_radius=8
            ).style_card(
                border=False,
                background_color="#1e1e1e",
                text_color="#e0e0e0",
                shadow=True,
                border_radius=8
            )

        elif theme == "minimal":
            return self.apply_global_styles(
                font_family='"Segoe UI", Roboto, sans-serif',
                background_color="white"
            ).style_button(
                border="1px solid #ced4da",
                background_color="white",
                text_color="#212529",
                hover_color="#f8f9fa",
                border_radius=4
            ).style_sidebar(
                padding="2rem 1rem"
            ).style_card(
                border="1px solid #ced4da",
                shadow=False,
                border_radius=4
            )

        return self


# Example usage
def create_styled_button(label="", icon=None, key=None, border=False):
    """Create a styled button with no border"""
    # Apply the style
    styler = StreamlitStyler()
    styler.style_button(border=border)

    # Create the button
    return st.button(label=label, icon=icon, key=key)


# Create a container with card-like styling
def create_card(content_function=None):
    """
    Create a container styled as a card.
    Pass a function that will be executed within the card context.
    """
    styler = StreamlitStyler()
    styler.style_card(shadow=True, background_color="white", border_radius=10)

    with st.container():
        if content_function:
            content_function()