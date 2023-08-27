import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def get_template_dir() -> str:
    return f"{APP_DIR}/template"


def get_static_dir() -> str:
    return f"{APP_DIR}/static"
