"""
Main app file
"""
# pylint: disable=invalid-name
import json
import random
import re
import uuid
import bs4
import flask
from checks_gets import end_check

app = flask.Flask(__name__)

games = {}
x = "XO"


def args(_args, *wanted):
    """
    Validates arguments.
    """
    return (_args.get(x, None).strip() for x in wanted)


@app.route("/")
def home():
    """index"""
    soup = bs4.BeautifulSoup(
        open("index.html", "r", encoding="utf-8").read(), "html.parser"
    )
    body = soup.new_tag("body")
    for gid, game in games.items():
        if len(game["players"]) != 1 or game["ended"][0] or not any(game["players"]):
            continue
        join_game_div = soup.new_tag("div", id="join_game_div")
        join_game_div.append(f"Player: {game['players'][0]}")
        join_game_div.append(
            soup.new_tag(
                "input",
                id="join_game_button",
                type="button",
                value="Join Game",
                onclick=f"location.href='/joinGame?game={gid}';",
            )
        )
        body.append(join_game_div)
    start_new = soup.new_tag(
        "input",
        id="start_new",
        type="button",
        value="Start New",
        onclick="location.href='/newGame';",
    )
    body.append(start_new)
    soup.find("html").append(body)
    return soup.prettify()


def meta(soup, game, num):
    for i, v in dict(
        game_id=game,
        #        player_num=num,
        player_name="",
        opponent_name="",
    ).items():
        soup.find("head").append(soup.new_tag("meta", id=i, content=v))


@app.route("/newGame")
def new_game():
    """
    Creates new game.
    """
    game = uuid.uuid1().hex
    games[game] = {
        "board": {"a": ["", "", ""], "b": ["", "", ""], "c": ["", "", ""]},
        "turn": random.choice((True, False)),
        "players": [],
        "ended": (False, False),
        "ai_game": False,
    }
    soup = bs4.BeautifulSoup(
        open("game.html", "r", encoding="utf-8").read(), "html.parser"
    )
    name = soup.find("div", id="div_name", recursive=True)
    for i, n, a in [("one", "1", ", true"), ("two", "2", "")]:
        name.append(
            soup.new_tag(
                "input",
                id=i + "_player",
                type="submit",
                value=n + " Player",
                onclick=f"addPlayer('{game}', document.getElementById('input_name').value.trim().slice(0,100){a});",
            )
        )
    meta(soup, game, 1)
    return soup.prettify()


@app.route("/joinGame")
def join_game():
    """
    Joins game.
    """
    game, = args(flask.request.args, "game")
    if not (res := check_game(game))[0]:
        return res
    if game and (not games.get(game) or len(games.get(game).get("players", [])) >= 2):
        return refresh("game_not_found_or_full")
    soup = bs4.BeautifulSoup(
        open("game.html", "r", encoding="utf-8").read(), "html.parser"
    )
    name = soup.find("div", id="div_name", recursive=True)
    name.append(
        soup.new_tag(
            "input",
            id="join_game",
            type="submit",
            value="Join Game",
            onclick=f"addPlayer('{game}', document.getElementById('input_name').value.trim().slice(0,100));",
        )
    )
    od = soup.find("div", id="div_opponent", recursive=True)
    if n := games.get(game, {}).get("players", [""])[0]:
        od.append(f"Opponent: {n}")
    meta(soup, game, 2)
    return soup.prettify()


@app.route("/game")
def active_game():
    """Active game"""
    game, user, ai = args(flask.request.args, "game", "user", "ai")
    soup = bs4.BeautifulSoup(
        open("game.html", "r", encoding="utf-8").read(), "html.parser"
    )
    meta(soup, game, games[game]["players"].index(user) + 1)
    s = soup.new_tag("script")
    s.append(f"runGame('{game}', '{user}', '{ai=='true'}');")
    soup.find("body").append(s)
    return soup.prettify()
    # body = soup.find("body")
    # body.append(
    #    soup.new_tag(
    #        "input",
    #        type="button",
    #        value="Share",
    #        id="share_button",
    #        onclick=f"share('{game}');",
    #    )
    # )
    # return soup.prettify()


