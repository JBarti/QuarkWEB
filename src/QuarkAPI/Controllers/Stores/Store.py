from urllib.parse import urlencode
import requests


class StoreTypes:
    steam = "Steam"
    g2a = "G2A"
    gog = "GOG"


class Store:
    def __init__(self, url_base: str, custom_headers: dict):
        self.url_base = url_base
        self.custom_headers = custom_headers

    def get_games(self, search_pattern: str):
        return []

    def build_url(self, url_params: dict):
        str_params = urlencode(url_params)
        return f"{self.url_base}?{str_params}"

    def fetch_raw_data(self, url_params: dict):
        url = self.build_url(url_params)

        resp = requests.get(
            url=url,
            headers=self.custom_headers,
        )

        return resp.text

    @staticmethod
    def calculate_discount(original_price: int, price: int):
        if original_price == 0:
            return 0
        discount_percentage = (original_price - price) / original_price
        discount_percentage = round(discount_percentage, 2) * 100

        return discount_percentage
