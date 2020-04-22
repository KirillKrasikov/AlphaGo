import time

from dlgo import goboard_fast
from dlgo import gotypes
from dlgo.agent import MCTSAgent, RandomBot
from dlgo.utils import print_board, print_move, point_from_coords

BOARD_SIZE = 5


def capture_diff(game_state):
    black_stones = 0
    white_stones = 0
    for r in range(1, game_state.board.num_rows + 1):
        for c in range(1, game_state.board.num_cols + 1):
            p = gotypes.Point(r, c)
            color = game_state.board.get(p)
            if color == gotypes.Player.black:
                black_stones += 1
            elif color == gotypes.Player.white:
                white_stones += 1
    diff = black_stones - white_stones
    if game_state.next_player == gotypes.Player.black:
        return diff
    return -1 * diff


def main():
    game = goboard_fast.GameState.new_game(BOARD_SIZE)

    bots = {
        gotypes.Player.white: MCTSAgent(500, temperature=0.8),
        gotypes.Player.black: MCTSAgent(500, temperature=1.4),
    }

    while not game.is_over():
        # print(chr(27) + "[2J")  # Clear terminal
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
        print_board(game.board)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print(time.time() - start_time)

