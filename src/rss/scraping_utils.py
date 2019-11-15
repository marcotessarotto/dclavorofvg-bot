
import urllib.request
from bs4 import BeautifulSoup


def get_content_from_regionefvg_news(URL, attr_name='class', attr_value='foglia-box-content'):
    if URL is None:
        return None

    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')

    results = soup.find_all('div', attrs={attr_name: attr_value})  # https://stackoverflow.com/a/14694669/974287

    if len(results) == 0:
        return None

    s = results[0].get_text()  #.replace('\n','\n\n')

    if s is not None:
        s = s.strip()

    return s


