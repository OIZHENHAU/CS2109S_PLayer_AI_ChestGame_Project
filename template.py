import utils
import time
import copy


class PlayerAI:
    # def make_move(self, board):
        '''
        This is the function that will be called from main.py
        Your function should implement a minimax algorithm with 
        alpha beta pruning to select the appropriate move based 
        on the input board state. Play for black.

        Parameters
        ----------
        self: object instance itself, passed in automatically by Python
        board: 2D list-of-lists
        Contains characters 'B', 'W', and '_' representing
        Black pawns, White pawns and empty cells respectively
        
        Returns
        -------
        Two lists of coordinates [row_index, col_index]
        The first list contains the source position of the Black pawn 
        to be moved, the second list contains the destination position
        '''

        def make_move(self, board):
            import time
            self.start_time = time.time()  # ✅ Initialize the start time here
            self.time_limit = 4.9  # Optional: a small buffer under 5 seconds
            depth = 20
            eval, move = self.minimax(board, depth, float('-inf'), float('inf'), True)

            if move is None:
                print("⚠️ Minimax returned None, falling back to random move.")

            return move

        def minimax(self, board, depth, alpha, beta, maximizing_player):
            if depth == 0 or utils.is_game_over(board) or (time.time() - self.start_time) > self.time_limit:
                return self.evaluate_board(board), None

            if maximizing_player:
                max_eval = float('-inf')
                best_move = None
                for move in self.generate_all_moves(board, 'B'):
                    new_board = utils.state_change(copy.deepcopy(board), move[0], move[1], in_place=False)
                    eval, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval, best_move
            else:
                min_eval = float('inf')
                best_move = None
                inverted_board = utils.invert_board(copy.deepcopy(board), in_place=False)
                for move in self.generate_all_moves(inverted_board, 'B'):
                    new_board = utils.state_change(copy.deepcopy(inverted_board), move[0], move[1], in_place=False)
                    reverted_board = utils.invert_board(new_board, in_place=False)
                    eval, _ = self.minimax(reverted_board, depth - 1, alpha, beta, True)
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval, best_move

        def evaluate_board(self, board):
            black_score = 0
            white_score = 0
            for r in range(6):
                for c in range(6):
                    if board[r][c] == 'B':
                        black_score += (r + 1)
                    elif board[r][c] == 'W':
                        white_score += (6 - r)
            return black_score - white_score

        def generate_all_moves(self, board, player):
            moves = []
            for r in range(6):
                for c in range(6):
                    if board[r][c] == player:
                        directions = [(1, 0), (1, -1), (1, 1)] if player == 'B' else [(-1, 0), (-1, -1), (-1, 1)]
                        for dr, dc in directions:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 6 and 0 <= nc < 6:
                                if board[nr][nc] == '_':
                                    if dr == 1 and dc == 0:
                                        moves.append(([r, c], [nr, nc]))
                                    elif dr == 1 and abs(dc) == 1:
                                        moves.append(([r, c], [nr, nc]))
                                elif board[nr][nc] == ('W' if player == 'B' else 'B') and abs(dc) == 1:
                                    moves.append(([r, c], [nr, nc]))
            return moves

class PlayerNaive:
    ''' A naive agent that will always return the first available valid move '''
    def make_move(self, board):
        return utils.generate_rand_move(board)


##########################
# Game playing framework #
##########################
if __name__ == "__main__":

    # public test case 1
    res1 = utils.test([['B', 'B', 'B', 'B', 'B', 'B'], ['_', 'B', 'B', 'B', 'B', 'B'], ['_', '_', '_', '_', '_', '_'], ['_', 'B', '_', '_', '_', '_'], ['_', 'W', 'W', 'W', 'W', 'W'], ['W', 'W', 'W', 'W', 'W', 'W']], PlayerAI())
    # assert(res1 == True)

    # public test case 2
    res2 = utils.test([['_', 'B', 'B', 'B', 'B', 'B'], ['_', 'B', 'B', 'B', 'B', 'B'], ['_', '_', '_', '_', '_', '_'], ['_', 'B', '_', '_', '_', '_'], ['W', 'W', 'W', 'W', 'W', 'W'], ['_', '_', 'W', 'W', 'W', 'W']], PlayerAI())
    # assert(res2 == True)

    # public test case 3
    res3 = utils.test([['_', '_', 'B', 'B', 'B', 'B'], ['_', 'B', 'B', 'B', 'B', 'B'], ['_', '_', '_', '_', '_', '_'], ['_', 'B', 'W', '_', '_', '_'], ['_', 'W', 'W', 'W', 'W', 'W'], ['_', '_', '_', 'W', 'W', 'W']], PlayerAI())
    # assert(res3 == True)

    # template code for question 2 and question 3
    # generates initial board
    board = utils.generate_init_state()
    # game play
    res = utils.play(PlayerAI(), PlayerNaive(), board) # PlayerNaive() will be replaced by a baby agent in question 2, or a base agent in question 3
    print(res) # BLACK wins means your agent wins. Passing the test case on Coursemology means your agent wins.
