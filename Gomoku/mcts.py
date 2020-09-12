from __future__ import absolute_import, division, print_function
from math import sqrt, log
from random import *
import math
import copy

#Feel free to add extra classes and functions

class State:
    def __init__(self, grid, player):
        self.grid = grid
        self.maxrc = len(grid)-1
        self.piece = player
        self.grid_size = 52
        self.grid_count = 11
        self.wins = 0
        self.visits = 1
        self.children = []
        self.parent = 0
        self.options = self.get_options(grid)
        self.terminate = False;
        self.sure_win = False


    def check_win(self, r, c):
        #north direction (up)
        n_count = self.get_continuous_count(r, c, -1, 0)
        #south direction (down)
        s_count = self.get_continuous_count(r, c, 1, 0)
        #east direction (right)
        e_count = self.get_continuous_count(r, c, 0, 1)
        #west direction (left)
        w_count = self.get_continuous_count(r, c, 0, -1)
        #south_east diagonal (down right)
        se_count = self.get_continuous_count(r, c, 1, 1)
        #north_west diagonal (up left)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        #north_east diagonal (up right)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        #south_west diagonal (down left)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
                return True
        return False

    def make_move(self):
        return random.choice(self.get_options(self.grid))

    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    def get_options(self, grid):
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(5, 5)]
        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        return options

