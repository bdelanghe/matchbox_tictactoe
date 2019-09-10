"""
TIC TAC TOE GAME

Play a simple game inside python's cmd module. The board is drawn to match the curses module layout:

  0 1 2 x
0| | | |
1| | | |
2| | | |
y

Play multiple session and keep track of score. Future versions will have curses graphics and an AI.
Currently considering created a MENACE machine in which all learning is done from beads inside matchboxes.
"""

from __future__ import annotations

from cmd import Cmd
from collections import namedtuple
from typing import List, Dict, Optional

import numpy as np
from pyfiglet import Figlet

f: Figlet = Figlet(font='slant')

Size = namedtuple('Size', ['y', 'x'])
Square = namedtuple('Square', ['y', 'x'])
CursesCords = namedtuple('Cords', ['y', 'x'])


class CmdMode(Cmd):
    """cmd wrapper for interactions"""
    intro = f.renderText('TIC TAC TOE')
    prompt = '(play)'
    file = None

    def __init__(self):
        super().__init__()
        self.session = Session
        self.player = 0

    def default(self, line):
        """making errors more fun"""
        print("I'm sorry I'm a bit confused. Maybe ask for 'help'?")

    def preloop(self):
        """Hook method executed once when the cmdloop() method is called."""
        print(f.renderText('TIC TAC TOE'))
        self.session.new_game()
        self._print_scores()
        self._print_board()

    def postloop(self):
        """After it's over"""
        pass

    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.
        """
        if self._do_last is True and self.last_simple is not None:
            return f'{self.last_simple} {line}'
        else:
            return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        if self._end is False and self.last_simple == 'move':
            self._print_board()
        return stop

    @staticmethod
    def _print_bye() -> None:
        """"print bye"""
        print(f.renderText('thanks for playing\n'))

    def _print_board(self) -> None:
        """print the current board to console"""
        print()
        for l in self.session.current_game.current_board:
            line = ''
            for e in l:
                line += '|' + e
            print(line + '|')
        print('\n')

    def _print_scores(self) -> None:
        """display the current player scores to console"""
        scores = []
        for player in self.players.values():
            scores.append(f'Player {player.name}: {player.wins} wins')
        scores.append(f'Ties: {self.players[0].ties}')
        print(str.join('   |   ', scores) + '\n')


class Player:
    """player object to hold moves and score"""

    def move(self, sqr: Square) -> bool:
        """add move to player moves"""
        return self.moves.move(sqr)

    def __init__(self, number: int) -> None:
        self.moves: Moves = Moves()
        self.number = number
        self.name = f'Player {self.number + 1}'
        self.wins = 0
        self.ties = 0


class Session:
    """sessions help keep track score"""

    def new_game(self) -> None:
        """create a new game"""
        if self.current_game is not None:
            self.play_count += 1
            del self.current_game
        self.current_game = Game(self)

    def __init__(self) -> None:
        self.players: Dict[int, Player] = {0: Player(0), 1: Player(1)}
        self.current_game: Optional[Game] = None
        self.play_count: int = 0

    def _new_game(self) -> None:
        """create a new game"""
        if self.current_game is not None:
            self.play_count += 1
            del self.current_game
        self.current_game = Game(self)

    def _print_scores(self) -> None:
        """display the current player scores to console"""
        scores = ''
        for player in self.players.values():
            scores += f'Player {player.number + 1}: {player.score}      '
        print(scores + '\n')

    @staticmethod
    def _print_exit_message() -> None:
        """saying goodbye is always hard"""
        print('Thanks for playing!!')

    def play(self):
        """keep playing games until quit"""
        while self.quit is False:
            self._print_scores()
            self._new_game()
            self.current_game.play()
        self._print_exit_message()


