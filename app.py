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


def args(_args, *wanted):
    """
    Validates arguments.
    """
    return (_args.get(x, "").strip() for x in wanted)


@app.route("/")
def home():
    """index"""
    soup = bs4.BeautifulSoup(
        open("src/index.html", "r", encoding="utf-8").read(), "html.parser"
    )
    body = soup.find("body", recursive=True)
    for gid, game in games.items():
        if len(game["players"]) != 1 or game["ended"] or not any(game["players"]):
            continue
        join_game_div = soup.new_tag("div", id="join_game_div")
        join_game_div.append(f"Room Name: {game['name']}")
        join_game_div.append(
            soup.new_tag(
                "input",
                id="join_game_button",
                type="button",
                value="Join Room",
                onclick=f"location.href='/joinGame?game={gid}';",
            )
        )
        body.append(join_game_div)
    start_div = soup.new_tag("div", id="start_div")
    start_div.append(
        soup.new_tag(
            "input",
            id="new_game",
            type="button",
            value="New Game",
            onclick="location.href='/newGame';",
            attrs={"class": "start_button"},
        )
    )
    # start_div.append(
    #   soup.new_tag(
    #      "input",
    #     id="new_game",
    #    type="button",
    #   value="New Room",
    #  onclick="location.href='/newRoom';",
    # attrs={"class": "start_button"},
    # )
    # )
    body.append(start_div)
    return soup.prettify()


