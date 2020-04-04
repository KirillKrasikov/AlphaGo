"""Base agent interface module

"""


class Agent:
    """Base interface of agents

    """
    def __init__(self):
        pass

    def select_move(self, game_state):
        """Select move by current game state

        Args:
            game_state:

        Returns:

        """
        raise NotImplementedError()