class Game:
    """simple class for playing in cmd"""

    n_by = 3
    marks = {0: 'x', 1: 'o'}

    def square_input(self, sqr: Square) -> Optional[bool]:
        """input from square object"""
        if self._is_open(sqr):
            return self._play_move(sqr)

    def __init__(self, session) -> None:
        self.session: Optional[Session] = session
        self.players: Dict[int, Player] = self.session.players
        self.turns: int = 0

    def __del__(self) -> None:
        """clean house on game end"""
        for player in self.players.values():
            player.moves.reset_moves()

    @property
    def current_board(self) -> List[List[str]]:
        """add the view of both players"""
        board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        for _, player in self.players.items():
            for y, row in enumerate(player.moves.matrix):
                for x, e in enumerate(row):
                    if e == 1:
                        board[y][x] = self.marks[player.number != self.session.first_move]
            return board

    @property
    def current_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns) % 2]

    @property
    def open_squares(self) -> np.matrix:
        """the inverse of all squares played"""
        moves = self.players[0].moves.matrix + self.players[1].moves.matrix
        return 1 - moves

    @property
    def _waiting_player(self) -> Player:
        """the player who's turn it is"""
        start = self.session.first_move
        return self.session.players[(start + self.turns - 1) % 2]

    def _cats(self) -> None:
        """better luck next time"""
        for player in self.players.values():
            player.ties += 1
        self._print_cats()
        self._end()

    def _end(self) -> None:
        self.session.new_game()
        """called if winner or tie"""

    def _is_open(self, sqr: Square) -> bool:
        """this is not the square you are looking for"""
        free = self.open_squares[sqr.y][sqr.x]
        if free == 0:
            self._print_square_not_free()
        return free

    def _is_last(self) -> bool:
        """are there any spots left to play"""
        for line in self.open_squares:
            for e in line:
                if e == 1:
                    return False
        return True

    def _new_winner(self) -> None:
        """increment play score"""
        self.current_player.wins += 1
        self._print_winner(self.current_player)
        self._end()

    def _play_move(self, sqr: Square) -> None:
        """commit a move and return if winner"""
        win = self.current_player.move(sqr)
        if win is True:
            self._new_winner()
        if self._is_last() is True:
            self._cats()
        self.turns += 1

    # todo remove printing from class
    @staticmethod
    def _print_cats() -> None:
        """let players know the cat always wins"""
        print(f.renderText("Cat's Game"))

    @staticmethod
    def _print_square_not_free():
        """Can't sit here"""
        print('Square is not open')

    @staticmethod
    def _print_winner(player: Player) -> None:
        """congrats are due"""
        print(f.renderText(f'{player.name} Wins!!!!'))


class Moves:
    """store all the moves a player has made"""
    n_by = 3

    def move(self, sqr: Square) -> bool:
        """add a move to np matrix return win"""
        self.matrix[sqr.y][sqr.x] = 1
        return self._is_win_move(sqr)

    def reset_moves(self):
        """reset after end of game"""
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def __init__(self):
        self.matrix: np.ndarray = np.zeros((self.n_by, self.n_by), dtype=int)

    def __repr__(self) -> str:
        return str(self.matrix)

    def _is_win_move(self, sqr: Square) -> bool:
        """check if the last move was the winning move"""
        # todo return which line contributed to the win
        #  maybe make a win tuple?

        if np.sum(self.matrix[sqr.y]) == self.n_by:
            return True
        elif sum([l[sqr.x] for l in self.matrix]) == self.n_by:
            return True
        elif sqr.x == sqr.y:
            if sum(np.diagonal(self.matrix)) == self.n_by:
                return True
        else:
            if sum(np.diag(np.fliplr(self.matrix))) == self.n_by:
                return True
        return False


class CursesSession(Session):
    """a class extension to include curses"""

    def __init__(self) -> None:
        super().__init__()
        self.quit_char = '`'
        self.window = Window(self.play())

    def play(self) -> None:
        """while loop for playing in curses"""
        curses.curs_set(0)

        while self.quit is False:
            self._new_game()
            self.current_game.play()


# class AiPlayer(Player):
#     """smart player extension"""
#
#     # todo add AI class
#     def __init__(self, number) -> None:
#         super().__init__(number)


class CursesGame(Game):
    """extended Game class for Curses"""

    def __init__(self, session: CursesSession) -> None:
        super().__init__(session)
        self.session = session
        self.board: BoardLib = BoardLib(self.session.window)

    def play(self) -> None:
        """display loop for curses"""
        # fixme after simplifying play
        # self.stdscr.clear()
        # self.stdscr.refresh()
        #
        # self.draw_board()
        #
        # while self.end is False:
        #     # todo make one call
        #     move = self.input()
        #
        #     stdscr.refresh()

    def _draw_board(self) -> None:
        """draw board in curses window"""
        str_list = self.board.board_grid
        self.session.window.draw_centered(str_list)

    def _curses_input(self) -> None:
        """overwrite game func to allow for quiting"""
        char: str = self.session.window.get_input()
        if char == self.session.quit_char:
            self.end = True
            self.session.quit = True
        else:
            self._input(char)


