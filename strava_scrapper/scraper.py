import requests
from bs4 import BeautifulSoup
from http.cookiejar import MozillaCookieJar


class StravaScraper:

    def __init__(self, email: str, password: str, load_cookies: bool = True) -> None:
        self._email = email
        self._password = password
        self._load_cookies = load_cookies
    

    