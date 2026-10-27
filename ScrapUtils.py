import requests
from bs4 import BeautifulSoup


class ProductLinks:

    def __init__(self, baseurl, class_):
        self.baseurl = baseurl
        self.class_ = class_
        self.productLinkList = []
        self.Links = []

    def execute(self, linkToScrap):
            r = requests.get(linkToScrap)
            soup = BeautifulSoup(r.content, 'lxml')
            product_list = soup.find_all('div', class_='products-list-page-preloader__links')
            
            for item in product_list:
                for link in item.find_all('a', href = True):
                    self.Links.append(self.baseurl + link['href'])


class ProductDetails:
    def __init__(self, links):
        self.links = links

    def getFirst(self):
        pass