# class BoardLib:
#     """extended library object for curses"""
#
#     def __init__(self, window: Window = None):
#         self._window = window
#         self.n_by: int = 3
#         self.scale: float = 2 / 3
#         self.line_fill: str = u'\u2588'
#         self.cross_fill: str = '?'
#         self.nought_fill: str = '@'
#         self.square_map: dict = {}
#
#     @property
#     def _window(self) -> Window:
#         """Current curses window for obj"""
#         return self._window
#
#     @_window.setter
#     def _window(self, value: Optional[Window]) -> None:
#         """allow for no window object for debugging"""
#         if value is not None:
#             self._window = value
#
#     @property
#     def _square_size(self) -> Size:
#         """find the pixel box size for each square"""
#         sqr_y = int((self._window.short_side * self.scale) / self.n_by)
#         sqr_x = sqr_y * 2
#         return Size(y=sqr_y, x=sqr_x)
#
#     @property
#     def board_grid(self) -> List[str]:
#         """creating a string for printing the TicTacToe grid"""
#         # todo: rewrite to just give cords of lines
#         lines = []
#         size = self._square_size
#         self.square_map = {}
#
#         for row in range(1, (size.y * self.n_by) + self.n_by):
#             line = ''
#             for col in range(1, (size.y * self.n_by) + self.n_by):
#                 y = int(row / self.n_by)
#                 x = int(col / self.n_by)
#                 sqr_cord = Square(y=y, x=x)
#                 curse_cord = CursesCords(y=row, x=col)
#                 if row % (size.y + 1) == 0:
#                     line += self.line_fill * 2
#                 elif col % (size.y + 1) == 0:
#                     line += self.line_fill * 2
#                 else:
#                     if sqr_cord not in self.square_map:
#                         self.square_map[sqr_cord] = []
#                     self.square_map[sqr_cord].append(curse_cord)
#             lines.append(line)
#
#         return lines
#
#     @staticmethod
#     def invert(string) -> str:
#         """invert the characters of a square"""
#         fill = max([c for c in string])
#         return str([' ' if fill else fill for _ in string])
#
#     @property
#     def cross(self) -> str:
#         """create a string for a cross"""
#         string = ''
#         sqr = self._square_size
#
#         for row in range(sqr.y):
#             for col in range(sqr.x):
#                 if col == row * 2 or col == (sqr.x - 1) - (row * 2):
#                     string += self.cross_fill
#                 else:
#                     string += ' '
#         return string
#
#     @property
#     def nought(self) -> str:
#         """create a string for a nought"""
#         string = ''
#         sqr = self._square_size
#
#         # Needed to add a boarder to get it to look right
#         border = 1 / 2
#         radius = sqr.y / 2 - border
#         for row in range(sqr.y):
#             for col in range(sqr.y):
#                 dist = math.sqrt((row - radius) * (row - radius) +
#                                  (col - radius) * (col - radius)) + 1
#                 if radius - border < dist < radius + border:
#                     string += self.nought_fill * 2
#                 else:
#
#                     string += ' ' * 2
#         return string


# def title_screen(stdscr: curses.initscr) -> None:
#     """a fun title screen"""
#     # todo turn this into an object?
#     # Set properties
#     curses.curs_set(0)
#     stdscr.nodelay(True)
#
#     # Get key input
#     k = stdscr.getch()
#
#     # Get window params
#     win_h, win_w = stdscr.getmaxyx()
#
#     def wipe_text(text: str) -> int:
#         """load multi-line text from left to right"""
#         lines = text.split("\n")
#
#         # Get dimensions for text
#         x_len = len(lines[0])
#         y_len = len(lines)
#
#         # Find center for text
#         x = int((win_w - x_len) / 2)
#         y = y_start = int((win_h - y_len) / 2)
#
#         for i in range(x_len):
#             y = y_start
#             for line in lines[:-1]:
#                 stdscr.addstr(y, x, line[i])
#                 y += 1
#             stdscr.refresh()
#             time.sleep(.05)
#             x += 1
#         return y
#
#     def load_title() -> None:
#         """add title to window"""
#         title = f.renderText('TIC TAC TOE')
#         sub_title = 'produced by: robert delanghe studio'
#         any_key = 'press any key to continue'
#
#         y: int = wipe_text(title)
#
#         stdscr.addstr(y, int((win_w - len(sub_title)) / 2), sub_title)
#         stdscr.refresh()
#
#         time.sleep(1)
#
#         stdscr.addstr(win_h - 1, win_w - len(any_key) - 2, any_key, curses.A_BLINK + curses.A_DIM)
#
#         stdscr.refresh()
#
#     load_title()
#
#     while k == -1:
#         k = stdscr.getch()


# def play() -> None:
#     """lets play tic tac toe"""
#     sess = Session()
#     sess.play()


def main() -> None:
    """want to play a game of tic tac toe?"""
    # curses.wrapper(title_screen)
    play()
    # CmdMode().cmdloop()


if __name__ == "__main__":
    main()
