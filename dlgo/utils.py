"""Utils

"""
from dlgo import gotypes


COLS = 'ABCDEFGHJKLMNOPQRST'

STONE_TO_CHAR = {
    None: ' . ',
    gotypes.Player.black: ' x ',
    gotypes.Player.white: ' o ',
}


def print_move(player, move):
    """Print move

    Args:
        player:
        move:

    Returns:
        None

    """
    if move.is_pass:
        move_str = 'passes'
    elif move.is_resign:
        move_str = 'resigns'
    else:
        move_str = f'{COLS[move.point.col - 1]}{move.point.row}'

    print(f'{player} {move_str}')


def print_board(board):
    """Print board

    Args:
        board:

    Returns:
        None

    """
    for row in range(board.num_rows, 0, -1):
        bump = ' ' if row <= 9 else ''
        line = []
        for col in range(1, board.num_cols + 1):
            stone = board.get(gotypes.Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])

        print(f'{bump}{row} {"".join(line)}')

    print('    ' + '  '.join(COLS[:board.num_cols]))


def point_from_coords(coords: str) -> gotypes.Point:
    """Convert input string of coordinates to Point

    Args:
        coords: str like 'A11'

    Returns:
        Point

    """
    col = COLS.index(coords[0]) + 1
    row = int(coords[1:])

    return gotypes.Point(row=row, col=col)
