"""Random choosing bots play script

"""
import time

from dlgo.agent import RandomBot
from dlgo import goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move


def main():
    """Random bots game

    Returns:
        None

    """
    board_size = 9
    game = goboard.GameState.new_game(board_size)

    bots = {
        gotypes.Player.black: RandomBot(),
        gotypes.Player.white: RandomBot(),
    }

    while not game.is_over():

        bot_move = bots[game.next_player].select_move(game)

        print(chr(27) + "[2J")  # Clear terminal
        print_board(game.board)
        print_move(game.next_player, bot_move)

        game = game.apply_move(bot_move)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print(time.time() - start_time)
