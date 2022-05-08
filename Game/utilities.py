import random

bold = "\033[1m"
r = "\033[0m"
heads = bold + "\033[95m\033[91m"
os = bold + "\033[94m"
xs = bold + "\033[92m"
ttt_help = "How to play:\n*wip check back later*"


def y_n(text):
    """
    Simple input wrapper for yes or no input.
    """
    resp = input(text + " [y/n] " + bold).lower() in ("y", "ye", "yes", "1")
    print(r)
    return resp


def make_board(a, b):
    """
    Builds a new board.
    """
    board = dict(zip("abc", (["", "", ""], ["", "", ""], ["", "", ""])))
    _next = random.choice((a, b))
    last = b if _next == a else a
    return board, _next, last


def get_p2_name(p1):
    """
    Gets Player 2's name and whether or not it should be an AI.
    """
    if y_n(
        "Would you like to play against an AI? (Will prompt for Player 2 if you don't say yes)"
    ):
        return "AI"

    def p2n():
        print("Player 2: Input your name")
        return input(f">>> {bold}")

    u_b = p2n()
    while u_b in [p1, ""]:
        if u_b == p1:
            print(f"{r}Players cannot have the same name!")
        elif u_b == "":
            print(f"{r}Names cannot be blank!")
        else:
            print(f"{r}how did you get here do tell")
        u_b = p2n()
    return u_b


