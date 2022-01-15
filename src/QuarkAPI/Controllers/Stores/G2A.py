import json
import requests
from urllib.parse import urlencode
from datetime import datetime

from .Store import Store
from .Game import Game
from .Store import StoreTypes


class G2A(Store):
    URL_BASE = "https://www.g2a.com/new/api/v3/products/filter"

    CUSTOM_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Host": "www.g2a.com",
        "Origin": "https://www.g2a.com",
        "Referer": "https://www.g2a.com/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "if-none-match": 'W/"9d3-vtNfK63G7ERz4Ayz1z6ErA"',
    }

    def __init__(self):
        super().__init__(G2A.URL_BASE, G2A.CUSTOM_HEADERS)

    def get_games(self, search_pattern: str):
        url_params = {
            "currency": "EUR",
            "query": search_pattern,
            "store": "english",
            "wholesale": "false",
        }
        data = self.fetch_raw_data(url_params)
        json_data = json.loads(data)
        return self.parse_response(json_data)

    def parse_response(self, json_data: dict):
        return [self.product_to_game(product) for product in json_data["products"]]

    def product_to_game(self, product: dict):
        original_price, price = self.get_prices(product)

        return Game(
            name=product.get("name"),
            dev="Unknown",
            price=price,
            original_price=original_price,
            discount_percentage=self.calculate_discount(original_price, price),
            fetch_date=datetime.now(),
            image_url=product.get("image", {}).get("sources")[0].get("url"),
            release_date=self.get_release_date(product),
            store=StoreTypes.g2a,
        )

    def get_release_date(self, product: dict):
        release_date_str = product.get("releaseDate")
        if not release_date_str:
            return None

        date_formats = ["%Y-%m-%d", "%Y-%m"]
        for fmt in date_formats:
            try:
                return datetime.strptime(release_date_str, "%Y-%m-%d")
            except Exception:
                print(f"Unable to read date {release_date_str}") 

    def get_prices(self, product: dict):
        original_price = (product.get("discount") or {}).get("suggestedPrice")
        price = product.get("minPrice")
        if not original_price:
            original_price = price

        return float(original_price or 0), float(price or 0)
