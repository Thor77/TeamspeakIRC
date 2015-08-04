from bs4 import BeautifulSoup
import cfscrape


def get():
    scraper = cfscrape.create_scraper()
    data = scraper.get('http://npl.teamspeakusa.com/ts3npl.php').content
    soup = BeautifulSoup(data, 'html.parser')
    raw_status = soup.find_all(class_='register_linklabel')[2].span
    return not raw_status
