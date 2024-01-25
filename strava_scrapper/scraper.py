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
    load_user_profile_data,
    retrieve_search_results
)

from errors import NotLoggedInError


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
            raise NotLoggedInError("You might want to refresh the cookies and check if your login credentials are correct.")

    def login(self) -> None:
        self._session = requests.Session()
        result = self.__load_cookies()
        self.__check_if_logged_in()

    def export_users_info(self, ids: list[int]) -> list[dict[str, str]]:

        results = []

        for user_id in ids:

            profile_url = f"https://www.strava.com/athletes/{user_id}"
            response = get_request(self._session, profile_url)

            user_model = load_user_profile_data(user_id, response.text)
            results.append(user_model)

            time.sleep(0.5)

        return results

    def export_search_results(self, search: str) -> list[dict]:

        params = {
            "page": "1",
            "page_uses_modern_javascript": "true",
            "text": search.replace(" ", "+"),
            "utf8": "✓"
        }

        url = f"https://www.strava.com/athletes/search"
        response = get_request(self._session, url, params=params)

        results = retrieve_search_results(response.text)
        return results
