"""Go board module

"""
import copy

from dlgo.gotypes import Player
from dlgo import zobrist


class Move():
    """A move means placing a stone on a board, skipping a move or quitting a game

    Args:
        point: point to placing a stone
        is_pass: move skipping
        is_resign: quitting a game

    """
    def __init__(
            self,
            point=None,
            is_pass=False,
            is_resign=False,
    ):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        """Move involving placing a stone on a board

        Args:
            point:

        Returns:
            Move

        """
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        """Move involves skipping

        Returns:
            Move instance

        """
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        """Move involves quitting the game

        Returns:
            Move instance

        """
        return Move(is_resign=True)


class GoString:
    """Tracking groups of related stones and their degrees of freedom

    Args:
        color:
        stones:
        liberties:

    """
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        """Fixed state accounting

        Args:
            point:

        Returns:
            GoString instance

        """
        new_liberties = self.liberties - set([point])

        return GoString(self.color, self.stones, new_liberties)

    def with_liberty(self, point):
        """Fixed state accounting

        Args:
            point:

        Returns:
            GoString instance

        """
        new_liberties = self.liberties | set([point])

        return GoString(self.color, self.stones, new_liberties)

    def merge_with(self, go_string):
        """Merge two stones strings

        Args:
            go_string: Other tracking group stones

        Returns:
            New chain containing all the stones of both chains

        """
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones

        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )

    @property
    def num_liberties(self) -> int:
        """Degrees of liberties

        Returns:
            Num of liberties

        """
        return len(self.liberties)

    def __eq__(self, other):
        """Overload of equality

        x == y calls x.__eq__(y).

        Args:
            other: y

        Returns:
            equality as bool

        """
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board():
    """Board is initialized as an empty grid consisting of a given number of rows and columns

    Args:
        num_rows:
        num_cols:

    """
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD

    def place_stone(self, player, point):
        """Checking the degrees of liberties numbers for neighboring points

        Args:
            player:
            point:

        Returns:
            None

        """
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []

        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue

            neighbor_string = self._grid.get(neighbor)

            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
                else:
                    if neighbor_string not in adjacent_opposite_color:
                        adjacent_opposite_color.append(neighbor_string)

        new_string = GoString(player, [point], liberties)

        # Union all adjacent stones of the same color
        for same_color_string in adjacent_same_color:
            new_string = new_string.merge_with(same_color_string)

        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        self._hash ^= zobrist.HASH_CODE[point, player]

        # Decline number of degrees of freedom of neighboring chains of stones of the same color
        for other_color_string in adjacent_opposite_color:
            replacement = other_color_string.without_liberty(point)
            if replacement.num_liberties:
                self._replace_string(other_color_string.without_liberty(point))
            else:
                self._remove_string(other_color_string)

    def _replace_string(self, new_string):
        """Board grid update

        Args:
            new_string:

        Returns:
            None

        """
        for point in new_string.stones:
            self._grid[point] = new_string

    def is_on_grid(self, point):
        """Check if a point is on the board

        Args:
            point:

        Returns:
            True if point on the board else False

        """
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        """Get contents of a point on the board

        Args:
            point:

        Returns:
            information about the player if there is a stone, otherwise None
        """
        string = self._grid.get(point)

        return None if string is None else string.color

    def get_go_string(self, point):
        """Get whole chain of stones if there is a stone at this point, otherwise None

        Args:
            point:

        Returns:
            Whole chain of stones if there is a stone at this point, otherwise None

        """
        string = self._grid.get(point)

        return None if string is None else string

    def _remove_string(self, string):
        """Stone string removal

        Args:
            string:

        Returns:
            None

        """
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue

                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))

            self._grid[point] = None

            self._hash ^= zobrist.HASH_CODE[point, string.color]

    def zobrist_hash(self):
        """Current board hash

        Returns:
            Zobrist hash

        """
        return self._hash


class GameState:
    """Game state fixation

    Args:
        board: fixme
        next_player: fixme
        previous: fixme
        move: fixme

    """
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())})
        self.last_move = move

    def apply_move(self, move):
        """Apply move

        Args:
            move:

        Returns:
            new game state after completion of the turn

        """
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board

        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        """New game

        Args:
            board_size:

        Returns:
            New game state instance

        """
        if isinstance(board_size, int):
            board_size = (board_size, board_size)

        board = Board(*board_size)

        return GameState(board, Player.black, None, None)

    def is_over(self):
        """Determining the end of the game

        Returns:
            bool

        """
        if self.last_move is None:
            return False

        if self.last_move.is_resign:
            return True

        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False

        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player, move):
        """Self capture rule

        Args:
            player:
            move:

        Returns:
            bool

        """
        if not move.is_play:
            return False

        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)

        return new_string.num_liberties == 0

    @property
    def situation(self):
        """Game situation

        Returns:

        """
        return self.next_player, self.board

    def does_move_violate_ko(self, player, move):
        """ko rule

        Args:
            player:
            move:

        Returns:
            bool

        """
        if not move.is_play:
            return False

        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())

        return next_situation in self.previous_states

    def is_valid_move(self, move):
        """Check move for current game state

        Args:
            move:

        Returns:

        """
        if self.is_over():
            return False

        if move.is_pass or move.is_resign:
            return True

        return (
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.next_player, move) and
            not self.does_move_violate_ko(self.next_player, move)
        )
