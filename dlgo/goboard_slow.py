"""Go board module

"""
import copy

from dlgo.gotypes import Player


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
    def play(cls, point) -> 'Move':
        """Move involving placing a stone on a board

        Args:
            point:

        Returns:
            Move instance

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
        self.stones = stones
        self.liberties = set(liberties)

    def remove_liberty(self, point) -> None:
        """Remove liberty

        Args:
            point:

        Returns:
            None

        """
        self.liberties.remove(point)

    def add_liberty(self, point) -> None:
        """Add liberty

        Args:
            point:

        Returns:
            None

        """
        self.liberties.add(point)

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

    def __eq__(self, other) -> bool:
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

    """
    def __init__(self, num_rows: int, num_cols: int):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}

    def place_stone(self, player, point):
        """Checking the degrees of liberties numbers for neighboring points

        Args:
            player: fixme
            point:  fixme

        Returns:
            fixme

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

        # Union all adjacent stones of the same colo
        for same_color_string in adjacent_same_color:
            new_string = new_string.merge_with(same_color_string)

        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        # Decline number of degrees of freedom of neighboring chains of stones of the same color
        for other_color_string in adjacent_opposite_color:
            other_color_string.remove_liberty(point)

        for other_color_string in adjacent_opposite_color:
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)


    def is_on_grid(self, point):
        """Check if a point is on the board

        Args:
            point: fixme

        Returns: fixme

        """
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        """Get contents of a point on the board

        Args:
            point: fixme

        Returns:
            information about the player if there is a stone, otherwise None
        """
        string = self._grid.get(point)

        return None if string is None else string.color

    def get_go_string(self, point):
        """Get whole chain of stones if there is a stone at this point, otherwise None

        Args:
            point: fixme

        Returns:
            whole chain of stones if there is a stone at this point, otherwise None

        """
        string = self._grid.get(point)

        return None if string is None else string

    def _remove_string(self, string) -> None:
        """Stone string removal

        Args:
            string: fixme

        Returns:
            None

        """
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue

                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)

            self._grid[point] = None


class GameState:
    """Game state fixation

    Args:
        board: fixme
        next_player:
        previous:
        move:

    """
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
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
            board_size: fixme

        Returns:
            new GameState instance

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
        """fixme

        Returns:

        """
        return (self.next_player, self.board)

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
        next_situation = (player.other, next_board)
        past_state = self.previous_state

        while past_state is not None:
            if past_state.situation == next_situation:
                return True

            past_state = past_state.previous_state

        return False

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
