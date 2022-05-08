"""
Main app file
"""
# pylint: disable=invalid-name
import json
import re
import uuid
import bs4
import flask
from checks_gets import end_check

app = flask.Flask(__name__)

games = {}
x = "XO"


@app.route("/")
def home():
    """index"""
    soup = bs4.BeautifulSoup(
        "<!DOCTYPE html><html><head><title>Tic-Tac-Toe Home</title></head></html>",
        "html.parser",
    )
    body = soup.new_tag("body")
    start_new = soup.new_tag(
        "input", id="start_new", type="button", value="Start New", onclick="location.href='/game';"
    )
    body.append(start_new)
    soup.find('html').append(body)
    return soup.prettify()


@app.route("/game")
def active_game():
    """Active game"""
    soup = bs4.BeautifulSoup(
        open("game.html", "r", encoding="utf-8").read(), "html.parser"
    )
    body = soup.new_tag("body")
    board = soup.new_tag("div", attrs={"class": "ttt_board"})
    tbl = soup.new_tag("table", id="ttt_board")
    for r in "abc":
        row = soup.new_tag("tr", id=f"row_{r}")
        for c in "123":
            col = soup.new_tag("td", id=f"{r}{c}")
            col.append(
                soup.new_tag(
                    "input",
                    type="button",
                    id=f"{r}{c}b",
                    value=" ",
                    onclick=f"setSpace('{r}{c}')",
                    attrs={"class": "ttt_space"},
                )
            )
            row.append(col)
        tbl.append(row)
    board.append(tbl)
    body.append(board)
    name_div = soup.new_tag("div", id="div_name")
    name_div.append("Enter name ")
    name_input = soup.new_tag("input", id="input_name", type="text")
    name_submit = soup.new_tag(
        "input",
        id="submit_name",
        type="submit",value="Enter",
        onclick="setPlayer(document.getElementById('input_name').value);",
    )
    name_div.append(name_input)
    name_div.append(name_submit)
    body.append(name_div)
    soup.find("html").append(body)
    foot = soup.new_tag("footer", id="game_id")
    gameid = uuid.uuid1().hex
    games[gameid] = {
        "board": {"a": ["", "", ""], "b": ["", "", ""], "c": ["", "", ""]},
        "turn": False,
        "players": [],
        "ended": False
    }
    foot.append(gameid)
    soup.find("html").append(foot)
    return soup.prettify()


@app.route("/setSpace")
def set_space():
    """
    Set space
    """
    game, user, space = [
        flask.request.args.get(x, None) for x in ["game", "user", "space"]
    ]
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
    if not re.match("[abcABC][123]", space):
        return flask.Response(
            json.dumps({"message": "Invalid space ID - must be `a1` to `c3`"}),
            status=400,
            mimetype="application/json",
        )
    game = games.get(game)
    if game["ended"]:
        return flask.Response(
            json.dumps({"message": "Game ended"}),
            status=400,
            mimetype="application/json",
        )
    s = game["turn"]
    game["board"][space[0]][int(space[1]) - 1] = x[s]
    game["turn"] = not s
    game["ended"] = end_check(game["board"], x[game["turn"] - 1])[0]
    return flask.Response(
        json.dumps(
            {
                "move": x[s],
                "gameOver": game["ended"],
                "player": game["players"][s],
            }
        ),
        status=200,
        mimetype="application/json",
    )


@app.route("/setPlayer")
def set_player():
    """
    Set player
    """
    game, user = [flask.request.args.get(x, None) for x in ["game", "user"]]
    if not (res := check_game(game))[0]:
        return res[1]
    if user in games[game]["players"]:
        return flask.Response(
            json.dumps({"message": "Player already exists"}),
            status=400,
            mimetype="application/json",
        )
    games[game]["players"].append(user)
    return flask.Response(
        json.dumps({"message": "Player set"}), status=200, mimetype="application/json"
    )


@app.route("/checkWin")
def check_win():
    """
    Check win
    """
    game, user = [flask.request.args.get(x, None) for x in ["game", "user"]]
    if not (res := check_game(game))[0]:
        return res[1]
    if not (res := check_user(user))[0]:
        return res[1]
    game = games[game]
    print(game["board"])
    return flask.Response(
        json.dumps(
            {
                "won": end_check(game["board"], x[game["turn"]])[0],
                "message": game["players"][game["turn"]],
            }
        ),
        status=200,
        mimetype="application/json",
    )


@app.errorhandler(404)
def not_found(details):  # pylint: disable=unused-argument
    """404 page"""
    return "<meta http-equiv='Refresh' content=\"0; url='/?err_code=404'\">"


@app.route("/<string:img>.png")
def png(img=""):
    return open(
        img + ".png", "rb"
    ).read()  # ask how to retrieve local resource without...this


def check_game(game):
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
    if not user:
        return False, flask.Response(
            json.dumps({"message": "Username is required"}),
            status=400,
            mimetype="application/json",
        )
    return True, None


app.run(port=7744, debug=True)
