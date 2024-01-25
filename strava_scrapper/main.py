from scraper import StravaScraper
import os

def main():

    password = os.environ.get('STRAVA_PASSWORD')
    email = os.environ.get('STRAVA_EMAIL')

    sc = StravaScraper(email, password, load_cookies_from_file=True)
    sc.login()
    # sc.export_users_info([33337454, 130264404])

    search = input("Search: ")
    users = sc.export_search_results(search)
    print(users)

if __name__ == '__main__':
    main()
