"""
TicTacToe game by Clari
Made for the Game Design Merit Badge
"""
from utilities import (
    startup,
    make_board,
    y_n,
    print_board,
    get_move,
    validate_text,
    end_check,
    r,
    ttt_help,
)

users = startup()


def start_game(_users: tuple):
    """
    Actual running of the game, ties all the little inner functions together.
    """
    user_a, user_b = _users
    board, _next, last = make_board(user_a, user_b)
    print(r, f"\n{_next} has been chosen to go first!")
    while True:
        print_board(board)
        if end_check(board, last, "X" if last == user_a else "O"):
            break
        text: str = get_move(board, _next)
        if text in "finish fi quit q end exit".split():
            print(f"{r}Thanks for playing!")
            return 0
        if text in "help h".split():
            print(ttt_help)
            continue
        validated = validate_text(board, text)
        if not validated:
            continue
        row, col = validated
        board[row][col] = "X" if _next == user_a else "O"
        last = _next
        _next = user_b if _next == user_a else user_a
    print("Game complete!")
    if y_n("Play again?"):
        if y_n("Change names or switch modes?"):
            return start_game(startup(True))
        return start_game(users)
    print(f"{r}Thanks for playing!")
    return 0


start_game(users)
