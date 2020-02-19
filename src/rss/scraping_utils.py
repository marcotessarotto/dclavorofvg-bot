
import urllib.request

import bs4
from bs4 import BeautifulSoup


counter = 0

tg_allowed_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del',
                   'a', 'code', 'pre']


# Pass soup.body in following
def process_node(node):
    global counter

    s = str(node)

    # print(f"process_node: {counter} TAG: {node.name}  str(): {s[:128]} ")
    counter = counter + 1
    if node is None:
        return ""

    if type(node) == bs4.element.NavigableString:
        return node
    else:
        # print(f"len(node.contents)={len(node.contents)}")
        if node.name == 'br' and len(node.contents) == 0:
            return "\n\n"
        elif node.name in tg_allowed_tags and  len(node.contents) == 1:
            if 'target' in node.attrs:  # remove target attribute (from a tag)
                del node.attrs['target']

            return str(node)
        elif len(node.contents) == 1:
            return process_node(node.contents[0])
        elif len(node.contents) > 1:
            try:
                return " ".join([process_node(child) for child in node.children])
            except TypeError:
                print(f"TypeError: {node}")
                return ""

        return ""


def get_content_from_regionefvg_news(URL, attr_name='class', attr_value='foglia-box-content'):
    if URL is None:
        return None

    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')

    results = soup.find_all('div', attrs={attr_name: attr_value})  # https://stackoverflow.com/a/14694669/974287

    if len(results) == 0:
        return None

    # s = results[0].get_text()
    s = process_node(results[0])

    if s is not None:
        s = s.strip()

        def sub_split(x):
            return ' '.join(x.split())

        # remove single occurrences of \n but keep in place \n\n(ugly but works)
        s = '\n\n'.join(sub_split(r) for r in s.split('\n\n'))

    return s


