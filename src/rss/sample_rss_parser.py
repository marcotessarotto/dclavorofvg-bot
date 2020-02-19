import datetime

import feedparser
from bs4 import BeautifulSoup

from src.rss.scraping_utils import get_content_from_regionefvg_news, process_node

s = '''<div class="foglia-box-content">
<p>Sono diverse le nuove 
<strong>offerte di lavoro</strong> nel 
<strong>settore alimentare</strong> provenienti dai Centri impiego FVG. </p>
<p>Si cerca in particolare la figura di 
<strong>tecnologo alimentare</strong>, per la quale sono necessari uno specifico titolo di studio e
competenza.
<br/> </p>
<p>
<strong>Offerte per tecnologo alimentare
<br/></strong>
<br/>• 
<strong>Dietista/Tecnologo alimentare</strong>
<br/>Sede di lavoro: 
<strong>Trieste</strong>, Ospedale di Cattinara
<br/>Mansioni: la risorsa si occuperà di stilare diete speciali per i pazienti e di controllo
qualità delle pietanze.
<br/>Contratto offerto: tempo determinato
<br/>Scadenza offerta: 10 febbraio 2020
<br/>Vai all’offerta, codice 
<a href="http://bit.ly/2Sq3AVn" target="_blank">L424-29959</a></p>
<p>• 
<strong>Tecnologo alimentare</strong>
<br/>Sede di lavoro: 
<strong>San Daniele del Friuli</strong>, prosciuttificio
<br/>Mansioni: la risorsa si occuperà di controllo qualità, gestione rapporti con i veterinari,
gestione procedure di autocontrollo aziendale, collaborazione alla spedizione merci
<br/>Contratto offerto: contratto di 24 mesi con possibilità di trasformazione in indeterminato
<br/>Scadenza offerta: 29 febbraio 2020.
<br/>Vai all'offerta, codice 
<a href="http://bit.ly/2uu9VqB" target="_blank">H816-29042 </a></p>
<p>• 
<strong>Tecnico in scienze e tecnologie alimentari</strong>
<br/>Sede di lavoro: 
<strong>San Vito al Tagliamento</strong>
<br/>Mansioni: controllo qualità dei prodotti alimentari e relativa documentazione
<br/>Contratto offerto: apprendistato (offerta riservata a giovani under 30 iscritti o iscrivibili
a Garanzia Giovani)
<br/>Scadenza offerta: 15 febbraio 2020
<br/>Vai all’offerta, codice 
<a href="https://offertelavoro.regione.fvg.it/lavoroFVG/dettaglio/I403-29958" target="_blank">I403-29958</a></p>
<p>• 
<strong>Tecnologo alimentare</strong>
<br/>Sede di lavoro: 
<strong>Chions</strong>
<br/>Mansioni: mastro birraio, cantiniere con mansioni di gestione della produzione,
imbottigliamento, sanificazione cisterne
<br/>Contratto offerto: tempo determinato 1 anno
<br/>Scadenza offerta: 29 febbraio 2020
<br/>Vai all’offerta, 
<a href="http://bit.ly/2UE7U6l" target="_blank">codice C640-2996</a>
<br/> </p>
<p>
<strong>Altre offerte in ambito alimentare</strong>
<br/>
<br/>• 
<strong>Operaio addetto al confezionamento, 20 posti disponibili</strong>
<br/>Sede di lavoro: 
<strong>Gorizia</strong>
<br/>Mansioni: confezionamento prodotti alimentari, metallici o cosmetici
<br/>Contratto offerto: in somministrazione
<br/>Scadenza offerta: 27 febbraio 2020
<br/>Vai all’offerta, 
<a href="https://offertelavoro.regione.fvg.it/lavoroFVG/dettaglio/E098-29810" target="_blank">codice E098-29810</a></p>
<p>• 
<strong>Addetto al confezionamento e alle spedizioni</strong>
<br/>Sede di lavoro: 
<strong>San Daniele del Friuli</strong>
<br/>Mansioni: confezionamento prodotti alimentari e preparazione commesse del reparto spedizioni
<br/>Contratto offerto: tempo determinato con possibilità di trasformazione in indeterminato
<br/>Scadenza offerta: 24 febbraio 2020
<br/>Codice offerta: 
<a href="http://bit.ly/2urtWOS" target="_blank">H816-29776</a></p> <div class="box-allegati">
<ul class="box-allegati-list">
<li><a href="https://offertelavoro.regione.fvg.it/lavoroFVG/ricerca" title="Vai al portale Lavoro FVG"><i class="fa fa-link"></i>Vai al portale Lavoro FVG</a>
<br/>Per tutte le offerte del settore, fai la ricerca usando il filtro "Settore attività" e scrivendo "Alimentari"</li>
</ul>
</div>
</div>'''

# soup = BeautifulSoup(s, 'html.parser')
#
#
# res = process_node(soup)
# print(res)
# exit(0)

url = "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/570.html"
url = "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/560.html"
url = "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/584.html"

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