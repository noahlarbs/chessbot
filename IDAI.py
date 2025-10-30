#Code Modified/writter by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#Iterative Deepening Search module for chess

import math
import chess
from AlphaBetaAI import AlphaBetaAI


class IDAI(AlphaBetaAI):
    # inits iterative deepning with max depth 3 by default
    def __init__(self, depth: int = 3, eval_fcn=None):
        super().__init__(depth= depth, eval_fcn=eval_fcn)
        self.best_move = None

    def choose_move(self, board: chess.Board):
        # new best move for this turn
        self.best_move = None
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        max_depth = self._depth_for_turn(board.fullmove_number)
        c = board.turn #color

        #deepen from 1..max_depth
        for depth in range(1, max_depth + 1):
            bestVal = -math.inf
            bestMove = None
            alpha = -math.inf
            beta = math.inf

            # prefer prev found best move for move ordering
            if self.best_move is not None and self.best_move in legal_moves:
                ordered_moves = [self.best_move] + [m for m in legal_moves if m != self.best_move]
            else:
                ordered_moves = legal_moves
            for move in ordered_moves:
                board.push(move)
                v = self.min_value(board, depth - 1, c, alpha, beta, 1)
                board.pop()
                if v > bestVal:
                    bestVal = v
                    bestMove = move
                if bestVal > alpha:
                    alpha = bestVal

            #store best move found at _ depth
            if bestMove is not None:
                self.best_move = bestMove

            # print progress 
            print(f"the best move at depth {depth} is {self.best_move} (value {bestVal})")

            if bestMove is None:
            # should not happen, but just in case
                legal = list(board.legal_moves)
                if not legal:
                    raise RuntimeError("No legal moves available in choose_move")
                bestMove = legal[0]

            # early exit if result (checkmate found)
            if abs(bestVal) == math.inf:
                break

        return self.best_move
    # arbitrary depth limits based on num of moves - exmaple, could also generalize to time based on an input time limit for the game

    def _depth_for_turn(self, fullmove_number: int) -> int:
        if fullmove_number < 6:
            return min(self.depth, 3)
        if fullmove_number < 15:
            return min(self.depth, 4)
        if fullmove_number < 30:
            return min(self.depth, 5)
        return min(self.depth, 6)