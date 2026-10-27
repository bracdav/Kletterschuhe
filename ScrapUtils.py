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

    def SelectLink(self, index):
        r = requests.get(self.links[index])
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup

    def getFirst(self):
        extractedInformation = self.ExtractProductInformation(0)
        extractedSizes = self.getSizes(0)
        key = list(extractedSizes.keys())[0]
        extractedInformation[key] = extractedSizes[key] 

        return extractedInformation

    def getSizes(self, index):
        soup = self.SelectLink(index)
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
    
        return {'availableSizes' : available_sizes}

    def ExtractProductInformation(self, index):
        soup = self.SelectLink(index)
        features_dict = {}

        for feature_div in soup.find_all('div', class_='product-features__feature'):
            name_div = feature_div.find('div', class_='product-features__feature-name')
            
            if name_div:
                key = name_div.get_text(strip=True)
                values = []
                
                list_items = feature_div.find_all('li', class_='product-features__list-item')
                if list_items:
                    values = [li.get_text(strip=True) for li in list_items]
                    
                else:
                    text_div = feature_div.find('div', class_='product-features__text')
                    if text_div:
                        values = [text_div.get_text(strip=True)]  # Wrap in a list for consistency
                        
                # 4. Save to dictionary
                features_dict[key] = values

        return features_dict




class ScrapExecutor:
    def execute(self, objectToScrap, baseurl, class_ = None):
        if (isinstance(objectToScrap, str)):
            self.objectToScrap = ProductLinks(baseurl, class_)
            self.objectToScrap.execute(objectToScrap)
            return self.objectToScrap.Links
        elif (isinstance(objectToScrap, list)):
            self.objectToScrap = ProductDetails(objectToScrap)
            return self.objectToScrap.getFirst()
        return 'Object type not implemented'