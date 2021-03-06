"""Naive bot module

"""
import random

from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point


class RandomBot(Agent):
    """Random bot

    """
    def select_move(self, game_state):
        """Choose a random valid move that preserves our own eyes

        Args:
            game_state:

        Returns:
            fixme
        """
        candidates = []
        for row in range(1, game_state.board.num_rows + 1):
            for col in range(1, game_state.board.num_cols + 1):
                candidate = Point(row=row, col=col)
                if game_state.is_valid_move(Move.play(candidate)) and \
                    not is_point_an_eye(
                            game_state.board,
                            candidate,
                            game_state.next_player,
                    ):
                    candidates.append(candidate)

        if not candidates:
            return Move.pass_turn()

        return Move.play(random.choice(candidates))
