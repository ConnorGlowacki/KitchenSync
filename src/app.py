import logging
from service.crawler import Crawler

PARSE_TARGET_URL = "https://www.allrecipes.com/recipe/16678/slow-cooker-taco-soup/"

logger = logging.Logger(__name__, logging.INFO)

if __name__ == "__main__":
    Crawler(urls=[PARSE_TARGET_URL]).run()