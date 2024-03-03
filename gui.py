import subprocess
from scrape import BrowserOperations
import os


class UserInterface:
    def __init__(self):
        self.colors = ['166', '202']
        self.activities_are_present = False
        self.menu_options = ['1','2','3','4','5']
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
                self.athlete_page = "Athlete Page Stored"
            if i == "cookies.json":
                self.logged_in = "Credentials Stored"

    def options(self):
        self.checks()
        while True:
            self.title()
            if [item for item in os.listdir("data") if ("activities" in item)]:
                self.activities_are_present = True
                self.menu_options = ['1', '2', '3', '4', '5', '6']
            print("[{}] {}".format(self.menu_options[0],self.logged_in))
            print("[{}] Use Headless mode [{}]".format(self.menu_options[1], self.headless_flag))
            print("[{}] Get Activity Links".format(self.menu_options[2]))
            print("[{}] {}".format(self.menu_options[3], self.athlete_page))
            if len(self.menu_options) == 6:
                print("[{}] Enter Activity Sub Menu".format(self.menu_options[4], self.athlete_page))
                print("[{}] Quit".format(self.menu_options[5]))
            else:
                print("[{}] Quit".format(self.menu_options[4]))
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
                    if self.athlete_page != "Athlete Page Stored":
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
                    if self.athlete_page == "Athlete Page Stored":
                        print("Athlete page is already stored")
                        print("Press Enter")
                        input()
                    else:
                        self.option_four()
                case "5":
                    if len(self.menu_options) == 6:
                        self.sub_menu()
                    else:
                        print("Goodbye")
                        exit()
                case "6":
                    if len(self.menu_options) == 6:
                        print("Goodbye")
                        exit()
                    else:
                        print("Invalid Option")
                        input("Press Enter")
                case _:
                    print("Invalid Option")
                    input("Press Enter")

    def sub_menu(self):
        self.title()
        counter = 1
        activities = []
        for i in os.listdir("data"):
            if "page" in i:
                pass
            else:
                activities.append(i)
        print("\n{} Year/s of activity/activities in total:\n".format(len(activities)))
        for i in activities:
            total_activity_links = open("data/{}".format(i)).readlines()
            print("[{}] Year {} Has {} Activity/Activities".format(counter, counter, len(total_activity_links)))
            counter += 1
        chosen_year = int(input("\nPick an Option: "))
        self.title()
        chosen_activity_year = open("data/{}".format(activities[chosen_year - 1])).readlines()
        print("Populating List:")
        counter = 1
        for i in chosen_activity_year:
            print("[{}] {}".format(counter, self.operations.fetch_interval_value(self.headless_flag, i)))
            counter += 1
        exit()

    #Login

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
        self.menu_options = ['1', '2', '3', '4', '5', '6']
        print("Done. Press Enter")
        input()
    # User Strava Page

    def option_four(self):
        self.title()
        user_page = input("Enter your athlete url: ")
        with open("login_data/athlete_page", 'w') as page:
            page.write(user_page)
        page.close()
        self.athlete_page = "Athlete Page Stored"