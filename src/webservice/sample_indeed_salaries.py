import urllib.request
from bs4 import BeautifulSoup


URL = "https://it.indeed.com/salaries/ESTETISTA%20QUALIFICATA"

# URL = "https://it.indeed.com/salaries/estetista-Salaries"
# https://it.indeed.com/jobs?q=%23categorieprotette&l=Friuli-Venezia+Giulia&from=disabilityfilter

URL = "https://it.indeed.com/salaries/sviluppatore%20software-Salaries"
URL = "https://it.indeed.com/salaries/svilupatore%20software-Salaries"


soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')

# print(soup)

# results = soup.find_all('strong', attrs={'class': 'cmp-salary-amount'})
#
# counter = 0
# sum_total = 0
#
# for item in results:
#     value = item.text.strip()
#     print(value)
#
#     # float_value = float(value[1:].replace(".", "").replace(",", "."))
#     # # print(float_value)
#     # sum_total += float_value
#     # counter += 1
#
# # print("average:")
# # print(sum_total / counter)

not_enough_data = False

print("*****")

results = soup.find_all('div', attrs={'class': 'cmp-not-enough-data-box'})

for item in results:
    if "Spiacenti, non abbiamo abbastanza informazioni sugli stipendi" in item.text.strip():
        not_enough_data = True

if not_enough_data:
    print("***not_enough_data***")

print("*****")

results = soup.find_all('div', attrs={'class': 'cmp-sal-salary'})

for item in results:
    value = item.text.strip()
    print(value)

print("*****")

results = soup.find_all('div', attrs={'class': 'cmp-sal-summary'})

for item in results:
    value = item.text.strip()
    print(value)


"""

<div class="cmp-sal-salary"><strong class="cmp-salary-amount">€846</strong> al mese</div>

   <td class="cmp-sal-summary-col">
      <div class="cmp-sal-summary"><strong class="cmp-salary-amount">€4.000</strong> al mese</div>
   </td>
   


<div class="cmp-not-enough-data-box">
   <div>
      <div class="text">
         <div class="caption">Spiacenti, non abbiamo abbastanza informazioni sugli stipendi per svilupatore software.</div>
         <div class="content">Di seguito trovi alcune informazioni sullo stipendio per altri lavori simili:</div>
      </div>
   </div>
</div>

   

https://it.indeed.com/salaries/estetista-Salaries


<div id="cmp-salary-panel-yearly" class="cmp-salary-info-panel active">
   <div class="cmp-sal-summary cmp-float-left">
      <div class="cmp-sal-summary-caption">Stipendio medio</div>
      <div class="cmp-sal-salary"><strong class="cmp-salary-amount">€846</strong> al mese</div>
   </div>
   <div class="cmp-sal-distribution">
      <ul>
         <li style="height:55.35512931526015%; width:9.2%; left:0.0%;"></li>
         <li style="height:90.0%; width:9.2%; left:10.088999999999999%;" class="cmp-sal-highlight"><span><i></i>Il più frequente</span></li>
         <li style="height:75.36946712684168%; width:9.2%; left:20.177999999999997%;"></li>
         <li style="height:55.50820470259225%; width:9.2%; left:30.266999999999996%;"></li>
         <li style="height:39.79287124360059%; width:9.2%; left:40.355999999999995%;"></li>
         <li style="height:28.55908789093361%; width:9.2%; left:50.44499999999999%;"></li>
         <li style="height:20.70640494367392%; width:9.2%; left:60.53399999999999%;"></li>
         <li style="height:15.208907250952588%; width:9.2%; left:70.62299999999999%;"></li>
         <li style="height:11.32207643430026%; width:9.2%; left:80.71199999999999%;"></li>
         <li style="height:8.53882984370451%; width:9.2%; left:90.80099999999999%;"></li>
      </ul>
      <div class="cmp-sal-min cmp-sal-caption cmp-float-left">
         <div></div>
         <span>€76,55</span>
      </div>
      <div class="cmp-sal-max cmp-sal-caption cmp-float-right">
         <div></div>
         <span>€2.700</span>
      </div>
      <div class="cmp-sal-center cmp-sal-caption"><span>Distribuzione dello stipendio</span></div>
   </div>
</div>




<tr class="cmp-salary-aggregate-table-entry" data-tn-component="salary-entry[]">
   <td class="cmp-sal-description-col">
      <div class="cmp-sal-description">
         <div class="cmp-sal-desc-wrapper">
            <div class="cmp-sal-title">
               <a data-tn-link="" data-tn-element="title-cmp-salaries" href="/salaries/estetista-Salaries-at-Skin3">
                  <div class="cmp-sal-company-logo-wrapper">
                     <div class="cmp-sal-company-logo"><img src="/cmp/_s/s/3762eb2/blank_company.gif" alt="Company Logo"></div>
                  </div>
                  <span>Estetista - SKIN3</span>
               </a>
            </div>
            <div class="cmp-sal-note">7 stipendi</div>
         </div>
      </div>
   </td>
   <td class="cmp-sal-summary-col">
      <div class="cmp-sal-summary"><strong class="cmp-salary-amount">€4.000</strong> al mese</div>
   </td>
</tr>


"""