#Code Modified/writter by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#Alpha Beta Search module for chess

import chess
from math import inf

#alphabeta ai class, for chess game
#if not specificed, depth of 3
class AlphaBetaAI():
    def __init__(self, depth = 3, eval_fcn = None):
        self.depth = depth
        self.eval_fcn = eval_fcn or self.pieces_eval
        self.pv = None
    # simple move ordering helper (PV, checks)
    def order_moves(self, board, moves, pv=None):
        
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 350,
            chess.BISHOP: 360,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0,
        }

        scored = []
        # score moves 
        for move in moves:
            score = 0
            # principal variation - best move found in previous search
            if pv is not None and move == pv:
                #we add 20000 to make sure pv is highest scored
                score += 20000
                # is capture  from chess lib - gives higher score to captures
                #victim and attacker piece values used for quanitfy val of captures

            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                victim_val = values.get(victim.piece_type, 0) if victim else 0
                attacker = board.piece_at(move.from_square)
                attacker_val = values.get(attacker.piece_type, 0) if attacker else 0
                score += 1000 + (victim_val - attacker_val)
            board.push(move)
            if board.is_check():
                score += 50
            board.pop()
            scored.append((score, move))
            # sort moves by score descending
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored]
    
    #returns best move for curr board state
    #alpha + beta work with minimax to prune branches
    #alpha is the best score the max could get
    #beta is the best score the min could get
    #basically same as minimax otherwise
    
    def choose_move(self, board: chess.Board):
        c = board.turn
        bestVal = -inf
        bestMove = None
        alpha = -inf
        beta = inf
        moves = list(board.legal_moves)
        ordered = self.order_moves(board, moves, pv=self.pv)

        for move in ordered:
            board.push(move)
            value = self.min_value(board, self.depth - 1, c, alpha, beta)
            board.pop()

            if value > bestVal:
                bestVal = value
                bestMove = move

            if bestVal > alpha:
                alpha = bestVal

        if bestMove is not None:
            self.pv = bestMove

        if bestMove is None:
            # should not happen, but just in case
            legal = list(board.legal_moves)
            if not legal:
                raise RuntimeError("No legal moves available in choose_move")
            bestMove = legal[0]
        return bestMove


    def cutoff_test(self, board: chess.Board, depth: int):
        return depth == 0 or board.is_game_over()
    #max value fcn - tries to maximize score
    def max_value(self, board: chess.Board, depth: int, c: bool, alpha: float, beta: float):
        if self.cutoff_test(board, depth):
            return self.evaluate(board, c)
        v = -inf
        moves = list(board.legal_moves)

        for move in self.order_moves(board, moves, pv=self.pv):
            board.push(move)
            v = max(v, self.min_value(board, depth - 1, c, alpha, beta))
            board.pop()
            if v >= beta:
                return v
            if v > alpha:
                alpha = v
        return v
    # min value fcn - tries to minimize score
    def min_value(self, board: chess.Board, depth: int, c: bool, alpha: float, beta: float):
        if self.cutoff_test(board, depth):
            return self.evaluate(board, c)
        v = inf
        moves = list(board.legal_moves)

        for move in self.order_moves(board, moves, pv=self.pv):
            board.push(move)
            v = min(v, self.max_value(board, depth - 1, c, alpha, beta))
            board.pop()
            if v <= alpha:
                return v
            if v < beta:
                beta = v
        return v
    

    # if terminal state, return utility val, else use pieces
    def evaluate(self, board: chess.Board, c: bool):
        util = self.terminal(board, c)
        if util is not None:
            return util
        return self.eval_fcn(board, c)
    
    # evals for terminal state
    def terminal(self, board: chess.Board, c: bool):
        if board.is_checkmate():
            winner = not board.turn
            return inf if winner == c else -inf
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
        return None
    
    #evaluation function
    #based on material value of pieces
    def pieces_eval(self, board: chess.Board, c: bool):
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0,
        }
        score = 0
        # now tally up scores
        for piece_type, val in values.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * val
            score -= len(board.pieces(piece_type, chess.BLACK)) * val
        return float(score) if c == chess.WHITE else float(-score)
