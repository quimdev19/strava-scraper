import requests
from http.cookiejar import MozillaCookieJar

def load_cookies_from_file(session: requests.Session, filepath: str) -> bool:
    """Load cookies from a file into a requests Session.

    Args:
        session (requests.Session): The requests Session object to update with loaded cookies.
        filepath (str): The path to the file containing the cookies.

    Returns:
        bool: True if the cookies were successfully loaded from an existing file, False otherwise.
    """

    cookies = MozillaCookieJar(filepath)
    try:
        cookies.load(ignore_discard=True)
        session.cookies = cookies
        return True
    except OSError as e:
        print(f"Error when trying to load cookies: {e}")
        return False

def login() -> None:
    pass
