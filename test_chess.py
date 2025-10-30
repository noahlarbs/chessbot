
#Code Modified/writter by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#Iterative Deepening Search module for chess

# pip3 install python-chess

import chess
from RandomAI import RandomAI
from HumanPlayer import HumanPlayer
from MinimaxAI import MinimaxAI
from AlphaBetaAI import AlphaBetaAI
from ChessGame import ChessGame
from IDAI import IDAI
#player1 = HumanPlayer()
#player1 = RandomAI()
# player2 = MinimaxAI(3, eval_fcn = MinimaxAI().pieces_eval)
#player1 = MinimaxAI(3, eval_fcn = MinimaxAI().pieces_eval)
player1 = AlphaBetaAI(4, eval_fcn = AlphaBetaAI().pieces_eval)
player2 = IDAI(4, eval_fcn = AlphaBetaAI().pieces_eval)
game = ChessGame(player1, player2)

while not game.is_game_over():
    print(game)
    game.make_move()


# print final position and outcome
print("FINAL POSITION:")
print(game)
print("Result:", game.board.result())
print("Checkmate:", game.board.is_checkmate())
print("Stalemate:", game.board.is_stalemate())
print("Bad Board?", game.board.is_insufficient_material())

# who won (if checkmate)
if game.board.is_checkmate():
    winner = "White" if game.board.result() == "1-0" else "Black"
    print("Winner:", winner)

#print(hash(str(game.board)))
