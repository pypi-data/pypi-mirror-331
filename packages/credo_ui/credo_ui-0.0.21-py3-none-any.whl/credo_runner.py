import os


def main():
    import streamlit.web.cli
    import sys
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    ocr_app_path = os.path.join(cur_dir, "credo_runner_main.py")
    sys.argv = ["streamlit", "run", ocr_app_path]
    # sys.argv = ["python","-m","streamlit","run","credo_runner_main.py"]
    streamlit.web.cli.main()

if __name__ == '__main__':
    main()