def meta(soup, game):
    """
    Adds meta tags.
    """
    for i, v in dict(
        game_id=game,
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
    games[game] = dict(
        name="",
        board={"a": ["", "", ""], "b": ["", "", ""], "c": ["", "", ""]},
        turn=random.choice((True, False)),
        players=[],
        ended=False,
        tie=False,
        ai_game=False,
    )
    soup = bs4.BeautifulSoup(
        open("src/game.html", "r", encoding="utf-8").read(), "html.parser"
    )
    name = soup.find("div", id="div_name", recursive=True)
    for i, n, a in [("one", "1", ", true"), ("two", "2", "")]:
        name.append(
            soup.new_tag(
                "input",
                id=i + "_player",
                type="submit",
                value=n + " Player",
                onclick=f"joinGame('{game}', "
                f"document.getElementById('input_name').value.trim().slice(0,100){a});",
            )
        )
    meta(soup, game)
    return soup.prettify()


@app.route("/joinGame")
def join_game():
    """
    Joins game.
    """
    (game,) = args(flask.request.args, "game")
    if not check_game(game)[0]:
        refresh("game_not_found")
    if game and (not games.get(game) or len(games.get(game).get("players", [])) >= 2):
        return refresh("game_not_found_or_full")
    soup = bs4.BeautifulSoup(
        open("src/game.html", "r", encoding="utf-8").read(), "html.parser"
    )
    soup.find("div", id="room_name", recursive=True).append(
        f"Room Name: {games[game]['name']}"
    )
    soup.find("div", id="join_opponent", recursive=True).append(
        f"Opponent: {games[game]['players'][0]}"
    )
    soup.find("div", id="div_name", recursive=True).append(
        soup.new_tag(
            "input",
            id="join_game",
            type="submit",
            value="Join Game",
            onclick=f"joinGame('{game}', "
            "document.getElementById('input_name').value.trim().slice(0,100));",
        )
    )
    meta(soup, game)
    return soup.prettify()


@app.route("/game")
def active_game():
    """Active game"""
    game, user = args(flask.request.args, "game", "user")
    if not check_game(game)[0]:
        return refresh("game_not_found")
    if games[game]["ended"]:
        return refresh("game_ended")
    if not (res := check_user(game, user))[0]:
        return refresh(
            "_".join(
                json.loads(res[1].response[0].decode())["message"].lower().split(" ")
            )
        )
    soup = bs4.BeautifulSoup(
        open("src/game.html", "r", encoding="utf-8").read(), "html.parser"
    )
    meta(soup, game)
    chnm = soup.find("div", id="change_name", recursive=True)
    chnm.append(
        soup.new_tag(
            "input",
            id="name_change_button",
            type="button",
            value="Change Username",
            onclick=f"changeName('{game}', '{user}');",
        )
    )
    chnm.append(
        soup.new_tag(
            "input",
            id="room_name_change_button",
            type="button",
            value="Change Room Name",
            onclick=f"changeRoomName('{game}');",
        )
    )
    s = soup.new_tag("script")
    s.append(f"runGame('{game}', '{user}');")
    soup.find("body").append(s)
    return soup.prettify()


@app.route("/setSpace")
def set_space():
    """
    Set space
    """
    game, user, space = args(flask.request.args, "game", "user", "space")
    if not (res := check_game(game))[0]:
        return res[1]
    if not (res := check_user(game, user))[0]:
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
    if game["ended"]:
        return flask.Response(
            json.dumps({"message": "Game is ended"}),
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
    game["board"][space[0]][int(space[1]) - 1] = "XO"[s]
    game["turn"] = not s
    game["ended"], game["tie"] = end_check(game["board"], "XO"[game["turn"] - 1])
    return flask.Response(
        json.dumps(
            {
                "move": "XO"[s],
                "ended": game["ended"],
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
    if not (res := check_user(game, user, True))[0]:
        return res[1]
    games[game]["players"].append(user)
    if not games[game]["name"]:
        games[game]["name"] = user
    if ai == "true":
        games[game]["ai_game"] = True
        games[game]["players"].append("AI")
    return flask.Response(
        json.dumps(
            {
                "message": f"Player {games[game]['players'].index(user)} added with name {user}"
            }
        ),
        status=200,
        mimetype="application/json",
    )


@app.route("/changeName")
def change_name():
    """
    Change player name
    """
    game, user, name = args(flask.request.args, "game", "user", "name")
    if not (res := check_game(game))[0]:
        return res[1]
    if not (res := check_user(game, user))[0]:
        return res[1]
    ps = games[game]["players"]
    i = ps.index(user)
    if ps[i - 1] == name:
        return flask.Response(
            json.dumps({"message": "Name already taken"}),
            status=400,
            mimetype="application/json",
        )
    ps[i] = name
    return flask.Response(
        json.dumps({"message": f"Player name changed from {user} to {name}"}),
        status=200,
        mimetype="application/json",
    )


@app.route("/changeRoomName")
def change_room_name():
    """
    Change player name
    """
    game, name = args(flask.request.args, "game", "name")
    if not (res := check_game(game))[0]:
        return res[1]
    ogname = games[game]["name"]
    if any(
        filter(lambda pair: pair[1]["name"] == name and pair[0] != game, games.items())
    ):
        return flask.Response(
            json.dumps({"message": "Room name already taken"}),
            status=400,
            mimetype="application/json",
        )
    games[game]["name"] = name
    return flask.Response(
        json.dumps({"message": f"Room name changed from {ogname} to {name}"}),
        status=200,
        mimetype="application/json",
    )


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
    if flask.request.args.get("pwd", None) == "pg_gs":
        while len(games) > 0:
            del games[list(games.keys())[0]]
        return flask.redirect("/")
    return refresh("invalid_purge_password")


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


def check_user(gameid, user, add=False):
    """
    Validates user existence.
    """
    if not user:
        return False, flask.Response(
            json.dumps({"message": "Username is required"}),
            status=400,
            mimetype="application/json",
        )
    if (user in games.get(gameid)["players"]) == add:
        return False, flask.Response(
            json.dumps(
                {"message": "User not in game" if not add else "User already in game"}
            ),
            status=400,
            mimetype="application/json",
        )
    return True, None


def refresh(err):
    """
    Wrapper for refresh meta tag.
    """
    return f"<meta http-equiv='Refresh' content=\"0; url='/?err_code={err}'\">"


@app.route("/about")
def about():
    """
    About page
    """
    return flask.send_file("src/about.html")


@app.route("/style.css")
def style():
    """style"""
    return flask.send_file("src/style.css")


@app.route("/functions.js")
def functions_js():
    """functions"""
    return flask.send_file("src/functions.js")


# app.run(port=7744, debug=True)
from waitress import serve
serve(app, port=7744)