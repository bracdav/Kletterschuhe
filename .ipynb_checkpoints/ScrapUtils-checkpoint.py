from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json5
import re

class ProductLinks:
    def __init__(self, baseurl, class_):
        self.baseurl = baseurl
        self.class_ = class_
        self.Links = []

    def execute(self, linkToScrap):
        r = requests.get(linkToScrap)
        soup = BeautifulSoup(r.content, 'html.parser')
        product_list = soup.find_all('div', class_=self.class_)
        
        for item in product_list:
            for link in item.find_all('a', href=True):
                self.Links.append(self.baseurl + link['href'])


class ProductDetails:
    def __init__(self, links):
        self.links = links

    def _scrape_single_link(self, link):
        """Helper method to scrape a single product page safely in its own thread."""
        try:
            r = requests.get(link)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Find page state
            script_tag = soup.find('script', string=lambda t: t and '__initialAppState' in t)
            if not script_tag:
                return None
                
            script_text = script_tag.string
            _, json_like_str = script_text.split('window.__initialAppState =', 1)
            json_like_str = json_like_str.strip().rstrip(';')
            json_like_str = re.sub(r'JSON\.parse\s*\("[^"]*(?:\\.[^"]*)*"\)', 'null', json_like_str, flags=re.DOTALL)
            page_state = json5.loads(json_like_str)

            # Extract Sizes
            product_data = page_state['modules']['productPage']['productData']['productDetails']['product']['variations'][1]['options']
            available_sizes = [product['value'].replace('EU ', '') for product in product_data]
            sizes = {'availableSizes': available_sizes}

            # Extract Descriptions
            descriptions = {
                'shortDescription': BeautifulSoup(page_state['global']['schemaOrg'][0]['description'], 'html.parser').get_text(),
                'longDescription': BeautifulSoup(page_state['modules']['productPage']['productData']['longDescription'], 'html.parser').get_text()
            }

            # Extract Features
            features_dict = {}
            for feature_div in soup.find_all('div', class_='product-features__feature'):
                name_div = feature_div.find('div', class_='product-features__feature-name')
                if name_div:
                    key = name_div.get_text(strip=True)
                    list_items = feature_div.find_all('li', class_='product-features__list-item')
                    if list_items:
                        values = [li.get_text(strip=True) for li in list_items]
                    else:
                        text_div = feature_div.find('div', class_='product-features__text')
                        values = [text_div.get_text(strip=True)] if text_div else []
                    features_dict[key] = values

            # Merge all dictionaries
            merged = {**descriptions, **sizes, **features_dict}
            return merged
        except Exception as e:
            print(f"Error scraping {link}: {e}")
            return None

    def execute(self, max_workers = 10):
        # Use ThreadPoolExecutor to run requests in parallel (e.g., 10 concurrent workers)
        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(executor.map(self._scrape_single_link, self.links))
        
        # Filter out any failed requests (None)
        return [res for res in results if res is not None]


class ScrapExecutor:
    def execute(self, objectToScrap, baseurl, class_ = None, max_workers = 10):
        if isinstance(objectToScrap, str):
            self.objectToScrap = ProductLinks(baseurl, class_)
            self.objectToScrap.execute(objectToScrap)
            return self.objectToScrap.Links
        elif isinstance(objectToScrap, list):
            self.objectToScrap = ProductDetails(objectToScrap)
            return self.objectToScrap.execute(max_workers = max_workers)
        return 'Object type not implemented'