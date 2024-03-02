import subprocess
from scrape import BrowserOperations


class UserInterface:
    def __init__(self):
        self.operations = BrowserOperations()
        self.headless_flag = 'off'
        self.logged_in = 'Log in to Strava'
        self.athlete_page = None #Athlete Page Goes Here
        self.opt = None

    def title(self):
        print("\x1bc")
        print("\033[38;05;166m███████╗████████╗██████╗  █████╗ ██╗   ██╗ █████╗       ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗")
        print("\033[38;05;172m██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║   ██║██╔══██╗      ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝")
        print("\033[38;05;202m███████╗   ██║   ██████╔╝███████║██║   ██║███████║█████╗███████╗██║     ██████╔╝███████║██████╔╝█████╗")
        print("\033[38;05;208m╚════██║   ██║   ██╔══██╗██╔══██║╚██╗ ██╔╝██╔══██║╚════╝╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝")
        print("\033[38;05;166m███████║   ██║   ██║  ██║██║  ██║ ╚████╔╝ ██║  ██║      ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗")
        print("\033[38;05;172m╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝      ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝")
        print("---------------------------------------- by Roberto Toledo (github.com/g3th) ----------------------------------------")

    def options(self):
        self.title()
        while True:
            print("[1] {}".format(self.logged_in))
            print("[2] Use Headless mode [{}]".format(self.headless_flag))
            print("[3] Get Activity Links")
            self.opt = input("\nPick an Option: ")
            match self.opt:
                case "1":
                    if self.logged_in == 'Logged in':
                        print("You are already Logged in")
                        print("Press Enter")
                        input()
                    else:
                        self.option_one()
                case "2":
                    self.option_two()
                case "3":
                    self.option_three()

    def option_one(self):
        while True:
            self.title()
            user = input("Enter your email: ")
            subprocess.run(['stty', '-echo'], shell=False, stdout=subprocess.DEVNULL)
            passw = input("Enter your password: ")
            repeat = input("Repeat your password: ")
            subprocess.run(['stty', 'echo'], shell=False, stdout=subprocess.DEVNULL)
            if passw == repeat:
                self.operations.strava_login("https://www.strava.com/login", user, passw)
                self.logged_in = 'Logged in'
                break
            else:
                print("Passwords don't match.")
                print("Press Enter")

    def option_two(self):
        if not self.headless_flag:
            self.headless_flag = 'yes'
        else:
            self.headless_flag = 'no'

    def option_three(self):
        self.title()
        print("Scraping Pages... Hands off...")
        self.operations.check_elements(self.athlete_page)
