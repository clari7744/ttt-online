"""
Main app file
"""
# https://flask.palletsprojects.com/en/2.1.x/debugging/
# look up jsonp
import bs4
import flask

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
        onclick="document.getElementById('div_name').innerHTML = 'Name: '+document.getElementById('input_name').value;",  # "{div = document.getElementById('div_name'); div.content = document.getElementById('input_name').value; div.innerHTML = 'Name: ' + div.content;}",
    )
    name_div.append(name_input)
    name_div.append(name_submit)
    body.append(name_div)
    script = soup.new_tag("script")
    script.append(
        """async function setSpace(elem) {
            n=document.getElementById('div_name').innerHTML.split(':');
            u=n.length>2?'no_name':n[1].slice(1); 
            document.getElementById(elem).innerHTML = await fetch(`${document.location.origin}/setSpace?user=${u}&space=${elem}`)
                //.then(resp=>console.log(resp))
                .then(resp=>resp.json())
                //.then(json=>console.log(json))
                .then(j=>j.move)
            }"""
    )
    # script.append(
    # "function setSpace(elem) {document.getElementById(elem).innerHTML = '<span class=text> x </span>';}"
    # )
    body.append(script)
    soup.find("html").append(body)
    return soup.prettify()

@app.route('/setSpace')
def setSpace():
    user = flask.request.args.get('user', None)
    if not user: return "User is required"
    space = flask.request.args.get('space', None)
    if not space: return "Space is required"
    return '{"move":"x"}'


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
