def check_not_empty(board: dict):
    """
    Checks if there are any empty spaces left on the board.
    """
    if not any(x for rs in board.values() for x in rs):
        return False
    return True


def check_rows(board: dict, sym):
    """
    Checks to see if there's a winning row.
    """
    if any(r[0] == r[1] == r[2] == sym for r in board.values()):
        return True
    return False


def check_cols(board: dict, sym):
    """
    Checks to see if there's a winning column.
    """
    a, b, c = board.values()
    if any(a[i] == b[i] == c[i] == sym for i in range(3)):
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


def end_check(board: dict, sym):  # Ended, isTie
    """
    Wrapper for the mini-row/col/diag win checks.
    """
    if not check_not_empty(board):
        return False, False
    if any((check_rows(board, sym), check_cols(board, sym), check_diags(board, sym))):
        return True, False
    if all(x for rs in board.values() for x in rs):
        return True, True
    return False, False