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
    def __init__(self, depth = 3, eval_fcn = None, weights = None, extension_cap: int = 2):
        self.depth = depth
        self.extension_cap = extension_cap
        default_weights = {
            "material": 1.0,
            "piece_square": 0.1,
            "king_safety": 0.2,
            "mobility": 0.05,
        }
        if weights:
            default_weights.update(weights)
        self.weights = default_weights
        self.eval_fcn = eval_fcn or self.pieces_eval
        self.pv = None
        self.piece_square_tables = self._create_piece_square_tables()
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
            value = self.min_value(board, self.depth - 1, c, alpha, beta, 1)
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


    def cutoff_test(self, board: chess.Board, depth: int, ply: int):
        if board.is_game_over():
            return True
        if ply >= self.depth + self.extension_cap:
            return True
        if depth > 0:
            return False
        if self._should_extend(board):
            return False
        return True
    #max value fcn - tries to maximize score
    def max_value(self, board: chess.Board, depth: int, c: bool, alpha: float, beta: float, ply: int):
        if self.cutoff_test(board, depth, ply):
            return self.evaluate(board, c)
        v = -inf
        moves = list(board.legal_moves)

        for move in self.order_moves(board, moves, pv=self.pv):
            board.push(move)
            v = max(v, self.min_value(board, depth - 1, c, alpha, beta, ply + 1))
            board.pop()
            if v >= beta:
                return v
            if v > alpha:
                alpha = v
        return v
    # min value fcn - tries to minimize score
    def min_value(self, board: chess.Board, depth: int, c: bool, alpha: float, beta: float, ply: int):
        if self.cutoff_test(board, depth, ply):
            return self.evaluate(board, c)
        v = inf
        moves = list(board.legal_moves)

        for move in self.order_moves(board, moves, pv=self.pv):
            board.push(move)
            v = min(v, self.max_value(board, depth - 1, c, alpha, beta, ply + 1))
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
    
    def pieces_eval(self, board: chess.Board, c: bool):
        material = self._material_score(board)
        piece_square = self._piece_square_score(board)
        king_safety = self._king_safety_score(board)
        mobility = self._mobility_score(board)

        score = (
            self.weights["material"] * material
            + self.weights["piece_square"] * piece_square
            + self.weights["king_safety"] * king_safety
            + self.weights["mobility"] * mobility
        )
        return float(score) if c == chess.WHITE else float(-score)

    def composite_eval(self, board: chess.Board, c: bool):
        return self.pieces_eval(board, c)

    def _material_score(self, board: chess.Board) -> float:
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0,
        }
        score = 0
        for piece_type, val in values.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * val
            score -= len(board.pieces(piece_type, chess.BLACK)) * val
        return float(score)

    def _piece_square_score(self, board: chess.Board) -> float:
        score = 0
        for piece_type, table in self.piece_square_tables.items():
            for square in board.pieces(piece_type, chess.WHITE):
                score += table[square]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= table[chess.square_mirror(square)]
        return float(score)

    def _king_safety_score(self, board: chess.Board) -> float:
        white = self._king_safety_for_color(board, chess.WHITE)
        black = self._king_safety_for_color(board, chess.BLACK)
        return white - black

    def _king_safety_for_color(self, board: chess.Board, color: bool) -> float:
        king_square = board.king(color)
        if king_square is None:
            return 0.0

        file_index = chess.square_file(king_square)
        rank_index = chess.square_rank(king_square)
        direction = 1 if color == chess.WHITE else -1

        shield_score = 0
        for df in (-1, 0, 1):
            target_file = file_index + df
            if 0 <= target_file <= 7:
                forward_rank = rank_index + direction
                if 0 <= forward_rank <= 7:
                    square = chess.square(target_file, forward_rank)
                    piece = board.piece_at(square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        shield_score += 15

        open_file_penalty = 0
        if not self._has_pawn_on_file(board, color, file_index):
            open_file_penalty -= 20

        open_file_penalty += self._open_file_threat(board, color, king_square)
        return float(shield_score + open_file_penalty)

    def _has_pawn_on_file(self, board: chess.Board, color: bool, file_index: int) -> bool:
        for rank in range(8):
            square = chess.square(file_index, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                return True
        return False

    def _open_file_threat(self, board: chess.Board, color: bool, king_square: chess.Square) -> float:
        file_index = chess.square_file(king_square)
        rank_index = chess.square_rank(king_square)
        penalty = 0

        ranks = range(rank_index + 1, 8) if color == chess.WHITE else range(rank_index - 1, -1, -1)
        for r in ranks:
            square = chess.square(file_index, r)
            piece = board.piece_at(square)
            if piece is None:
                continue
            if piece.color == color:
                break
            if piece.piece_type in (chess.ROOK, chess.QUEEN):
                penalty -= 30
            break

        return float(penalty)

    def _mobility_score(self, board: chess.Board) -> float:
        original_turn = board.turn
        try:
            board.turn = chess.WHITE
            white_moves = board.legal_moves.count()
            board.turn = chess.BLACK
            black_moves = board.legal_moves.count()
        finally:
            board.turn = original_turn
        return float(white_moves - black_moves)

    def _create_piece_square_tables(self):
        return {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5, 5, 10, 25, 25, 10, 5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, -5, -10, 0, 0, -10, -5, 5,
                5, 10, 10, -20, -20, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0,
            ],
            chess.KNIGHT: [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50,
            ],
            chess.BISHOP: [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -10, -10, -10, -10, -10, -20,
            ],
            chess.ROOK: [
                0, 0, 5, 10, 10, 5, 0, 0,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 5, 5, 0, 0, -5,
                -5, 0, 0, 5, 5, 0, 0, -5,
                -5, 0, 0, 5, 5, 0, 0, -5,
                -5, 0, 0, 5, 5, 0, 0, -5,
                5, 10, 10, 10, 10, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0,
            ],
            chess.QUEEN: [
                -20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 5, 0, 0, 0, 0, -10,
                -10, 5, 5, 5, 5, 5, 0, -10,
                0, 0, 5, 5, 5, 5, 0, -5,
                -5, 0, 5, 5, 5, 5, 0, -5,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20,
            ],
            chess.KING: [
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                20, 20, 0, 0, 0, 0, 20, 20,
                20, 30, 10, 0, 0, 10, 30, 20,
            ],
        }

    def _should_extend(self, board: chess.Board) -> bool:
        if board.is_check():
            return True
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return False
        captures = [move for move in legal_moves if board.is_capture(move)]
        return bool(captures) and len(captures) == len(legal_moves)
