import os
import pickle
from typing import Any
import appdirs

def get_token_file_path() -> str:
    """
    Determines where to save & load token.
    """
    app_dirs = appdirs.AppDirs("benchify", "benchify")
    token_file = "token.pickle"
    token_file_path = os.path.join(app_dirs.user_data_dir, token_file)
    return token_file_path


def save_token(token: str) -> bool:
    """
    Saves the token_data to get_token_file_path().
    """
    try:
        token_file_path = get_token_file_path()
        os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
        with open(token_file_path, "wb") as f:
            pickle.dump(token, f)
    #pylint:disable=broad-exception-caught
    except Exception:
        print("Failed to save the authentication token.")
        exit(1)
    return True


def load_token() -> str:
    """
    Loads the token_data from get_token_file_path().
    """
    token_file_path = get_token_file_path()
    if os.path.exists(token_file_path):
        with open(token_file_path, "rb") as f:
            return pickle.load(f)
    return None