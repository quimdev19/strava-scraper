import requests
from http.cookiejar import MozillaCookieJar
from bs4 import BeautifulSoup
from bs4 import Tag
from errors import CsrfTokenNotFoundError
from models.user import User

def load_cookies(session: requests.Session, filepath: str, load_from_file: bool) -> bool:
    """Load cookies from a file into a requests Session.

    Args:
        session (requests.Session): The requests Session object to update with loaded cookies.
        filepath (str): The path to the file containing the cookies.

    Returns:
        bool: True if the cookies were successfully loaded from an existing file, False otherwise.
    """

    status = True
    cookies = MozillaCookieJar(filepath)

    if load_from_file:
        try:
            cookies.load(ignore_discard=True)
        except OSError as e:
            print(f"Error when trying to load cookies: {e}")
            status = False

    session.cookies = cookies
    return status

def login() -> None:
    pass

def make_request(session: requests.Session, url: str, method: str, **kwargs) -> requests.Response:
    return session.request(method, url, **kwargs)

def post_request(session: requests.Session, url: str, **kwargs) -> requests.Response:
    return make_request(session, url, 'POST', **kwargs)

def get_request(session: requests.Session, url: str, **kwargs) -> requests.Response:
    return make_request(session, url, 'GET', **kwargs)

def load_csrf_token(soup: BeautifulSoup) -> str:
    csrf_token = soup.select('meta[name="csrf-token"]')
    if not csrf_token:
        raise CsrfTokenNotFoundError
    return csrf_token[0].get('content')

def load_user_profile_data(user_id: int, element: Tag) -> User:

    name = element.find("h1",{"class":"athlete-name"})
    if name is not None:
        name = name.get_text(strip=True)
    
    location = element.find("div",{"class":"location"})
    if location is not None:
        location = location.get_text(strip=True)

    description = element.find("div",{"class":"description-content"})
    if description is not None:
        description = description.find("p").get_text(strip=True)

    image_url = element.find("img",{"class":"avatar-img"})
    if image_url is not None:
        image_url = image_url.get("src")

    user_data = {
        "id": user_id,
        "name": name,
        "location": location,
        "description": description,
        "image_url": image_url
    }

    return User(**user_data)
