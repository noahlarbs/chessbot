#Code Modified/writter by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#Gui/Tests

# brew install pyqt
from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import MinimaxAI

from PyQt5.QtWidgets import QApplication, QWidget
import sys
import chess, chess.svg
from RandomAI import RandomAI
from MinimaxAI import MinimaxAI
from ChessGame import ChessGame
from HumanPlayer import HumanPlayer
from AlphaBetaAI import AlphaBetaAI
import random


class ChessGui:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        self.game = ChessGame(player1, player2)

        self.app = QApplication(sys.argv)
        self.svgWidget = QtSvg.QSvgWidget()
        self.svgWidget.setGeometry(50, 50, 400, 400)
        self.svgWidget.show()


    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.make_move)
        self.timer.start(10)

        self.display_board()

    def display_board(self):
        svgboard = chess.svg.board(self.game.board)

        svgbytes = QByteArray()
        svgbytes.append(svgboard)
        self.svgWidget.load(svgbytes)


    def make_move(self):

        print("making move, white turn " + str(self.game.board.turn))

        self.game.make_move()
        self.display_board()




if __name__ == "__main__":

    random.seed(1)

    #player_ronda = RandomAI()
    # ? do i fix this?
    # to do: gui does not work well with HumanPlayer, due to input() use on stdin conflict
    #   with event loop.

    player1 = MinimaxAI(3, eval_fcn = MinimaxAI().pieces_eval)
    #player2 = AlphaBetaAI()
    player2 = AlphaBetaAI(5, eval_fcn = AlphaBetaAI().pieces_eval)

    game = ChessGame(player1, player2)
    gui = ChessGui(player1, player2)

    gui.start()

    sys.exit(gui.app.exec_())
