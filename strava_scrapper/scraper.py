import requests
import time
from bs4 import BeautifulSoup
from bs4 import Tag
from typing import Any

from utils import (
    load_cookies, 
    post_request, 
    get_request,
    load_csrf_token,
    load_user_data
)

from errors import NotLoggedInError

from models.user import User


class StravaScraper:

    COOKIES_PATH = "./strava_scrapper/cookies.txt"
    LOGIN_URL = "https://www.strava.com/login"
    SESSION_URL = "https://www.strava.com/session"
    DASHBOARD_URL = "https://www.strava.com/dashboard"
    ONBOARD_URL =  "https://www.strava.com/onboarding"

    def __init__(
        self, 
        email: str, 
        password: str, 
        load_cookies_from_file: bool = True
    ) -> None:
        self._email = email
        self._password = password
        self._load_cookies_from_file = load_cookies_from_file
        self._session = None

    def __get_session_data(self, csrf_token: str) -> dict[str, str]:
        return {
            "utf8": "✓",
            "authenticity_token": csrf_token,
            "plan": "",
            "password": self._password,
            "email": self._email,
        }

    def __load_cookies(self) -> bool:

        status = load_cookies(self._session, self.COOKIES_PATH, self._load_cookies_from_file)

        if self._load_cookies_from_file and status:
            return True
    
        response = get_request(self._session, self.LOGIN_URL, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'lxml')
        csrf_token = load_csrf_token(soup) # what if CsrfTokenNotFoundError is raised?
        data = self.__get_session_data(csrf_token)
        response = post_request(
            self._session, 
            self.SESSION_URL, 
            allow_redirects=False, 
            data=data
        )
        self._session.cookies.save(ignore_discard=True)
        # return response.headers["Location"] == "https://www.strava.com/dashboard"
        return True
    
    def __check_if_logged_in(self) -> bool:
        response = get_request(self._session, self.DASHBOARD_URL, allow_redirects=True)
        if not response.url == self.ONBOARD_URL:
            raise NotLoggedInError

    def login(self) -> None:
        self._session = requests.Session()
        result = self.__load_cookies()
        self.__check_if_logged_in()

    def export_users_info(self, ids: list[int]) -> list[User]:

        results = []

        for user_id in ids:

            profile_url = f"https://www.strava.com/athletes/{user_id}"
            response = get_request(self._session, profile_url)

            soup = BeautifulSoup(response.text, 'lxml')
            content = soup.select_one("div.profile-heading.profile.section")

            user_model = load_user_data(user_id, content)
            results.append(user_model)
            
            time.sleep(0.5)

        return results

    def export_search_results(self, search: str) -> list[dict]:

        users = []

        formatted_search = search.replace(" ", "+")

        params = {
            "page": "1",
            "page_uses_modern_javascript": "true",
            "text": formatted_search,
            "utf8": "✓"
        }

        url = f"https://www.strava.com/athletes/search"
        response = get_request(self._session, url, params=params)

        soup = BeautifulSoup(response.text, 'lxml')

        content = soup.select_one("ul.athlete-search.striped.container-fluid")
        rows = content.find_all("div", {"class": "athlete-details"})
        for i in rows:
            name = i.find("a", {"class": "athlete-name-link"}).get_text(strip=True)
            user_id = i.find("a", {"class": "athlete-name-link"}).get("data-athlete-id")

            users.append({
                "name": name,
                "id": user_id
            })

        return users
