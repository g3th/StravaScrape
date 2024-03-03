import time
import json
import os
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver


class BrowserOperations:

    def __init__(self):
        self.parse_activity_weeks_links = []
        self.athlete_page = None
        self.year_activity_link_list = []
        self.html_page = False
        self.passw = None
        self.user = None
        self.program_directory = str(Path(__file__).parent)
        self.browser_service = Service(executable_path=str(self.program_directory) + "/Chromedriver/chromedriver")
        self.browser_options = Options()
        self.browser_options.add_argument('--headless=new')
        self.source = None
        self.browser = None
        self.login_exists = False
        self.soup = None

    def login(self, headless):
        if headless == 'on':
            self.browser = webdriver.Chrome(service=self.browser_service, options=self.browser_options)
        else:
            self.browser = webdriver.Chrome(service=self.browser_service)
        self.browser.get("https://www.strava.com/login")
        print("\nOpening Browser...")
        email_box = self.browser.find_element(By.XPATH, "//input[@type='email']")
        password_box = self.browser.find_element(By.XPATH, "//input[@type='password']")
        print("Entering credentials...")
        email_box.send_keys(self.user)
        time.sleep(0.8)
        password_box.send_keys(self.passw)
        time.sleep(0.8)
        log_in = self.browser.find_element(By.XPATH, "//button[@id='login-button']")
        print("Logging in...")
        log_in.click()
        time.sleep(2)
        if self.browser.find_elements(By.XPATH, '//div[@class="alert-message"]'):
            error = self.browser.find_element(By.XPATH, '//div[@class="alert-message"]').text
            if "The username or password did not match" in error:
                print("Login was invalid")
                input("Press Enter")
        else:
            print("All Done.")
            time.sleep(2)
            self.source = self.browser.page_source
            self.write_cookies(self.browser)
            time.sleep(0.3)
            self.browser.close()

    def page_source(self, name, attributes, file_name):
        entire_page = soup(self.source, 'html.parser')
        find = entire_page.find_all(name, attrs=attributes)
        with open(file_name, 'w') as page_html:
            for i in find:
                page_html.write(str(i) + "\n")

    # Parse activity links for every week
    def get_week_links(self, counter):
        with open("data/source_{}".format(counter), 'r') as unparsed_links:
            for i in unparsed_links.readlines():
                if i != "</a>\n":
                    link = "https://www.strava.com" + i.split('<a class="bar" href="')[1].split('"><div')[0]
                    self.parse_activity_weeks_links.append(link)
        unparsed_links.close()
        with open("data/activities_{}".format(counter), 'w') as write_links:
            for i in self.parse_activity_weeks_links:
                write_links.write(i + "\n")
        write_links.close()

    # Extract year activities from entire page html
    def year_activities(self, file_name):
        page_html = open(file_name, 'r')
        for i in page_html.readlines():
            if 'graph_date_range' in str(i):
                link = "https://www.strava.com/" + i.split('href="/')[1].split('">')[0]
                self.year_activity_link_list.append(link)

    def write_cookies(self, browser):
        with open("login_data/cookies.json", 'w') as write_cookies:
            json.dump(browser.get_cookies(), write_cookies, indent=3)

    def load_cookies(self, go_to_athlete_page, parse_page_source):
        with open("login_data/cookies.json", 'r') as read_cookies:
            cookie_jar = json.load(read_cookies)
            for i in cookie_jar:
                self.browser.add_cookie(i)
        read_cookies.close()
        time.sleep(0.5)
        self.browser.refresh()
        if go_to_athlete_page:
            self.browser.get(self.athlete_page)
        time.sleep(0.4)
        self.source = self.browser.page_source
        time.sleep(0.4)
        # Unparsed HTML
        if parse_page_source:
            self.page_source('ul', {'class': 'options'}, "page_html")
        time.sleep(0.8)

    def strava_login(self, user, passw, headless):
        self.user = user
        self.passw = passw
        self.login(headless)

    def check_elements(self, headless):
        page_counter = 0
        self.athlete_page = open("login_data/athlete_page", 'r').readlines()[0]
        while True:
            if [item for item in os.listdir("data") if ("page_html" in item)]:
                self.year_activities("data/page_html")
                print("Found {} Years with Activities".format(len(self.year_activity_link_list)))
                for i in self.year_activity_link_list:
                    if headless == 'on':
                        self.browser = webdriver.Chrome(service=self.browser_service, options=self.browser_options)
                    else:
                        self.browser = webdriver.Chrome(service=self.browser_service)
                    self.browser.get(i)
                    print("Scraping Activities for year {}".format(page_counter))
                    self.load_cookies(False, False)
                    time.sleep(0.3)
                    self.page_source('a', {'class': 'bar'}, "data/source_{}".format(page_counter))
                    self.get_week_links(page_counter)
                    self.parse_activity_weeks_links = []
                    self.browser.close()
                    os.remove("data/source_{}".format(page_counter))
                    page_counter += 1
                break
            else:
                if headless == 'on':
                    self.browser = webdriver.Chrome(service=self.browser_service, options=self.browser_options)
                else:
                    self.browser = webdriver.Chrome(service=self.browser_service)
                print("Extracting links for all-year round activity/activities")
                self.browser.get(self.athlete_page)
                time.sleep(0.6)
                self.load_cookies(True, True)
                time.sleep(0.4)
                self.page_source('ul', {'class': 'options'}, "data/page_html")

    def fetch_interval_value(self, headless, page):
        if headless == 'on':
            self.browser = webdriver.Chrome(service=self.browser_service, options=self.browser_options)
        else:
            self.browser = webdriver.Chrome(service=self.browser_service)
        self.browser.get(page)
        time.sleep(0.8)
        self.load_cookies(False, False)
        time.sleep(0.8)
        raw = self.browser.page_source
        parse = soup(raw, 'html.parser')
        find = parse.find_all('h2', attrs={'id':'interval-value'})
        return find[0].text

