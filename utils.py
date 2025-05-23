import copy
import multiprocessing
import sys
import os
import time
import timeout_decorator
import functools
from threading import Thread

# board row and column -> these are constant
ROW, COL = 6, 6

# generates initial state
def generate_init_state():
    state = [
        ['B']*COL, ['B']*COL, # 2 black rows
        ['_']*COL, ['_']*COL, # 2 empty rows
        ['W']*COL, ['W']*COL, # 2 white rows
    ]
    return state

# prints board
def print_state(board):
    horizontal_rule = '+' + ('-'*5 + '+') * COL
    for i in range(len(board)):
        print(horizontal_rule)
        print('|  ' +  '  |  '.join(' ' if board[i][j] == '_' else board[i][j] for j in range(COL)) + '  |')
    print(horizontal_rule)

# inverts board by modifying board state, or returning a new board with updated board state
def invert_board(curr_board, in_place=True):
    ''' Inverts the board by modifying existing values if in_place is set to True, or creating a new board with updated values if in_place is set to False'''
    board = curr_board
    if not in_place:
        board = copy.deepcopy(curr_board)
    board.reverse()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 'W':
                board[i][j] = 'B'
            elif board[i][j] == 'B':
                board[i][j] = 'W'
    return board

# checks if a move made for black is valid or not. Move source: from_ [row, col], move destination: to_ [row, col]
def is_valid_move(board, from_, to_):
    if board[from_[0]][from_[1]] != 'B': # if move not made for black
        return False
    elif (to_[0]<0 or to_[0]>=ROW) or (to_[1]<0 or to_[1]>=COL): # if move takes pawn outside the board
        return False
    elif to_[0]!=(from_[0]+1): # if move takes more than one step forward
        return False
    elif to_[1]>(from_[1]+1) or to_[1]<(from_[1]-1): # if move takes beyond left/ right diagonal
        return False
    elif to_[1]==from_[1] and board[to_[0]][to_[1]]!='_': # if pawn to the front, but still move forward
        return False
    elif ((to_[1]==from_[1]+1) or (to_[1]==from_[1]-1)) and board[to_[0]][to_[1]]=='B': # if black pawn to the diagonal or front, but still move forward
        return False
    else:
        return True

# generates the first available valid move for black
def generate_rand_move(board):
    from_, to_ = [0, 0], [0, 0]
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j]=='B':
                from_[0], from_[1] = i, j
                to_[0] = from_[0] + 1
                to_[1] = from_[1]
                if is_valid_move(board, from_, to_):
                    return from_, to_
                to_[1] = from_[1] + 1
                if is_valid_move(board, from_, to_):
                    return from_, to_
                to_[1] = from_[1] - 1
                if is_valid_move(board, from_, to_):
                    return from_, to_

# makes a move effective on the board by modifying board state, or returning a new board with updated board state
def state_change(curr_board, from_, to_, in_place=True):
    ''' Updates the board configuration by modifying existing values if in_place is set to True, or creating a new board with updated values if in_place is set to False '''
    board = curr_board
    if not in_place:
        board = copy.deepcopy(curr_board)
    if is_valid_move(board, from_, to_):
        board[from_[0]][from_[1]] = '_'
        board[to_[0]][to_[1]] = 'B'
    return board

# checks if game is over
def is_game_over(board):
    ''' Returns True if game is over '''
    flag = any(
        board[ROW-1][i] == 'B' or \
        board[0][i] == 'W'
        for i in range(COL)
    )

    wcount, bcount = 0, 0
    for i in range(ROW):
        for j in range(COL):
            if board[i][j] == 'B':
                bcount+=1
            elif board[i][j] == 'W':
                wcount+=1
    
    if wcount==0 or bcount==0:
        flag = True
    
    return flag


#############################################
# Utils function for game playing framework #
# ############################################

# move making function for game playing
def make_move_job_func(player, board, queue):
    # disable stdout and stderr to prevent prints
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    try:
        src, dst = player.make_move(board) # returns [i1, j1], [i2, j2] -> pawn moves from position [i1, j1] to [i2, j2]
        queue.put((src, dst))
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        queue.put(e)
        exit(1)
    finally:
        # reenable stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    return

# game playing function. Takes in the initial board
def play(playerAI_A, playerAI_B, board):
    COLOURS = [BLACK, WHITE] = 'Black(Student agent)', 'White(Test agent)'
    TIMEOUT = 3
    random_moves = 0
    PLAYERS = []
    move = 0

    # disable stdout for people who leave print statements in their code, disable stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    try:
        PLAYERS.append(playerAI_A)
    except KeyboardInterrupt:
        exit()
    except:
        return f"{BLACK} failed to initialise"
    finally:
        # reenable stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
    # disable stdout for people who leave print statements in their code, disable stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    try:
        PLAYERS.append(playerAI_B)
    except KeyboardInterrupt:
        exit()
    except:
        return f"{WHITE} failed to initialise"
    finally:
        # reenable stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    # game starts
    while not is_game_over(board):
        player = PLAYERS[move % 2]
        colour = COLOURS[move % 2]
        src, dst = -1, -1
        if colour == WHITE:
            invert_board(board)
            src, dst = player.make_move(board)
        else: # BLACK
            board_copy = copy.deepcopy(board)
            start_time = time.time()
            src, dst = player.make_move(board_copy)
            end_time = time.time()
            
            isValid = False
            try:
                isValid = is_valid_move(board, src, dst) and end_time - start_time <= TIMEOUT
            except KeyboardInterrupt:
                exit()
            except Exception:
                isValid = False
            if not isValid: # if move is invalid or time is exceeded, then we give a random move
                random_moves += 1
                src, dst = generate_rand_move(board)
        
        state_change(board, src, dst) # makes the move effective on the board
        if colour == WHITE:
            invert_board(board)
        move += 1
    
    return f"{colour} win; Random move made by {BLACK}: {random_moves};"

# decorator for first three public test cases
def wrap_test(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f'FAILED, reason: {str(e)}'
    return inner

TIME_LIMIT = 3.05

class TimeoutException(Exception):
    pass

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [TimeoutException('Function [%s] exceeded timeout of [%s seconds]' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('Error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

@wrap_test
@timeout_decorator.timeout(TIME_LIMIT)
def test(board, playerAI):
    board_copy = copy.deepcopy(board)
    start = time.time()
    src, dst = playerAI.make_move(board_copy)
    end = time.time()
    move_time = end - start
    valid = is_valid_move(board, src, dst)
    return valid and move_time<=3


@wrap_test
@timeout(TIME_LIMIT)
def test_windows(board, playerAI):
    board_copy = copy.deepcopy(board)
    start = time.time()
    src, dst = playerAI.make_move(board_copy)
    end = time.time()
    move_time = end - start
    valid = is_valid_move(board, src, dst)
    return valid and move_time<=3

if os.name == "nt":
    test = test_windows
