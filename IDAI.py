#Code Modified/writter by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#Iterative Deepening Search module for chess

import math
import time
from typing import Dict, Optional

import chess
from AlphaBetaAI import AlphaBetaAI


class SearchLimitReached(Exception):
    """Raised when the search must terminate due to time or node limits."""
    pass


class IDAI(AlphaBetaAI):
    # inits iterative deepning with max depth 3 by default
    def __init__(self, depth: int = 3, eval_fcn=None, *, max_nodes: Optional[int] = None,
                 safety_margin: float = 0.05, branching_threshold: int = 30,
                 low_branching_threshold: int = 8):
        super().__init__(depth= depth, eval_fcn=eval_fcn)
        self.best_move = None
        self.max_nodes = max_nodes
        self.safety_margin = safety_margin
        self.branching_threshold = branching_threshold
        self.low_branching_threshold = low_branching_threshold
        self._avg_time_per_node: Optional[float] = None
        self._nodes_per_depth: Dict[int, float] = {}
        self._start_time: Optional[float] = None
        self._time_budget: Optional[float] = None
        self._node_count: int = 0
        self._stop_search: bool = False

    def choose_move(self, board: chess.Board, time_budget: Optional[float] = None):
        # new best move for this turn
        self.best_move = None
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        self._start_time = time.perf_counter()
        self._time_budget = time_budget
        self._node_count = 0
        self._stop_search = False

        max_depth = self._select_search_depth(board, time_budget)
        c = board.turn  # color

        # deepen from 1..max_depth
        for depth in range(1, max_depth + 1):
            bestVal = -math.inf
            bestMove = None
            alpha = -math.inf
            beta = math.inf
            depth_completed = True
            depth_start_time = time.perf_counter()
            nodes_before = self._node_count

            # prefer prev found best move for move ordering
            if self.best_move is not None and self.best_move in legal_moves:
                ordered_moves = [self.best_move] + [m for m in legal_moves if m != self.best_move]
            else:
                ordered_moves = legal_moves
            try:
                for move in ordered_moves:
                    self._check_limits()
                    board.push(move)
                    try:
                        v = self.min_value(board, depth - 1, c, alpha, beta)
                    finally:
                        board.pop()
                    if v > bestVal:
                        bestVal = v
                        bestMove = move
                    if bestVal > alpha:
                        alpha = bestVal
            except SearchLimitReached:
                depth_completed = False

            if depth_completed:
                if bestMove is None:
                    legal = list(board.legal_moves)
                    if not legal:
                        raise RuntimeError("No legal moves available in choose_move")
                    bestMove = legal[0]

                # store best move found at depth
                self.best_move = bestMove
                self.pv = bestMove
                depth_nodes = self._node_count - nodes_before
                depth_elapsed = time.perf_counter() - depth_start_time
                self._record_depth_statistics(depth, depth_nodes, depth_elapsed)

                # print progress
                print(f"the best move at depth {depth} is {self.best_move} (value {bestVal})")

                # early exit if result (checkmate found)
                if abs(bestVal) == math.inf:
                    break
            else:
                break

        if self.best_move is None:
            self.best_move = legal_moves[0]

        self._time_budget = None
        self._start_time = None
        self._stop_search = False

        return self.best_move

    def max_value(self, board: chess.Board, depth: int, c: bool, alpha: float, beta: float):
        self._check_limits()
        self._node_count += 1
        if self.cutoff_test(board, depth):
            return self.evaluate(board, c)
        v = -math.inf
        moves = list(board.legal_moves)

        for move in self.order_moves(board, moves, pv=self.pv):
            self._check_limits()
            board.push(move)
            try:
                v = max(v, self.min_value(board, depth - 1, c, alpha, beta))
            finally:
                board.pop()
            if v >= beta:
                return v
            if v > alpha:
                alpha = v
        return v

    def min_value(self, board: chess.Board, depth: int, c: bool, alpha: float, beta: float):
        self._check_limits()
        self._node_count += 1
        if self.cutoff_test(board, depth):
            return self.evaluate(board, c)
        v = math.inf
        moves = list(board.legal_moves)

        for move in self.order_moves(board, moves, pv=self.pv):
            self._check_limits()
            board.push(move)
            try:
                v = min(v, self.max_value(board, depth - 1, c, alpha, beta))
            finally:
                board.pop()
            if v <= alpha:
                return v
            if v < beta:
                beta = v
        return v

    def _check_limits(self):
        if self._stop_search:
            raise SearchLimitReached
        if self._time_budget is not None and self._start_time is not None:
            elapsed = time.perf_counter() - self._start_time
            if elapsed >= max(0.0, self._time_budget - self.safety_margin):
                self._stop_search = True
                raise SearchLimitReached
        if self.max_nodes is not None and self._node_count >= self.max_nodes:
            self._stop_search = True
            raise SearchLimitReached

    def _record_depth_statistics(self, depth: int, nodes: int, elapsed: float):
        if nodes <= 0:
            return
        prev_nodes = self._nodes_per_depth.get(depth)
        if prev_nodes is None:
            self._nodes_per_depth[depth] = float(nodes)
        else:
            self._nodes_per_depth[depth] = 0.5 * prev_nodes + 0.5 * float(nodes)
        rate = elapsed / nodes
        if self._avg_time_per_node is None:
            self._avg_time_per_node = rate
        else:
            self._avg_time_per_node = 0.7 * self._avg_time_per_node + 0.3 * rate

    def _select_search_depth(self, board: chess.Board, time_budget: Optional[float]) -> int:
        legal_count = sum(1 for _ in board.legal_moves)
        target_depth = self.depth

        if legal_count >= self.branching_threshold:
            target_depth = max(1, target_depth - 1)
        elif legal_count <= self.low_branching_threshold:
            target_depth = target_depth + 1

        target_depth = max(1, min(target_depth, self.depth + 1))

        expected_nodes = sum(self._nodes_per_depth.get(d, 0.0) for d in range(1, target_depth + 1))
        if expected_nodes <= 0:
            expected_nodes = target_depth * 100.0

        if self.max_nodes is not None and expected_nodes > self.max_nodes:
            while target_depth > 1 and expected_nodes > self.max_nodes:
                expected_nodes -= self._nodes_per_depth.get(target_depth, 0.0)
                target_depth -= 1

        if time_budget is not None and self._avg_time_per_node is not None:
            available_time = max(0.0, time_budget - self.safety_margin)
            while target_depth > 1 and expected_nodes * self._avg_time_per_node > available_time:
                expected_nodes -= self._nodes_per_depth.get(target_depth, 0.0)
                target_depth -= 1

        return max(1, target_depth)
