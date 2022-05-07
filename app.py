"""
Main app file
"""
# https://flask.palletsprojects.com/en/2.1.x/debugging/
# look up jsonp
import uuid
import bs4
import flask
import json

app = flask.Flask(__name__)
# flask.request.args = query params

games = {}


@app.route("/")
def home():
    """index"""
    return "Games will show here"


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
    name_div.append("Enter Name: ")
    name_input = soup.new_tag("input", id="input_name", type="text")
    name_submit = soup.new_tag(
        "input",
        id="submit_name",
        type="submit",
        onclick="document.getElementById('div_name').innerHTML = 'Name: '+document.getElementById('input_name').value;",
    )
    name_div.append(name_input)
    name_div.append(name_submit)
    body.append(name_div)
    soup.find("html").append(body)
    foot = soup.new_tag("footer", id="game_id")
    foot.append(uuid.uuid1().hex)
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
    if not game:
        return flask.Response(
            json.dumps({"message": "No game specified"}),
            status=400,
            mimetype="application/json",
        )
    if not user or not space:
        return flask.Response(
            json.dumps(
                {"message": ("Space ID" if not space else "Username") + " is required"}
            ),
            status=400,
            mimetype="application/json",
        )
    s = "X"  # "O"
    return flask.Response(
        json.dumps({"move": s}),
        status=200,
        mimetype="application/json",
    )


@app.errorhandler(404)
def not_found(details):
    """404 page"""
    return "<meta http-equiv='Refresh' content=\"0; url='/?err_code=404'\">"


@app.route("/<string:img>.png")
def png(img=""):
    return open(
        img + ".png", "rb"
    ).read()  # ask how to retrieve local resource without...this


app.run()
