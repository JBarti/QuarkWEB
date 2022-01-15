from bs4 import BeautifulSoup, Tag
from datetime import datetime

from .Game import Game
from .Store import Store, StoreTypes


class Steam(Store):
    URL_BASE = "https://store.steampowered.com/search/results"

    CUSTOM_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Host": "store.steampowered.com",
        "Referer": "https://store.steampowered.com/news/",
    }

    def __init__(self):
        super().__init__(Steam.URL_BASE, Steam.CUSTOM_HEADERS)

    def get_games(self, search_pattern: str):
        url_params = {
            "start": 0,
            "count": 50,
            "sort_by": "_ASC",
            "term": search_pattern,
            "inifinite": 1,
        }

        data = self.fetch_raw_data(url_params)
        bs_parse = BeautifulSoup(data, "html.parser")
        return self.parse_html(bs_parse)

    def parse_html(self, bs_parse: BeautifulSoup):
        products = bs_parse.find_all(
            "a",
            attrs={"class": "search_result_row"},
        )

        return [self.parse_product_data(product) for product in products]

    def parse_product_data(self, product: Tag):
        original_price, price = self.parse_prices(product)

        return Game(
            name=product.find("span", "title").text,
            dev="Unknown",
            original_price=original_price,
            price=price,
            discount_percentage=self.calculate_discount(original_price, price),
            release_date=self.parse_product_release_date(product),
            fetch_date=datetime.now(),
            image_url=product.find("img")["src"],
            store=StoreTypes.steam,
        )

    def parse_product_release_date(self, product: Tag):
        release_date = product.find("div", "search_released").text
        try:
            return datetime.strptime(release_date, "%d %b, %Y")
        except:
            return None

    def parse_prices(self, product: Tag):
        original_price_tag = product.find("strike")
        price = self.parse_current_price(product, original_price_tag)

        if original_price_tag:
            original_price = self.normalize_price_str(original_price_tag.text)
        else:
            original_price = price

        return original_price, price

    def parse_current_price(self, product: Tag, original_price_tag: Tag):
        if original_price_tag:
            price_str = original_price_tag.parent.next_sibling.next_sibling
        else:
            price_str = product.find("div", "search_price").text
            try:
                return self.normalize_price_str(price_str)
            except ValueError:
                return 0

        return self.normalize_price_str(price_str)

    @staticmethod
    def normalize_price_str(price: str):
        return float(price.replace(",", ".").split("€")[0])
        


