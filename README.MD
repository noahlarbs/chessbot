###ReadMe for Chess AI PA3
#Code Modified/written by Larbalestier, Noah; F006B9P
#26 October 2025
#PA3 COSC 076, 25F
#Scaffold and Driver given by Professor Soroush Vosoughi
#various search/driver modules for chess games

need:
- Python 3 (tested with python3.11.9)
- python-chess: i
- PyQt5 for the GUI:
- python-math

Main files modified / used
- AlphaBetaAI.py (ABAI)
  - Depth-lim alpha–beta search 
  - Has an order_moves helper to order captures / PV / checks (helps pruning)
    - NOTE* this order_moves is fairly arbitrary and often just prefs the previous, a better implementation  tracks via more organized tuples of some meaningful chess features 
- MinimaxAI.py (MmAI)
  - Simple minimax (no alpha–beta)
  - Public API: choose_move(board) — returns a chess.Move
- IDAI.py (IDS wrapper)
  - Iterative deepening wrapper around AlphaBetaAI
  - ideally one might create a time per move budget
  - principal variation (PV) for move ordering and prints progress by depth
- ChessGame.py
  -  game loop wrapper holds a python-chess Board and two players
  - make_move() calls player.choose_move(board) and pushes the move 
- test_chess.py
  - Simple CL driver that creates two AIs and runs a game loop, printing positions and final result


How to run:

Run the test driver:
   ```
   python3 test_chess.py
   ```
If you want the GUI (requires PyQt5):
   ```
   python3 gui_chess.py
   ```
To play against the AB algo:
    ```
    python3 playab.py
    ```

    