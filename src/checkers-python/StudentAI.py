from random import randint, choice
import copy
from math import sqrt, log, e
from BoardClasses import Move
from BoardClasses import Board
import datetime
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():
    MAP_COLOR = {1 : "B", 2: "W"}
    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2

        self.c = 2
        self.game_tree = {}
        self.board_copy = Board(col,row,p) # <- used in simulation
        self.board_copy.initialize_game()
        self.max_move = 100

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        
        possible_moves = self.board.get_all_possible_moves(self.color)
        """
        Given Moves:  [[(1,1)-(2,0), (1,1)-(2,2)], 
                      [(1,3)-(2,2), (1,3)-(2,4)], 
                      [(1,5)-(2,4), (1,5)-(2,6)]] 
        """
        if(len(possible_moves) == 1):
            #print("Only one possible move: returning the only move")
            self.board.make_move(possible_moves[0][0],self.color)
            return possible_moves[0][0]
        
        move = self.MCTS()
        #print("MOVE:", move)
        self.board.make_move(move,self.color)
        return move


    def MCTS(self):
        """
        Runs the MCTSearch using 4 phases
        sudocode:
        def MCTS(state):
        tree = Node(state)
        while time_remains():
            leaf = Select(tree)
            child = Expand(leaf)
            result = Simulate(child)
            Back_Propagate(result, child)
        return the move in Actions(state) whose node has highest number of playouts 
        """
        self.board_copy = copy.deepcopy(self.board)

        # initialize tree with root node 
        if self.board_copy in self.game_tree:
            root = self.game_tree[board_copy]
        else:
            root = Node(self.board_copy, None, self.opponent[self.color])
        root.parent = None

        endTime = datetime.datetime.now() + datetime.timedelta(seconds = 10) # <- determine how long it'll run
        sim_count = 0
        while datetime.datetime.now() <= endTime:
            node, color = self.select_node(root) # either best_child or newly expanded child
            simulation_result = self.run_simulation(node, color) # winner: 2 or 1 or 0.5 or 0
            self.backprop(node, simulation_result, color)
            sim_count += 1
            #self.print_children(root)
            #print("MCTS::-----------simcount:", sim_count,"-------------")
            if sim_count == 1000:
                break
        return self.best_move(root)
    
    def backprop(self, node, winner, color):
        if winner != 0.5 and winner != 0:
            inc_color = winner
            while node.parent is not None:
                if node.color == inc_color:
                    node.plays += 1
                    node.wins  += 1
                else:
                    node.plays += 1
                node = node.parent
            node.plays += 1
        else:
            while node.parent is not None:
                node.plays += 1
                node.wins += winner # either 0.5 or 0
                node = node.parent
            node.plays += 1

        
    def print_children(self, node):
        for child in node.children:
            print("PRINT_CHILD:: Child move", child.move, "with wins,plays:", child.wins, ",", child.plays)
    
    def select_node(self, root):
        cur_node = root 
        
        legal_moves = self.make_list(cur_node.state.get_all_possible_moves(self.color))
        i = -1
        while True:
            i += 1
            #print("select_node-1:: cur_node's move:", cur_node.move)
            #print("cur_node's state: ")
            #cur_node.state.show_board()
            #print("winrate :", cur_node.wins, cur_node.plays)
            # case 1: children are not fully expanded
            if (i % 2) == 0: #i is even => AI's turn
                termination_check = cur_node.state.is_win(self.MAP_COLOR[self.opponent[self.color]])
                if termination_check != 0:
                    return cur_node, self.opponent[self.color]
                elif len(cur_node.children) == 0 or len(cur_node.children) < len(legal_moves):
                    
                    #print("select_node-4:: cur_node's poss_move:", legal_moves)
                    #print("select_node-5:: cur_node's expanded move (before expansion):", cur_node.moves_expanded)

                    unexpanded = [ move for move in legal_moves if tuple(move) not in cur_node.moves_expanded]
                    assert len(unexpanded) > 0

                    move = choice(unexpanded) # randomly choose unexpanded move 
                    next_state = copy.deepcopy(cur_node.state)
                    next_state.make_move(move,self.color) # create a next_state with a chosen move
                    #print("select_node-8:: after next_state makes move, root's board: ")
                    #print(cur_node.state.show_board())
                    child = Node(next_state, move, self.color) # create a new child (leaf)
                    #print("select_node-6:: expanded child", child.move)
                    child.deepcopy_state()
                    cur_node.add_child(child)
                    #cur_node.state.show_board()

                    #print("select_node-7:: cur_node's expanded move (after expansion):", cur_node.moves_expanded)
                    self.game_tree[next_state] = child # udpate game_tree
                    next_state.undo()
                    return child, self.color
                # case 2: Every possible next state has been expanded, pick one
                else:              
                    cur_node = self.best_child(cur_node)
                    #print("select_node-2:: best_child's move:", cur_node.move)
                    #print("select_node-3:: best_child's parent:", cur_node.parent.move)
                    legal_moves = self.make_list(cur_node.state.get_all_possible_moves(self.opponent[self.color]))
                    #cur_node.state.show_board()       

            else: # i % 2 != 0
                termination_check = cur_node.state.is_win(self.MAP_COLOR[self.color])
                if termination_check != 0:
                    return cur_node, self.color

                elif len(cur_node.children) == 0 or len(cur_node.children) < len(legal_moves):
                    
                    #print("select_node-4:: cur_node's poss_move:", legal_moves)
                    #print("select_node-5:: cur_node's expanded move (before expansion):", cur_node.moves_expanded)

                    unexpanded = [ move for move in legal_moves if tuple(move) not in cur_node.moves_expanded]
                    assert len(unexpanded) > 0

                    move = choice(unexpanded) # randomly choose unexpanded move 
                    next_state = copy.deepcopy(cur_node.state)
                    next_state.make_move(move, self.opponent[self.color]) # create a next_state with a chosen move
                    #print("select_node-8:: after next_state makes move, root's board: ")
                    #print(cur_node.state.show_board())
                    child = Node(next_state, move, self.opponent[self.color]) # create a new child (leaf)
                    #print("select_node-6:: expanded child", child.move)
                    child.deepcopy_state()
                    cur_node.add_child(child)
                    #cur_node.state.show_board()

                    #print("select_node-7:: cur_node's expanded move (after expansion):", cur_node.moves_expanded)
                    self.game_tree[next_state] = child # udpate game_tree
                    next_state.undo()
                    return child, self.opponent[self.color] # enemy child 
                # case 2: Every possible next state has been expanded, pick one
                else:           
                    cur_node = self.best_child(cur_node)
                    #print("select_node-2:: best_child's move:", cur_node.move)
                    #print("select_node-3:: best_child's parent:", cur_node.parent.move)
                    legal_moves = self.make_list(cur_node.state.get_all_possible_moves(self.color))
                    #cur_node.state.show_board()    
            

    def best_child(self, node):
        values = {}
        for child in node.children:
                values[child] = (child.wins/child.plays) + (1.5 * sqrt(log(node.plays, e) / child.plays))
    
        best_child = max(values, key=values.get)
        return best_child
        
    def best_move(self, root):
        most_plays = float('-inf')
        most_wins  = float('-inf')
        most_percentage  = float('-inf')
        move = None
        for child in sorted(root.children, key = lambda child : child.plays):
            wins, plays = child.get_wins_plays()
            percentage = wins/plays
            if plays > most_plays:
                most_plays = plays
            if (plays/most_plays) >= 0.8:
                if percentage > most_percentage:
                    most_percentage = percentage 
                    move = child.move    
        return move                 

    def run_simulation(self, node, color):
        """
        Start random game simulation from the given node 
        is_win returns 2 if W won, 1 if B won, 0 if no one won, , -1 if tie
        """
        cur_state = copy.deepcopy(node.state) # board state of the given node
        if color == self.color:
            while True:
                # repeatedly do : check termination, play opponent -> check termination, play AI 
                termination_check = cur_state.is_win(self.MAP_COLOR[self.color])
                if   termination_check ==                self.color: return self.color  # if AI is a winner, return 1
                elif termination_check == self.opponent[self.color]: return self.opponent[self.color]
                elif termination_check ==                        -1: return 0.5
                elif termination_check ==                         0:
                    opp_moves = cur_state.get_all_possible_moves(self.opponent[self.color])
                    if(len(opp_moves) == 0): return 0 # opponent ran out of moves
                    #opp_move  = self.sim_behavior(self.make_list(opp_moves), cur_state, self.opponent[self.color])
                    opp_move  = choice(self.make_list(opp_moves))
                    cur_state.make_move(opp_move, self.opponent[self.color])
                    #cur_state.show_board()
                
                termination_check = cur_state.is_win(self.MAP_COLOR[self.opponent[self.color]])
                if   termination_check ==                self.color: return self.color
                elif termination_check == self.opponent[self.color]: return self.opponent[self.color]
                elif termination_check ==                        -1: return 0.5
                elif termination_check ==                         0:
                    my_moves = cur_state.get_all_possible_moves(self.color)
                    if(len(my_moves) == 0): return 0 # Betago ran out of moves
                    #my_move  = self.sim_behavior(self.make_list(my_moves), cur_state, self.color)
                    my_move  = choice(self.make_list(my_moves))
                    cur_state.make_move(my_move, self.color)
                    #cur_state.show_board() 
        else:
            while True:
                termination_check = cur_state.is_win(self.MAP_COLOR[self.opponent[self.color]])
                if   termination_check ==                self.color: return self.color
                elif termination_check == self.opponent[self.color]: return self.opponent[self.color]
                elif termination_check ==                        -1: return 0.5
                elif termination_check ==                         0:
                    my_moves = cur_state.get_all_possible_moves(self.color)
                    if(len(my_moves) == 0): return 0 # Betago ran out of moves
                    #my_move  = self.sim_behavior(self.make_list(my_moves), cur_state, self.color)
                    my_move  = choice(self.make_list(my_moves))
                    cur_state.make_move(my_move, self.color)
                    #cur_state.show_board()
                    # repeatedly do : check termination, play opponent -> check termination, play AI 
                termination_check = cur_state.is_win(self.MAP_COLOR[self.color])
                if   termination_check ==                self.color: return self.color  # if AI is a winner, return 1
                elif termination_check == self.opponent[self.color]: return self.opponent[self.color]
                elif termination_check ==                        -1: return 0.5
                elif termination_check ==                         0:
                    opp_moves = cur_state.get_all_possible_moves(self.opponent[self.color])
                    if(len(opp_moves) == 0): return 0 # opponent ran out of moves
                    #opp_move  = self.sim_behavior(self.make_list(opp_moves), cur_state, self.opponent[self.color])
                    opp_move  = choice(self.make_list(opp_moves))
                    cur_state.make_move(opp_move, self.opponent[self.color])
                    #cur_state.show_board()

    def make_list(self, possible_moves):
        """
        Helper Method: Change a nested-list into a list
        """
        to_explore = [ ]
        for checker in possible_moves:
            for move in checker:
                to_explore.append(move)
        return to_explore

class Node:
    
    def __init__(self, state_to_copy, move, color):
        self.state_to_copy = state_to_copy
        self.state = state_to_copy # self.board
        self.color = color
        self.plays = 0 
        self.wins = 0
        self.parent = None
        self.children = []
        self.moves_expanded = set()
        self.move = move

    def deepcopy_state(self):
        self.state = copy.deepcopy(self.state_to_copy)

    def add_child(self,node):
        self.children.append(node)
        self.moves_expanded.add(tuple(node.move))
        node.parent = self
    
    def get_wins_plays(self):
        return self.wins, self.plays
    
    def __str__(self):
        return "Win: " + self.wins + " Plays: " + self.plays + " # children: " + self.num_children
    
    def __len__(self):
        return str(self)