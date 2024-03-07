import subprocess
from scrape import BrowserOperations
import os


class UserInterface:
    def __init__(self):
        self.athlete_name = None
        self.colors = ['166', '202']
        self.activities_are_present = False
        self.menu_options = ['1', '2', '3', '4', '5', '6']
        self.operations = BrowserOperations()
        self.headless_flag = 'on'
        self.logged_in = 'Store Credentials'
        self.athlete_page = "Store Athlete Page"
        self.opt = None
        try:
            os.mkdir("data")
        except FileExistsError:
            pass
        try:
            os.mkdir("login_data")
        except FileExistsError:
            pass

    def title(self):
        counter = 0
        title = open("assets/art.txt").readlines()
        print("\x1bc")
        for i in title:
            if counter > len(self.colors) - 1:
                counter = 0
            print("\033[38;05;{}m".format(self.colors[counter]) + i, end='')
            counter += 1
        print()
        chromedriver_note = open('Chromedriver/note').readlines()
        for i in chromedriver_note:
            print(i, end='')
        print()

    def checks(self):
        for i in os.listdir("login_data"):
            if i == "athlete_page":
                self.athlete_name = open("login_data/athlete").readline()
                self.athlete_page = "Athlete Page Stored [Athlete is {}]".format(self.athlete_name)
            if i == "cookies.json":
                self.logged_in = "Credentials Stored"

    def options(self):
        self.checks()
        while True:
            self.title()
            if [item for item in os.listdir("data") if ("activities" in item)]:
                self.activities_are_present = True
                self.menu_options = ['1', '2', '3', '4', '5', '6']
            print("[{}] {}".format(self.menu_options[0], self.logged_in))
            print("[{}] Use Headless mode [{}]".format(self.menu_options[1], self.headless_flag))
            print("[{}] Get Activity Links".format(self.menu_options[2]))
            print("[{}] {} ".format(self.menu_options[3], self.athlete_page))
            print("[{}] Enter Activity Sub Menu".format(self.menu_options[4], self.athlete_page))
            print("[{}] Quit".format(self.menu_options[5]))
            self.opt = input("\nPick an Option: ")
            match self.opt:
                case "1":
                    if self.logged_in == "Credentials Stored":
                        print("You are already Logged in")
                        print("Press Enter")
                        input()
                    else:
                        self.option_one()
                case "2":
                    self.option_two()
                case "3":
                    if not self.athlete_name:
                        print("There is no athlete page stored.")
                        print("Press Enter")
                        input()
                    elif self.logged_in != "Credentials Stored":
                        print("There are no credentials stored.")
                        print("Press Enter")
                        input()
                    else:
                        if self.activities_are_present:
                            print("Activities have already been scraped")
                            input("Press Enter")
                        else:
                            self.option_three()
                case "4":
                    if self.athlete_page == "Athlete Page Stored [Athlete is {}]".format(self.athlete_name):
                        print("Athlete page is already stored")
                        print("Press Enter")
                        input()
                    else:
                        self.option_four()
                case "5":
                    if [file for file in os.listdir("data") if ("activities" in file)]:
                        self.sub_menu()
                    else:
                        print("Scrape some activities first.")
                        input("Press Enter.")
                case "6":
                    print("Goodbye")
                    exit()
                case _:
                    print("Invalid Option")
                    input("Press Enter")

    def sub_menu(self):
        self.title()
        counter = 1
        activities = []
        files = [file for file in os.listdir("data") if os.path.isfile("data/" + file)]
        for i in files:
            if "page" in i:
                pass
            else:
                activities.append(i)
        print("\n{} Year/s of activity/activities in total:\n".format(len(activities)))
        for i in activities:
            total_activity_links = open("data/{}".format(i)).readlines()
            print("[{}] Year {} Has {} Activity/Activities".format(counter, counter, len(total_activity_links)))
            counter += 1
        user_option = int(input("\nPick an Option: "))
        chosen_year = user_option - 1
        self.title()
        chosen_activity_year = open("data/activities_{}".format(chosen_year)).readlines()
        counter = 1
        files = [file for file in os.listdir("data") if os.path.isdir("data/" + file) and "Activities" in file]
        print("Found Activities for the following date ranges:\n")
        dates = []
        activity_links = []
        if files:
            for i in files:
                print("[{}] {}".format(counter, i))
                dates.append(i)
                counter += 1
            opt = int(input("\nPick a date range: "))
            date_range_choice = opt - 1
            with open("data/{}/week_activities_links".format(dates[date_range_choice])) as a_links:
                for j in a_links.readlines():
                    activity_links.append(j.strip())
            self.title()
            date_only = dates[date_range_choice].split("for ")[1]
            print("The following activities are available for date range: {}\n".format(date_only))
            counter = 1
            for i in activity_links:
                print("[{}] {}".format(counter, i.split(" | ")[1]))
                counter += 1
            opt = int(input("\nPick an activity: "))
            activity_choice = opt - 1
            self.title()
            activity_title = activity_links[activity_choice].split(" | ")[1]
            link = activity_links[activity_choice].split(" | ")[0]
            print("Scraping Metrics for activity '{}'".format(activity_title))
            self.operations.activity_data_scraper(self.headless_flag, "https://" + link, activity_title, dates[date_range_choice])
            print("Metrics saved in file titled: {}".format(activity_title))
            input("Press Enter to Return")
        else:
            date = None
            week_links = []
            activity_titles = []
            print("Populating List:")
            for i in chosen_activity_year:
                date, links, titles = self.operations.fetch_interval_value(self.headless_flag, i)
                print("[{}] {}".format(counter, date))
                os.makedirs("data/{}".format(date), exist_ok=True)
                for j in range(len(links)):
                    week_links.append(links[j - 1])
                    activity_titles.append(titles[j - 1])
                with open("data/{}/week_activities_links".format(date), 'w') as w_links:
                    for i in range(len(week_links)):
                        # Split by Pipe.
                        # One case could be that user starts activity with "|", and 'split' returns wrong date (above).
                        # This is improbable, but still possible.
                        w_links.write("www.strava.com{} | {}\n".format(week_links[i], activity_titles[i]))
                week_links = []
                activity_titles = []
                counter += 1

            print("\n\nData was stored.")
            input("Press Enter")

    # Login
    def option_one(self):
        while True:
            self.title()
            user = input("Enter your email: ")
            subprocess.run(['stty', '-echo'], shell=False, stdout=subprocess.DEVNULL)
            passw = input("Enter your password: ")
            repeat = input("\nRepeat your password: ")
            subprocess.run(['stty', 'echo'], shell=False, stdout=subprocess.DEVNULL)
            if passw == repeat:
                self.operations.strava_login(user, passw, self.headless_flag)
                self.logged_in = 'Credentials Stored'
                break
            else:
                print("Passwords don't match.")
                print("Press Enter")
                input()

    # Set Headless Mode

    def option_two(self):
        if self.headless_flag == "off":
            self.headless_flag = "on"
        else:
            self.headless_flag = "off"

    def option_three(self):
        self.title()
        print("Scraping Pages... Hands off...")
        self.operations.check_elements(self.headless_flag)
        print("Done. Press Enter")
        input()

    # User Strava Page

    def option_four(self):
        self.title()
        user_page = input("Enter your athlete url: ")
        athlete_name = self.operations.get_athlete_name(user_page)
        with open("login_data/athlete_page", 'w') as page:
            page.write(user_page)
        page.close()
        self.athlete_page = "Athlete Page Stored [Athlete is {}]".format(athlete_name)

    def activity_data_menu(self):
        print("1) Heart Rate")