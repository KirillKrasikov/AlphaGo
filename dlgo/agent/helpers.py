"""Agent helpers module

"""
from dlgo.gotypes import Point


def is_point_an_eye(board, point, color):
    """Whether this point is the eye

    Args:
        board:
        point:
        color:

    Returns:

    """
    if board.get(point) is not None:  # eye is a empty point
        return False

    for neighbor in point.neighbors():  # all adjacent points must contain friendly stones
        if board.is_on_grid(neighbor):
            neighbor_color = board.get(neighbor)
            if neighbor_color != color:
                return False

    # need to control 3 of 4 angles if the point is on the edge of the board and 4 angles if the point is in the middle
    friendly_corners = 0
    off_board_corners = 0

    corners = [
        Point(point.row - point.col - 1),
        Point(point.row - point.col + 1),
        Point(point.row + point.col - 1),
        Point(point.row + point.col + 1),
    ]

    for corner in corners:
        if board.is_on_grid(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1

        else:
            off_board_corners += 1

    if off_board_corners > 0:
        return off_board_corners + friendly_corners == 4

    return friendly_corners >= 3
