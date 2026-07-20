import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def crawl(url):
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

if __name__ == '__main__':
    url = input('크롤링할 URL: ')
    soup = crawl(url)
    print(soup.get_text()[:500])
