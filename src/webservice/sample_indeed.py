import urllib.request
from bs4 import BeautifulSoup

# URL = "https://www.indeed.com/jobs?q=data+scientist+%2420%2C000&l=New+York&start=10"

URL = "https://it.indeed.com/offerte-lavoro?q=software&l=Friuli-Venezia+Giulia"


soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')

results = soup.find_all('div', attrs={'data-tn-component': 'organicJob'})

for x in results:

    # print(x)
    details_page_link = None

    company = x.find('span', attrs={"class":"company"})
    if company:
        print('******************* company:', company.text.strip() )

    job = x.find('a', attrs={'data-tn-element': "jobTitle"})
    if job:
        print('******************* job:', job.text.strip())
        details_page_link = job.attrs['href']
        print('link to page: ' + str(details_page_link))

    summary = x.find('div', attrs={"class":"summary"})
    if summary:
        print("summary: ", summary.text.strip())

    source = x.find('span', attrs={"class":"result-link-source"})
    if source:
        print("source: ", source.text.strip())

    location = x.find('span', attrs={"class":"location"})
    if location:
        print("location: ", location.text.strip())

    salary = x.find('nobr')
    if salary:
        print('******************* salary:', salary.text.strip())

    link2 = 'https://it.indeed.com/rc/clk?jk=4fec53066fe76158&fccid=e1ba2fcebdda8535&vjs=3'
    if details_page_link:
        details_page_link = 'https://it.indeed.com' + details_page_link

        soup2 = BeautifulSoup(urllib.request.urlopen(details_page_link).read(), 'html.parser')

        job_description_full = soup2.find('div',  attrs={"class":"jobsearch-jobDescriptionText"}) # jobDescriptionText

        if job_description_full:
            print("JOB DESCRIPTION FULL: " + job_description_full.text.strip())




    print ('----------\n\n\n')