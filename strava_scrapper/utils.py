import requests
import json
from typing import Any
from http.cookiejar import MozillaCookieJar
from bs4 import BeautifulSoup
from bs4 import Tag
from errors import CsrfTokenNotFoundError

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

def load_user_profile_data(user_id: int, html_content: str) -> dict[str, str]:

    soup = BeautifulSoup(html_content, 'lxml')
    container = soup.select_one("div.profile-heading.profile.section")

    name = container.find("h1",{"class":"athlete-name"})
    if name is not None:
        name = name.get_text(strip=True)
    
    location = container.find("div",{"class":"location"})
    if location is not None:
        location = location.get_text(strip=True)

    description = container.find("div",{"class":"description-content"})
    if description is not None:
        description = description.find("p").get_text(strip=True)

    image_url = container.find("img",{"class":"avatar-img"})
    if image_url is not None:
        image_url = image_url.get("src")

    user_data = {
        "id": user_id,
        "name": name,
        "location": location,
        "description": description,
        "image_url": image_url
    }

    return user_data

def load_user_search_data(user_row: Tag) -> dict[str, Any]:

    name = user_row.find("a", {"class": "athlete-name-link"})
    if name is not None:
        name = name.get_text(strip=True)

    user_id = user_row.find("a", {"class": "athlete-name-link"})
    if user_id is not None:
        user_id = user_id.get("data-athlete-id")
        user_id = int(user_id)

    return {"name": name, "id": user_id }

def retrieve_search_results(html_content: str) -> list[dict]:

    users = []

    soup = BeautifulSoup(html_content, 'lxml')
    container = soup.select_one("ul.athlete-search.striped.container-fluid")

    rows = container.find_all("div", {"class": "athlete-details"})
    for row in rows:

        data = load_user_search_data(row)
        users.append(data)

    return users

def export_to_json_file(data: Any, file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
