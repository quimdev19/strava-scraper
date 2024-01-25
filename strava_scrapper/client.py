from getpass import getpass
from pprint import pprint

from scraper import StravaScraper

def display_options_info() -> None:
    print('\n-----------------------------------------------------------------')
    print("1. Please provide a list of user IDs to retrieve user profiles.")
    print("2. Enter a name to find users matching that name.")
    print("Type 'exit' if you want to stop the program.")
    print('-----------------------------------------------------------------\n')

def scraper_client() -> None:

    email = input("Email: ")
    password = getpass("Password: ")

    load_cookies = input("Load cookies from file (Y/n): ")
    load_cookies = load_cookies.upper() == "Y"

    export_to_file = input("Export results to a JSON file (Y/n): ")
    export_to_file = export_to_file.upper() == "Y"

    sc = StravaScraper(email, password, load_cookies_from_file=load_cookies)
    sc.login()

    while True:

        display_options_info()
        print("Type 'options' to display the options")
        option = input("Option (1, 2): ")

        if option == "1":

            users_ids = input("Insert the users IDs (separated by commas): ")
            users_ids = users_ids.split(",")

            results = sc.export_users_info(users_ids, export_to_json=export_to_file)
            pprint(results)
        
        elif option == "2":

            search = input("Insert a name: ")
            search = search.strip()

            results = sc.export_search_results(search, export_to_json=export_to_file)
            pprint(results)

        elif option == "exit":
            exit()
