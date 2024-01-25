import requests
import time
import os
from bs4 import BeautifulSoup

from utils import (
    load_cookies, 
    post_request, 
    get_request,
    load_csrf_token,
    load_user_profile_data,
    retrieve_search_results,
    export_to_json_file
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
        self._results_path = "./strava_scrapper/results/"

        if not os.path.exists(self._results_path):
            os.makedirs(self._results_path)

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
        return True
    
    def __check_if_logged_in(self) -> bool:
        response = get_request(self._session, self.DASHBOARD_URL, allow_redirects=True)
        if not response.url == self.ONBOARD_URL:
            raise NotLoggedInError("You might want to refresh the cookies and check if your login credentials are correct.")

    def login(self) -> None:
        self._session = requests.Session()
        result = self.__load_cookies()
        self.__check_if_logged_in()

    def export_users_info(
        self, 
        ids: list[str],
        export_to_json: bool = True, 
        json_filename: str = "users_info.json"
    ) -> list[dict[str, str]]:

        results = []

        for user_id in ids:

            profile_url = f"https://www.strava.com/athletes/{user_id.strip()}"
            response = get_request(self._session, profile_url)

            # Means that the user related to this ID doesn't exist
            if response.url == "https://www.strava.com/athletes/search":
                continue

            user_model = load_user_profile_data(user_id, response.text)
            results.append(user_model)

            time.sleep(0.5)

        if export_to_json:
            export_to_json_file(results, f"{self._results_path}{json_filename}")

        return results

    def export_search_results(
        self, 
        search: str, 
        num_of_pages: int = 1,
        export_to_json: bool = True, 
        json_filename: str = "search_results.json"
    ) -> list[dict]:
        
        results = []
        
        for num in range(0, num_of_pages):

            params = {
                "page": num + 1,
                "page_uses_modern_javascript": "true",
                "text": search.replace(" ", "+"),
                "utf8": "✓"
            }

            url = f"https://www.strava.com/athletes/search"
            response = get_request(self._session, url, params=params)

            page_result = retrieve_search_results(response.text)
            if not page_result:
                break

            results.extend(page_result)
            time.sleep(0.5)

        if export_to_json:
            export_to_json_file(results, f"{self._results_path}{json_filename}")
        return results
