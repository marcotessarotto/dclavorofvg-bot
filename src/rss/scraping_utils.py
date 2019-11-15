
import urllib.request
from bs4 import BeautifulSoup


def get_content_from_regionefvg_news(URL, attr_name='class', attr_value='foglia-box-content'):
    if URL is None:
        return None

    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')

    results = soup.find_all('div', attrs={attr_name: attr_value})  # https://stackoverflow.com/a/14694669/974287

    if len(results) == 0:
        return None

    s = results[0].get_text()

    if s is not None:
        s = s.strip()

        def sub_split(x):
            return ' '.join(x.split())

        # remove single occurrences of \n but keep in place \n\n(ugly but works)
        s = '\n\n'.join(sub_split(r) for r in s.split('\n\n'))

    return s


