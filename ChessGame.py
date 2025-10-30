#Code Modified/writter by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#chessgame module for chess
#added legal move check

import chess

class ChessGame:
    def __init__(self, player1, player2):
        self.board = chess.Board()
        self.players = [player1, player2]

    def make_move(self):

        player = self.players[1 - int(self.board.turn)]
        move = player.choose_move(self.board)

        if move is None:
            # debug output to identify the broken AI and fallback to a legal move
            print(f"ERROR: {player.__class__.__name__}.choose_move returned None")
            print("Board FEN:", self.board.fen())
            legal = list(self.board.legal_moves)
            print("Legal moves (first 30):", legal[:30])
            
            if not legal:
                raise RuntimeError(f"No legal moves available and {player.__class__.__name__} returned None")
            # fallback: pick the first legal move to keep the game running
            move = legal[0]
            print(f"Falling back to first legal move: {move}")

        self.board.push(move)  # Make the move

    def is_game_over(self):
        return self.board.is_game_over()

    def __str__(self):

        column_labels = "\n----------------\na b c d e f g h\n"
        board_str =  str(self.board) + column_labels

        # did you know python had a ternary conditional operator? yes
        move_str = "White to move" if self.board.turn else "Black to move"

        return board_str + "\n" + move_str + "\n"
