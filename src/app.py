from flask import Flask, render_template, request
from datetime import datetime

from QuarkAPI.Quark import api, Game
from QuarkAPI.Controllers import FilterNew, StoreTypes, FilterStored

app = Flask(__name__, static_folder="./static", template_folder="./templates")
app.config["DEBUG"] = True


@app.route("/home", methods=["GET"])
def get_home():
    print(request.args)
    game_name = request.args.get("game_name") or "Witcher"


    filter = FilterNew(
        name=game_name,
        stores=[StoreTypes.steam]
    )

    games = api.get_games(filter)

    return render_template(
        "home.html",
        games=games[0:9],
    )


@app.route("/store", methods=["POST"])
def store_game():
    game_name = request.form.get("game_name") or "Witcher"

    game_for_storage = Game(
        name=game_name,
        dev="",
        price=0,
        original_price=0,
        discount_percentage=0,
        fetch_date=datetime.now(),
        store="Steam",
        image_url="",
        hash_id=12321313,
        release_date=datetime.now(),
        is_stored=True,
    )

    api.store_game(game_for_storage)

    return f"{game_name} was stored"


if __name__ == "__main__":
    app.run(host="localhost", port=3000)
