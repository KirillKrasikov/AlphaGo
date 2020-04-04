"""Go types module

"""
import enum
from collections import namedtuple
from typing import List


class Player(enum.Enum):
    """Player type enumeration class

    """
    black = 1
    white = 2

    @property
    def other(self) -> enum.Enum:
        """Other opponent color

        Returns:
            integer value of the opponent color
        """
        return Player.black if self == Player.white else Player.white


class Point(namedtuple('Point', 'row col')):
    """Board coordinates represented in the form of tuples

    """
    def neighbors(self) -> List[namedtuple]:
        """Points surrounding the current instance

        Returns:
            List of surrounding points

        """
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
