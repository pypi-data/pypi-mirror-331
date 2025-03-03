# Credo UI

A Streamlit-based UI for conversational AI with integrated search capabilities.

## Features

- Chat interface with streaming responses
- Multiple search modes:
  - Regular search
  - Deep search
  - Deep research
- Sidebar for additional information and settings
- Session management for chat history
- Built on top of Streamlit and streamlit-shadcn-ui



## Installation

```python
pip install credo-ui
```

## Usage

Run the application:

```
credo_ui
```

## Screenshots


![Search Results](resources/Screenshot%20from%202025-03-03%2007-32-08.png)
*Chat interface with search capabilities*

![Chat Interface](resources/Screenshot%20from%202025-03-03%2007-32-00.png)



## Components

- **Chat Interface**: A clean, responsive UI for interacting with LLMs
- **Search Integration**: Connect to various search backends through the LLMSearch class
- **Customizable Sidebar**: Add additional controls and information
- **Expandable "Thinking" Section**: Shows intermediate processing steps

## Project Structure

```
credo_ui/
├── ui.py             # Main UI components
├── sidebar.py        # Sidebar implementation
├── utils.py          # Helper functions
resources/
├── ui_image1.png     # UI screenshot for chat interface
├── ui_image2.png     # UI screenshot for search results
```

## Example

```python
import streamlit as st
from credo_ui.utils import setup_chat_session
from credo_ui.ui import render_titles
from credo_ui.sidebar import Sidebar

# Initialize
sidebar = Sidebar(st)
chat_manager = setup_chat_session(st)

# Render UI components
render_titles(st)
sidebar.render_sidebar_info()

# ... rest of your application
```

## Configuration

Switch between different search modes using the toggle buttons:
- **DeepSearch**: Enhanced search capabilities
- **Search**: Basic search functionality
- **DeepResearch**: In-depth research capabilities with thinking steps

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.