from dataclasses import dataclass
from enum import Enum
import logging
from typing import List
from urllib.parse import urljoin
from uuid import UUID
from bs4 import BeautifulSoup, PageElement, Tag
import requests
import re
from models import Ingredient

# PARSE_TARGET_URL = "https://sugarspunrun.com/creamy-potato-soup-recipe/" // LOL I think the website owner noticed the traffic caused by my crawler and locked it down
PARSE_TARGET_URL = "https://www.allrecipes.com/recipe/16678/slow-cooker-taco-soup/"

logger = logging.Logger(__name__, logging.INFO)

class Crawler:

    def __init__(self, urls: List[str]=[]):
        self.visited_urls = []
        self.urls_to_visit = urls
    
    def download_url(self, url):
        response = requests.get(url)
        if response.status_code == requests.codes["ok"]:
            with open("test.html", "w") as fp:
                fp.write(response.text)
            return response.text
        else:
            logger.warning(f'{response.status_code} - {response.reason}')
            return "" # TODO - Not sure about returning empty result
    
    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path
    
    def add_url_to_visit(self, url: str):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def __class_contains_ingredient(self, tag: Tag) -> bool:
        ingredients_pattern = re.compile("(ingredient)")
        if tag.has_attr('class'):
            class_names = " ".join(tag.attrs.get('class'))
            return (
                tag.parent.name == "ul" and 
                tag.name == "li" and 
                ingredients_pattern.search(class_names) != None
            )
        else:
            return False
        
    def __class_contains_name(self, tag: Tag) -> bool:
        name_pattern = re.compile("(name)")
        if tag.has_attr('class'):
            class_names = " ".join(tag.attrs.get('class'))
            return name_pattern.search(class_names) != None
        else:
            return False

    def __class_contains_amount(self, tag: Tag) -> bool:
        amount_pattern = re.compile("(amount|quantity)")
        if tag.has_attr('class'):
            class_names = " ".join(tag.attrs.get('class'))
            return amount_pattern.search(class_names) != None
        else:
            return False

    def __class_contains_unit(self, tag: Tag) -> bool:
        unit_pattern = re.compile("(unit|measurement)")
        if tag.has_attr('class'):
            class_names = " ".join(tag.attrs.get('class'))
            return unit_pattern.search(class_names) != None
        else:
            return False

    def __extract_ingredients(self, tag: Tag):
        # logger.debug(tag)
        ingredient_data = tag.find_all("span")
        # TODO - I don't trust this approach, since it only works if allrecipes.com has it standardized and we are only crawling that domain
        ingredient = Ingredient(
            amount=ingredient_data[0].contents.pop(),
            uom=ingredient_data[1].contents.pop() if ingredient_data[1].contents else "",
            name=ingredient_data[2].contents.pop()
            )
        return ingredient

    def find_ingredients(self, soup: BeautifulSoup):
        ingredients = []
        for result in soup.find_all(self.__class_contains_ingredient):
            ingredients.append(self.__extract_ingredients(result))

    def crawl(self, url):
        # html = self.download_url(url) # TODO - Not trying to lose access to another site, so dev will be done on static file
        # soup = BeautifulSoup(html, 'html.parser')
        # self.find_ingredients(soup)
        with open("test.html", "r") as fp:
            html = fp.read()
            soup = BeautifulSoup(html, 'html.parser')
            self.find_ingredients(soup)
        for url in self.get_linked_urls(url, html):
            # self.add_url_to_visit(url)
            print(url)
            pass

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logger.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except Exception:
                logger.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)

    def find_recipe(self):
        pass 
            
# req = requests.get(PARSE_TARGET_URL, stream=True)

if __name__ == "__main__":
    Crawler(urls=[PARSE_TARGET_URL]).run()