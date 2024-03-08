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

    def get_athlete_name(self, athlete_page):
        self.browser = webdriver.Chrome(service=self.browser_service, options=self.browser_options)
        print("Fetching Athlete...")
        self.browser.get(athlete_page)
        raw_html_for_athlete_name = soup(self.browser.page_source, 'html.parser')
        athlete_name_element = raw_html_for_athlete_name.find_all('h2', {'data-testid': 'details-name'})
        with open("login_data/athlete", 'w') as athlete:
            athlete.write(athlete_name_element[0].text)
        return athlete_name_element[0].text

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
            self.page_source('ul', {'class': 'options'}, "data/page_html")
        time.sleep(0.8)

    def strava_login(self, user, passw, headless):
        self.user = user
        self.passw = passw
        self.login(headless)

    def check_elements(self, headless):
        page_counter = 1
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
        time.sleep(3)
        raw = self.browser.page_source
        parse = soup(raw, 'html.parser')
        links = []
        titles = []
        date = parse.find_all('h2', attrs={'id': 'interval-value'})
        unparsed_links = parse.find_all('a', attrs={'data-testid': 'activity_name'})
        for i in unparsed_links:
            links.append(str(i).split('href="')[1].split('">')[0])
            titles.append(i.text)
        return date[0].text.replace("\n", ""), links, titles

    def activity_data_scraper(self, headless, activity_link, activity_title_, activity_date):
        if headless == 'on':
            self.browser = webdriver.Chrome(service=self.browser_service, options=self.browser_options)
        else:
            self.browser = webdriver.Chrome(service=self.browser_service)
        self.browser.get(activity_link)
        time.sleep(0.8)
        self.load_cookies(False, False)
        time.sleep(0.8)
        time.sleep(7)
        source = self.browser.page_source
        s = soup(source, 'html.parser')
        unparsed_activity_type = s.find('span', {'class': 'title'})
        # Run, Hike etc
        activity_type = str(unparsed_activity_type).replace("\n", "").replace("–", "").split("</a>")[1].split("<")[0]
        # Time splits i.e. 1 - 6:00 /mile - 5 meters (Split Number - Minutes per mile/km - GAP - elevation)
        splits = s.find_all('td', {'class': 'centered'})
        # Details: Time, date and Location
        details_contents_div = s.find('div', {'class': 'details'})
        activity_time_and_date = details_contents_div.find_next('time').text.strip()
        activity_location = details_contents_div.find_next('span').text.strip()
        inline_stats = s.find('ul', {'class': 'inline-stats section'})
        total_distance = inline_stats.find_next('li').find_next('strong').text
        moving_time = inline_stats.find_next('li').find_next('strong').find_next('strong').text
        pace = inline_stats.find_next('li').find_next('strong').find_next('strong').find_next('strong').text
        time_date_and_location = "{} - {}".format(activity_time_and_date, activity_location)
        counter = 1
        store_splits = []
        # Stores Splits when present in an activity.
        # These are not always present, like in Swimming, hiking etc...
        # Try block is used to determine whether user has GAP in splits.
        # This is only present if user is Premium, otherwise sibling will not exist.
        for i in splits:
            try:
                store_splits.append(
                    "[{}] | {} | {}".format(counter, i.find_next_sibling("td").text.strip(),
                                            i.find_next_sibling("td").find_next_sibling(
                                                'td').find_next_sibling('td').text.strip()))
            except AttributeError:
                store_splits.append(
                    "[{}] | {} | {}".format(counter, i.find_next_sibling("td").text.strip(),
                                            i.find_next_sibling("td").find_next_sibling(
                                                'td').text.strip()))
            counter += 1
        activity_title = activity_title_.replace("/","-")
        with open("data/{}/'{}'".format(activity_date, activity_title), 'w') as splits_file:
            splits_file.write("----------------------------------\n")
            splits_file.write('Activity Title "{}"\n'.format(activity_title))
            splits_file.write("----------------------------------\n")
            splits_file.write("Activity Type - {}\n".format(activity_type))
            splits_file.write("----------------------------------\n")
            splits_file.write("{}\n".format(time_date_and_location))
            splits_file.write("----------------------------------\n")
            splits_file.write(
                "Total Distance: {} | Moving Time: {} | Pace: {}".format(total_distance, moving_time, pace))
            splits_file.write("\n----------------------------------\n")
            for i in store_splits:
                splits_file.write(i + "\n")
        splits_file.close()

    def photo_scraper(self, page):
        self.browser = webdriver.Chrome(service=self.browser_service, options = self.browser_options)
        self.browser.get(page)
        time.sleep(0.8)
        self.load_cookies(False, False)
        time.sleep(3)
        source = self.browser.page_source
        s = soup(source, 'html.parser')
        find = s.find('div', {'data-react-class':'MediaThumbnailList'})
        a = str(find).replace('&quot;','"').replace("\\u0026","&").split('"large":')
        links = []
        for i in range(len(a)):
            if i % 2 == 0 or i == [0]:
                pass
            else:
                links.append(a[i].split(',')[0].split("{")[0].replace('"',''))
        self.browser.close()
        return links