class MCTS:
    def __init__(self, grid, player):
        self.root = State(grid, player)
        self.grid = grid


    def uct_search(self):
        i = 0
        # MCTS Algorithm
        while i < 50:
            s = self.selection(self.root)
            winner = self.simulation(s)
            self.backpropagation(s, winner)
            i = i + 1
        # The value in children are all finished set up, find the best move
        children = self.root.children
        result = 0
        index = 0
        # Make the final choice among children
        for i in range(len(children)):
            child = children[i]
            #if child.sure_win == True:
                #return child.action
            value = child.wins / child.visits
            if result < value:
                result = value
                index = i
        return children[index].action
        #child = self.best_child(self.root)
        #return child.action

    def selection(self, state):
        while state.terminate != True:
            # When the state still has available options to take, it is still expendable
            if len(state.options) != 0:
                return self.expansion(state)
            # Not expendable
            else:
                state = self.best_child(state)
        return state

    def expansion(self, state):
        color = state.piece
        if color == self.root.piece:
            if self.check_empty(state.grid, self.root.piece) == True:
                state.options = self.reset_option(state.options, state.grid, self.root.piece)
        # child has opposite piece
        if(color == 'b'):
            color = 'w'
        else:
            # For white player, I try to avoid the play which the position has no other white pieces around it
            #if self.check_empty(state.grid, 'w') == True:
               # state.options = self.reset_option(state.options, state.grid)
            color = 'b'
        index =randint(0,len(state.options)-1)
        move = state.options[index]
        # The grid at the next move
        new_grid = copy.deepcopy(state.grid)
        new_grid[move[0]][move[1]] = state.piece
        # Create and set up child node
        child = State(new_grid, color)
        child.action = move
        child.parent = state
        if state.piece == self.root.piece:
            value = self.check_for_good_move(child.grid, state.piece, move[0], move[1])
            child.wins += value
        # If this action ends the game, this child is a terminate node
        if child.check_win(move[0], move[1]) == True:
            child.terminate = True
            child.wins += 1;
            #if(state.piece == 'w'):
                #child.sure_win = True
        # If this child has no option, board is full, terminate node and white is the winner
        if len(child.options) == 0:
            child.terminate = True
            if(self.root.piece == 'w'):
                child.wins = child.wins + 1;
        state.children.append(child)
        # Pop this move 
        state.options.pop(index)
        return child

    def best_child(self, state):
        result = 0
        index = 0;
        # Follow the example of MCTS child evaluation
        for i in range(len(state.children)):
            # Number of wins of s'
            Qs = state.children[i].wins
            # Number of visits of s
            Nsp = state.children[i].visits
            # Number of visits of s'
            Ns = state.visits
            # The algorithm
            value = Qs/Nsp + sqrt(math.log(Ns)/Nsp)
            if result < value:
                result = value
                index = i
        return state.children[index]

    def simulation(self, state):
        s = copy.deepcopy(state)
        while s.terminate == False:
            # Simulate next move for white's turn
            if(s.piece == 'w'):
                # Optimaize the option
                s.options = self.reset_option(s.options, s.grid, 'w')
                index = randint(0,len(s.options)-1)
                move = s.options[index]
                new_grid = copy.deepcopy(s.grid)
                new_grid[move[0]][move[1]] = 'w'
                s = State(new_grid, 'b')
                # Check for the win
                if(s.check_win(move[0], move[1])==True):
                    return 'w'
            # Simulate next move for black's turn
            else:
                index = randint(0,len(s.options)-1)
                move = s.options[index]
                new_grid = copy.deepcopy(s.grid)
                new_grid[move[0]][move[1]] = 'b'
                s = State(new_grid, 'w')
                # Check for the win
                if(s.check_win(move[0], move[1])==True):
                    return 'b'
            
    # Go back up the tree and set up the value
    def backpropagation(self, state, result):
        while state != 0:
            state.visits = state.visits + 1
            if state.piece!=result:
                #print("Add winner")
                state.wins = state.wins + 1
            state = state.parent

    # Optimize the choices for white player, making sure there's no move that is isolated in a spot
    def reset_option(self, options, grid, player):
        result = []
        copy_grid = grid
        for i in range(len(options)):
            move = options[i]
            if(move[0]-1>=0):
                # Left has white
                if(copy_grid[move[0]-1][move[1]]==player):
                    result.append(move)
                    continue
                if(move[1]+1<11):
                    # Left down has white
                    if(copy_grid[move[0]-1][move[1]+1]==player):
                        result.append(move)
                        continue
                    # down has white
                    if(copy_grid[move[0]][move[1]+1]==player):
                        result.append(move)
                        continue
                if(move[1]-1>=0):
                    # Left up has white
                    if(copy_grid[move[0]-1][move[1]-1]==player):
                        result.append(move)
                        continue
                    # Up has white
                    if(copy_grid[move[0]][move[1]-1]==player):
                        result.append(move)
                        continue
            if(move[0]+1<11):
                # Right has white
                if(copy_grid[move[0]+1][move[1]]==player):
                    result.append(move)
                    continue
                if(move[1]+1<11):
                    # Right down has white
                    if(copy_grid[move[0]+1][move[1]+1]==player):
                        result.append(move)
                        continue
                if(move[1]-1 >= 0):
                    # Right up has white
                    if(copy_grid[move[0]+1][move[1]-1]==player):
                        result.append(move)
                        continue
        return result

    # Check if this is the first move for a player(Mainly because the first move is a unique case that only happens once).
    def check_empty(self, grid, player):
        for i in range(len(grid)):
            for j in range(len(grid)):
                if(grid[i][j]==player):
                    return True
        return False

    # Check if the move creates at least a 3 
    # This function check for total of 8 directions
    def check_for_good_move(self, grid, player, r, c):
        value = 0
        if r-2 >= 0:
            if grid[r-2][c]==player and grid[r-1][c]==player:
                value += 1
            if(c+2 < 11):
                if grid[r-2][c+2]==player and grid[r-1][c+1]==player:
                    value += 1
                if grid[r][c+2]==player and grid[r][c+1]==player:
                    value += 1
            if(c-2>=0):
                if grid[r-2][c-2]==player and grid[r-1][c-1]==player:
                    value += 1
                if grid[r][c-2]==player and grid[r][c-1]==player:
                    value += 1
        if r+2 < 11:
            if grid[r+2][c]==player and grid[r+1][c]==player:
                value += 1
                if(c+2 < 11):
                    if grid[r+2][c+2] == player and grid[r+1][c+1]==player:
                        value += 1
                if(c-2>=0):
                    if grid[r+2][c-2] ==player and grid[r+1][c-1] == player:
                        value += 1
        return value