@app.route("/setSpace")
def set_space():
    """
    Set space
    """
    game, user, space = args(flask.request.args, "game", "user", "space")
    if not (res := check_game(game))[0]:
        return res[1]
    if not (res := check_user(user))[0]:
        return res[1]
    if not space:
        return flask.Response(
            json.dumps({"message": "Space ID is required"}),
            status=400,
            mimetype="application/json",
        )
    space = space.lower()
    if not re.match("[abc][123]", space):
        return flask.Response(
            json.dumps({"message": "Invalid space ID - must be `a1` to `c3`"}),
            status=400,
            mimetype="application/json",
        )
    game = games.get(game)
    if game["ended"][0]:
        return flask.Response(
            json.dumps({"message": "Game ended"}),
            status=400,
            mimetype="application/json",
        )
    s = game["turn"]
    if s and len(game["players"]) < 2 and not game["ai_game"]:
        return flask.Response(
            json.dumps({"message": "Waiting for player 2..."}),
            status=400,
            mimetype="application/json",
        )
    if int(s) != game["players"].index(user):
        return flask.Response(
            json.dumps({"message": "Not your turn"}),
            status=400,
            mimetype="application/json",
        )
    if game["board"][space[0]][int(space[1]) - 1]:
        return flask.Response(
            json.dumps({"message": "Space already taken"}),
            status=400,
            mimetype="application/json",
        )
    game["board"][space[0]][int(space[1]) - 1] = x[s]
    game["turn"] = not s
    game["ended"] = end_check(game["board"], x[game["turn"] - 1])
    return flask.Response(
        json.dumps(
            {
                "move": x[s],
                "ended": game["ended"][0],
                "tie": game["ended"][1],
                "player": game["players"][s],
            }
        ),
        status=200,
        mimetype="application/json",
    )


@app.route("/addPlayer")
def add_player():
    """
    Add player
    """
    game, user, ai = args(flask.request.args, "game", "user", "ai")
    if not (res := check_game(game))[0]:
        return res[1]
    if user in games[game]["players"]:
        return flask.Response(
            json.dumps({"message": "Player already exists"}),
            status=400,
            mimetype="application/json",
        )
    # games[game]["players"][int(player_num) - 1] = user
    games[game]["players"].append(user)
    if ai == "true":
        games[game]["ai_game"] = True
        games[game]["players"].append("__AI__")
    return flask.Response(
        json.dumps({"message": "Player set"}), status=200, mimetype="application/json"
    )


# @app.route("/checkWin")
# def check_win():
#    """
#    Check win
#    """
#    game, user = args(flask.request.args, "game", "user")
#    if not (res := check_game(game))[0]:
#        return res[1]
#    if not (res := check_user(user))[0]:
#        return res[1]
#    game = games[game]
#    print(game["board"])
#    return flask.Response(
#        json.dumps(
#            {
#                "won": end_check(game["board"], x[game["turn"]])[0],
#                "message": game["players"][game["turn"]],
#            }
#        ),
#        status=200,
#        mimetype="application/json",
#    )


@app.route("/getBoard")
def get_board():
    """
    Get board
    """
    (game,) = args(flask.request.args, "game")
    if not (res := check_game(game))[0]:
        return res[1]
    game = games[game]
    return flask.Response(
        json.dumps(game["board"]), status=200, mimetype="application/json"
    )


@app.route("/getGame")
def get_game():
    """
    Get game
    """
    (game,) = args(flask.request.args, "game")
    if not (res := check_game(game))[0]:
        return res[1]
    game = games[game]
    return flask.Response(json.dumps(game), status=200, mimetype="application/json")


@app.route("/purgeGames")
def purge_games():
    """
    Purge games
    """
    while len(games) > 0:
        del games[list(games.keys())[0]]
    return flask.redirect("/")


@app.errorhandler(404)
def not_found(details):  # pylint: disable=unused-argument
    """404 page"""
    return refresh("not_found")


def check_game(game):
    """
    Validates game ID input.
    """
    if not game:
        return False, flask.Response(
            json.dumps({"message": "No game specified"}),
            status=400,
            mimetype="application/json",
        )
    if not games.get(game):
        return False, flask.Response(
            json.dumps({"message": "Game does not exist"}),
            status=404,
            mimetype="application/json",
        )
    return True, None


def check_user(user):
    """
    Validates user existence.
    """
    if not user:
        return False, flask.Response(
            json.dumps({"message": "Username is required"}),
            status=400,
            mimetype="application/json",
        )
    return True, None


def refresh(err):
    return f"<meta http-equiv='Refresh' content=\"0; url='/?err_code={err}'\">"


@app.route("/style.css")
def style():
    """style"""
    return flask.send_file("style.css")


@app.route("/functions.js")
def functions_js():
    """functions"""
    return flask.send_file("functions.js")


app.run(port=7744, debug=True)
