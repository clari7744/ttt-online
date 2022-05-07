import random
from utilities import bold as b, r

# CHECKS


def check_not_empty(board: dict):
    """
    Checks if there are any empty spaces left on the board.
    """
    if not any(x for rs in board.values() for x in rs):
        return False
    return True


def check_rows(board: dict, m):
    """
    Checks to see if there's a winning row.
    """
    if any(r[0] == r[1] == r[2] == m for r in board.values()):
        return True
    return False


def check_cols(board: dict, m):
    """
    Checks to see if there's a winning column.
    """
    a, b, c = board.values()
    if any(a[i] == b[i] == c[i] == m for i in range(3)):
        return True
    return False


def check_diags(board: dict, m):
    """
    Checks to see if there's a winning diagonal.
    """
    a, b, c = board.values()
    if a[0] == b[1] == c[2] == m or a[2] == b[1] == c[0] == m:
        return True
    return False


def end_check(board: dict, last, m):
    """
    Wrapper for the mini-row/col/diag win checks.
    """
    if not check_not_empty(board):
        return False
    if any((check_rows(board, m), check_cols(board, m), check_diags(board, m))):
        print(f"{b}{last}{r} wins!")
        return True
    if all(x for rs in board.values() for x in rs):
        print("All spaces are filled!\nTie game!")
        return True
    return False


# GETS


def get_ai_move(board: dict):
    """
    Randomly chooses a space from the available options.
    """
    opts = []
    for col, row in board.items():
        for ind, space in enumerate(row, 1):
            if space == "":
                opts.append(f"{ind}{col}")
    return random.choice(opts)


def get_move(board: dict, _next):
    """
    Checks whose move it is, and gives the proper prompt for said move.
    """
    if _next == "AI":
        text = get_ai_move(board)
        print(f"{_next}'s move: {b}{text}")
    else:
        text = input(f"{_next}'s move: {b}").lower()
    print(r)
    return text
