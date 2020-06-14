from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm import tqdm

def get_soup(url):
    return BeautifulSoup(requests.get(url).content, 'lxml')

def get_links(url, i=0, pages=0):
    soup = get_soup(url)
    
    # takes the number of total pages to report
    
    if i == 0:
        pages = int(soup.findAll('a', {'class': 'block br3 brc8 large tdnone lheight24'})[-1].text.strip())

    # looks for a container with all the needed data
    
    for item in soup.findAll('tr', {'class': 'wrap'}):
        
        # scrapes name, link, number of reviews, cooking and rating
        
        link = item.td.div.table.tbody.tr.td.a['href']
                   
        links.append(link)
        
        if DEBUG:
            print('Link: ', link)
    
    # we look for the next page, if it is not present we just save list to csv

                    
    if i == pages:
        df = pd.DataFrame(links, columns=['Link'])
        df.to_csv('apartments.csv', index=False)
        
    else:
        i += 1
        print(f'{i}/{pages}')
        nextPageUrl = f'&page={i+1}'
        nextPageUrl = base_url + nextPageUrl
        
        if DEBUG:
            print('Next page: ', nextPageUrl)
            
        get_links(nextPageUrl, i, pages)

        
    
def get_offers(url):
    soup = get_soup(url)
    
    if 'www.olx.pl' in url:
        container = soup.find('div', {'class': 'offerdescription clr'})
        
        # scrapes reviews one by one, etracting rating and review text itself
        data = {}
        data['Url'] = url
        data['Oferta'] = container.h1.text.strip().replace(',', '.')
        data['Cena'] = container.find('div', {'class': 'pricelabel'}).text.strip().split('\n')[0])
        features = container.findAll('li', {'class': 'offer-details__item'})
        for feature in features:
            key, value = feature.text.strip().split('\n')
            data[key] = value
               
        offers.append(data)  
            
        if DEBUG:
            print(data)
    else:
        # scrapes reviews one by one, etracting rating and review text itself
        data = {}
        data['Url'] = url
        data['Oferta'] = soup.find('div', {'class': 'css-d2oo9m'}).h1.text.strip().replace(',', '.')
        data['Cena'] = soup.find('div', {'class': 'css-1vr19r7'}).text.strip().split('/')[0].strip().split('\n')[0])
        features = soup.find('div', {'class': 'css-1ci0qpi'}).findChildren()
        for i,feature in enumerate(features):
            if i%2 != 0:
                key, value = feature.text.strip().split(':')
                data[key] = value
               
        offers.append(data)  
            
        if DEBUG:
            print(data)
        
            

# set scraped website, debug state and ranks dictionary          
DEBUG = True
base_url = 'https://www.olx.pl/nieruchomosci/mieszkania/wynajem/lodz/?search%5Bfilter_enum_builttype%5D%5B0%5D=blok'
links = []
offers = []

# scrape restaurants
get_links(base_url)

# read csv with restaurants and scrape reviews of each one
df = pd.read_csv('apartments.csv')

for url in tqdm(df.Link):
    get_offers(url)
    
df = pd.DataFrame(offers)
df.to_csv('offers.csv')


