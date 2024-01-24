import requests
from bs4 import BeautifulSoup

from utils import (
    load_cookies, 
    post_request, 
    get_request,
    load_csrf_token
)


class StravaScraper:

    COOKIES_PATH = './strava_scrapper/cookies.txt'
    LOGIN_URL = 'https://www.strava.com/login'

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
            "utf8": "",
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
        csrf_token = load_csrf_token(soup)
        data = self.__get_session_data(csrf_token)
        response = post_request(
            self._session, 
            'https://www.strava.com/session', 
            allow_redirects=False, 
            data=data
        )
        self._session.cookies.save(ignore_discard=True)
        # return response.headers["Location"] == "https://www.strava.com/dashboard"
        return True
    
    def __check_if_logged_in(self) -> bool:
        url = "https://www.strava.com/dashboard"
        response = get_request(self._session, url, allow_redirects=True)
        if not response.url == "https://www.strava.com/onboarding":
            raise Exception("User not logged in")

    def login(self) -> None:

        self._session = requests.Session()
        result = self.__load_cookies()
        self.__check_if_logged_in()

        print('Logged in!')
