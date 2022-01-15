from typing import List
from dataclasses import asdict
from copy import deepcopy
from datetime import datetime
import csv
from fuzzywuzzy import fuzz

from .Stores import Store, StoreTypes, Steam, G2A, GOG, Game
from .Filter import Filter, FilterNew, FilterStored


class GameStore:
    csv_fieldnames = list(Game.__annotations__.keys())
    date_format = "%d-%m-%Y"

    def __init__(self, filename="./storage.csv"):
        self.filename = filename
        self.storage = {}
        self.read_games()
        print(self.storage)

    def store_game(self, game: Game):
        with open(self.filename, "a") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self.csv_fieldnames
            )
            game = self.format_for_storage(game)
            self.storage.update({game.hash_id: game})
            writer.writerow(asdict(game))

    def read_games(self):
        with open(self.filename, "r") as csvfile:
            reader = csv.DictReader(
                csvfile,
                fieldnames=self.csv_fieldnames
            )

            self.storage = {
                int(game_dict["hash_id"]): self.extract_game(game_dict)
                for game_dict in reader
            }

    def extract_game(self, game_data: dict):
        game = Game(**game_data)
        game.fetch_date = datetime.strptime(game.fetch_date, self.date_format)
        game.release_date = datetime.strptime(
            game.release_date,
            self.date_format,
        )
        game.price = float(game.price)
        game.original_price = float(game.original_price)
        game.discount_percentage = float(game.discount_percentage)
        game.hash_id = int(game.hash_id)

        return game

    def is_stored(self, game: Game):
        return game.hash_id in self.storage

    def format_for_storage(self, game: Game):
        game = deepcopy(game)
        game.fetch_date = game.fetch_date.strftime(self.date_format)
        game.hash_id = self.get_hash_id(game)
        game.is_stored = True
        game.release_date = game.release_date.strftime(self.date_format)

        return game

    def get_hash_id(self, game: Game):
        return hash(f"{game.name} {game.fetch_date} {game.store}")



class GamesCollector:
    store_types_classes = {
        StoreTypes.steam: Steam(),
        StoreTypes.g2a: G2A(),
    }
    store = GameStore()

    def __init__(self):
        self.last_fetched = []
        self.last_filter = Filter(stores=[])

    def collect_games(self, filter_params: Filter):
        if isinstance(filter_params, FilterNew):
            return self.search_stores(filter_params)
        elif isinstance(filter_params, FilterStored):
            return self.get_stored(filter_params)

    def get_stored(self, filter_params: FilterStored):
        games = list(self.store.storage.values())
        return self.apply_filters(games, filter_params)

    def search_stores(self, filter_params: FilterNew):
        should_fetch = self.should_fetch(filter_params)
        self.last_filter = deepcopy(filter_params)

        if not should_fetch:
            return self.apply_filters(self.last_fetched)

        games = []
        for store_type in filter_params.stores:
            games += self.store_types_classes[store_type].get_games(filter_params.name)

        self.last_fetched = games

        return self.apply_filters(games)

    def should_fetch(self, filter_params: Filter):
        same_name = filter_params.name == self.last_filter.name
        new_stores = not all(
                        store in self.last_filter.stores
                        for store in filter_params.stores
                    )
        return (not same_name) or new_stores or (not self.last_fetched)

    def apply_filters(self, games: List[Game], filter_params=None):
        if not filter_params:
            filter_params = self.last_filter

        filter_methods = [
            self.price_filter,
            self.discount_filter,
            self.store_filter
        ]

        if isinstance(filter_params, FilterStored):
            filter_methods.append(self.name_filter)

        filtered_games = []
        for game in games:
            filter_stats = (
                f(game, filter_params)
                for f in filter_methods
            )

            if all(filter_stats):
                filtered_games.append(game)

        return filtered_games

    def price_filter(self, game, filter_params):
        price_from = filter_params.price_from
        price_to = filter_params.price_to

        if price_from and price_to:
            return price_from <= game.price <= price_to
        if price_from:
            return price_from <= game.price
        if price_to:
            return game.price <= price_to

        return True

    def discount_filter(self, game, filter_params):
        discount = filter_params.discount

        if discount is None:
            return True
        if discount is False:
            return True
        if discount is True:
            return game.discount_percentage > 0

    def store_filter(self, game, filter_params):
        return game.store in filter_params.stores

    def name_filter(self, game, filter_params):
        ratio = fuzz.ratio(filter_params.name, game.name)
        print(filter_params.name, game.name, ratio)
        return ratio > 30


