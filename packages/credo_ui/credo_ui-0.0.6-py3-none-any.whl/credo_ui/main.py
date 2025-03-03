def main():
    import streamlit.web.cli
    import sys
    sys.argv = ["streamlit", "run", "credo_ui/app.py"]
    streamlit.web.cli.main()

if __name__ == '__main__':
    main()