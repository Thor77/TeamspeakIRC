import re

from bs4 import BeautifulSoup

import cfscrape


def nplstatus():
    scraper = cfscrape.create_scraper()
    data = scraper.get('http://npl.teamspeakusa.com/ts3npl.php').content
    soup = BeautifulSoup(data, 'html.parser')
    raw_status = soup.find_all(class_='register_linklabel')[2].span
    return not raw_status


def latest_version():
    scraper = cfscrape.create_scraper()
    data = scraper.get('http://teamspeak.com/downloads').content
    soup = BeautifulSoup(data, 'html.parser')

    def search(search_string):
        return soup.find_all(text=re.compile(search_string))[0].parent.\
                find(class_='version').text
    return search(r'Client\ 64\-bit'), search(r'Server\ 64\-bit')
