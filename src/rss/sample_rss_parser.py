import datetime

import feedparser

from src.rss.scraping_utils import get_content_from_regionefvg_news

url = "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/570.html"
url ="http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/560.html"


results = get_content_from_regionefvg_news(url)


print("****")

print(results)

print("****")

exit(0)

#
# a = datetime.datetime.now()
# print(a)


def get_feed_entries_from_url(url):

    feed = feedparser.parse(url)

    # print (feed)

    for item in feed.entries:
        # print(item)
        # print(item["title"])
        # print(item["title_detail"])
        print(item["link"])
        # print(item["id"])
        # print(item["updated_parsed"])

        url = item["link"]

        results = get_content_from_regionefvg_news(url)

        if results is not None:
            print("***CONTENT OK***")

    # if 'status' in feed:
    #     feed = manage_http_status(feed, url)
    # else:
    #     # An error happened such that the feed does not contain an HTTP response
    #     manage_non_http_errors(feed, url)
    #     feed = None
    #
    # return feed

url1 = "http://www.regione.fvg.it/rafvg/cms/RAFVG/rss/formazione-lavoro"
url2 = "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/?rss=y"
url3 = "http://www.regione.fvg.it/rafvg/cms/RAFVG/rss/istruzione-ricerca"

get_feed_entries_from_url(url2)

# http://www.regione.fvg.it/rafvg/cms/RAFVG/rss/formazione-lavoro
"""
{
	'title': 'L. 68/99 - Collocamento mirato di Udine: adesioni per due posti di operatore pluriservizi di sala e cucina.',
	'title_detail': {
		'type': 'text/plain',
		'language': None,
		'base': 'http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/?rss=y',
		'value': 'L. 68/99 - Collocamento mirato di Udine: adesioni per due posti di operatore pluriservizi di sala e cucina.'
	},
	'links': [{
		'rel': 'alternate',
		'type': 'text/html',
		'href': 'http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/553.html'
	}],
	'link': 'http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/553.html',
	'published': 'Fri, 04 Oct 2019 09:00:00 GMT',
	'published_parsed': time.struct_time(tm_year = 2019, tm_mon = 10, tm_mday = 4, tm_hour = 9, tm_min = 0, tm_sec = 0, tm_wday = 4, tm_yday = 277, tm_isdst = 0),
	'id': 'http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/553.html',
	'guidislink': False,
	'updated': '2019-10-04T09:00:00Z',
	'updated_parsed': time.struct_time(tm_year = 2019, tm_mon = 10, tm_mday = 4, tm_hour = 9, tm_min = 0, tm_sec = 0, tm_wday = 4, tm_yday = 277, tm_isdst = 0)
}
"""


    # <div class="foglia-box-content">
#
# URL = "https://www.indeed.com/jobs?q=data+scientist+%2420%2C000&l=New+York&start=10"
#
# soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
#
# results = soup.find_all('div', attrs={'data-tn-component': 'organicJob'})
#
# for x in results:
#
#     company = x.find('span', attrs={"class":"company"})
#     if company:
#         print('company:', company.text.strip() )
#
#     job = x.find('a', attrs={'data-tn-element': "jobTitle"})
#     if job:
#         print('job:', job.text.strip())
#
#     salary = x.find('nobr')
#     if salary:
#         print('salary:', salary.text.strip())
#
#     print ('----------')