import time
import json
import os
from bs4 import BeautifulSoup as soup
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver


# user = input("user: ")
# passw = input("passw: ")
class BrowserOperations:

    def __init__(self):

        self.parse_activity_weeks_links = []
        self.athlete_page = None #Athlete Page goes here
        self.year_activity_link_list = []
        self.html_page = False
        self.passw = None
        self.user = None
        self.program_directory = Path(__file__).parent
        self.browser_options = Service(executable_path=str(self.program_directory) + "/Chromedriver/chromedriver")
        self.source = None
        self.browser = None
        self.login_exists = False
        self.soup = None

    def login(self):
        self.browser = webdriver.Chrome(service=self.browser_options)
        email_box = self.browser.find_element(By.XPATH, "//input[@type='email']")
        password_box = self.browser.find_element(By.XPATH, "//input[@type='password']")
        email_box.send_keys(self.user)
        time.sleep(0.8)
        password_box.send_keys(self.passw)
        time.sleep(0.8)
        log_in = self.browser.find_element(By.XPATH, "//button[@id='login-button']")
        log_in.click()
        time.sleep(3)
        self.source = self.browser.page_source
        self.browser.close()

    def page_source(self, name, attributes, file_name):
        entire_page = soup(self.source, 'html.parser')
        find = entire_page.find_all(name, attrs=attributes)
        with open(file_name, 'w') as page_html:
            for i in find:
                page_html.write(str(i) + "\n")

    # Parse activity links for every week
    def get_week_links(self, counter):
        with open("source_{}".format(counter), 'r') as unparsed_links:
            for i in unparsed_links.readlines():
                if i != "</a>\n":
                    link = "https://www.strava.com" + i.split('<a class="bar" href="')[1].split('"><div')[0]
                    self.parse_activity_weeks_links.append(link)
        unparsed_links.close()
        with open("activities_{}".format(counter), 'w') as write_links:
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

    def write_cookies(self):
        with open("cookies.json", 'w') as write_cookies:
            json.dump(self.browser.get_cookies(), write_cookies, indent=3)

    def load_cookies(self, go_to_athlete_page, parse_page_source):
        with open("cookies.json", 'r') as read_cookies:
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

    def strava_login(self, page, user, passw):
        self.user = user
        self.passw = passw
        self.login()
        self.write_cookies()

    def check_elements(self, page):
        page_counter = 0
        files_list = []
        for i in os.listdir():
            files_list.append(i)
        if [file for file in files_list if ("cookies.json" in file)]:
            if [f for f in files_list if ("page_html" in f)]:
                self.year_activities("page_html")
                for j in self.year_activity_link_list:
                    self.browser = webdriver.Chrome(service=self.browser_options)
                    self.browser.get(page)
                    self.load_cookies(False,False)
                    self.page_source('a', {'class': 'bar'}, "source_{}".format(page_counter))
                    self.get_week_links(page_counter)
                    self.parse_activity_weeks_links = []
                    self.browser.close()
                    page_counter += 1
            else:
                self.login()
                self.load_cookies(True, True)
            # returns full year activity page
