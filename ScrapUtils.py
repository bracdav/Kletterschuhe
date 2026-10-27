import requests
from bs4 import BeautifulSoup
import json5
import re

class ProductLinks:

    def __init__(self, baseurl, class_):
        self.baseurl = baseurl
        self.class_ = class_
        self.productLinkList = []
        self.Links = []

    def execute(self, linkToScrap):
            r = requests.get(linkToScrap)
            soup = BeautifulSoup(r.content, 'html.parser')
            product_list = soup.find_all('div', class_='products-list-page-preloader__links')
            
            for item in product_list:
                for link in item.find_all('a', href = True):
                    self.Links.append(self.baseurl + link['href'])


class ProductDetails:
    def __init__(self, links):
        self.links = links

    def getFirst(self):
        first = self.links[0]
        r = requests.get(first)
        soup = BeautifulSoup(r.content, 'html.parser')
        res = soup.find_all('script', id = 'global')
        print(res)
        #details = soup.find_all('div', class_ = 'size-select-tiles__tile')
        #with open("xml.txt", "w", encoding="utf-8") as file:
        #    file.write(soup.prettify())

    def getSizes(self):
        first = self.links[0]
        r = requests.get(first)
        soup = BeautifulSoup(r.content, 'html.parser')

        script_tag = soup.find('script', string=lambda t: t and '__initialAppState' in t)

        if not script_tag:
            raise ValueError("Could not find script tag with __initialAppState")
            
        script_text = script_tag.string
        _, json_like_str = script_text.split('window.__initialAppState =', 1)
        json_like_str = json_like_str.strip().rstrip(';')
        json_like_str = re.sub(r'JSON\.parse\s*\("[^"]*(?:\\.[^"]*)*"\)', 'null', json_like_str, flags=re.DOTALL)
        app_state = json5.loads(json_like_str)

        product_data = app_state['modules']['productPage']['productData']['productDetails']['product']['variations'][1]['options']

        available_sizes = []
        for product in product_data:
            available_sizes.append(product['value'].replace('EU ', ''))
    
        return available_sizes




class ScrapExecutor:
    def execute(self, objectToScrap, baseurl, class_ = None):
        if (isinstance(objectToScrap, str)):
            self.objectToScrap = ProductLinks(baseurl, class_)
            self.objectToScrap.execute(objectToScrap)
            return self.objectToScrap.Links
        elif (isinstance(objectToScrap, list)):
            self.objectToScrap = ProductDetails(objectToScrap)
            return self.objectToScrap.getSizes()
        return 'Object type not implemented'