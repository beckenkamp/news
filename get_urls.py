import requests
from bs4 import BeautifulSoup

def get_urls():
    url_news = []

    r = requests.get('http://exame.abril.com.br/topicos/startups/')

    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')

    links = soup.find_all('a', attrs={'class': 'featured-content-image'}, href=True)
    for link in links:
        if not link['href'] in url_news:
            url_news.append('http://exame.abril.com.br{}'.format(link['href']))


    r = requests.get('http://revistapegn.globo.com/Startups/index.html')

    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')

    links = soup.find_all('div', attrs={'class': 'materia__item'})
    for link in links:
        for l in link.find_all(href=True):
            if not 'javascript:void(0);' in l['href']:
                if not l['href'] in url_news:
                    url_news.append(l['href'])


    r =  requests.get('http://startse.infomoney.com.br/portal/ultimas/')

    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')

    links = soup.find_all('a', attrs={'class': 'image-link'}, href=True)
    for link in links:
        if not link['href'] in url_news:
            url_news.append(link['href'])


    r = requests.get('http://startupi.com.br/categoria/materias/')

    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')

    links = soup.find_all('h3', attrs={'class': 'post-title'})
    for link in links:
        for l in link.find_all(href=True):
            if not 'javascript:void(0);' in l['href']:
                if not l['href'] in url_news:
                    url_news.append(l['href'])

    return url_news