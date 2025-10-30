#Code Modified/writter by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#Minimax Search module for chess

import chess
from math import inf
import ChessGame

class MinimaxAI():
    def __init__(self, depth = 3, eval_fcn = None):
        self.depth = depth
        self.eval_fcn = eval_fcn or self.pieces_eval #default based on piece value

    def choose_move(self, board: None):
        moves = list(board.legal_moves)
        if not moves:
            return None  #  no-move possible
        #get root color 
        c = board.turn
        bestVal = -inf
        bestMove = None

        for move in moves:
            board.push(move)
            v = self.min_value(board, self.depth - 1, c)
            board.pop()
            if v > bestVal:
                bestVal = v
                bestMove = move

        if bestMove is None:
            # should not happen, but just in case
            legal = list(board.legal_moves)
            if not legal:
                raise RuntimeError("No legal moves available in choose_move")
            bestMove = legal[0]
        return bestMove

#stops minimax whenn we have reached either temrinal state(win/draw) or the max depth
    def cutoff_test(self, board: None, depth = int):
        return depth ==0 or board.is_game_over()
    
    #max value fcn
    def max_value(self, board: None, depth: int, c: bool):
        if self.cutoff_test(board, depth):
            return self.evaluate(board, c)
        v = -inf

        #iterate through all legal moves
        for move in board.legal_moves:
            board.push(move)
            v = max(v, self.min_value(board, depth - 1, c))
            board.pop()
        return v

    #min value fcn
    def min_value(self, board: None, depth: int, c: bool):
        if self.cutoff_test(board, depth):
            return self.evaluate(board, c)
        v = inf
        
        #iterate through all legal moves
        for move in board.legal_moves:
            board.push(move)
            v = min(v, self.max_value(board, depth - 1, c))
            board.pop()
        return v

    #evaluate fcn
    def evaluate(self, board: None, c: bool):
        util = self.terminal(board, c)
        if util is not None:
            return util
        return self.eval_fcn(board, c)

    #terminal fcn checks for checkmate, stalemate, or messed up state
    def terminal(self, board: None, c: bool):
        if board.is_checkmate():
            winner = not board.turn  # winner is the side that just moved
            return inf if winner == c else -inf
       #draw
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
        return None

    def pieces_eval(self, board: None, c: bool):
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 350,
            chess.BISHOP: 360,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0,
        }
        score = 0
        for piece_type, val in values.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * val
            score -= len(board.pieces(piece_type, chess.BLACK)) * val
        return float(score) if c == chess.WHITE else float(-score)


