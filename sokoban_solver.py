from utils import *
from copy import deepcopy

class Node:
    def __init__(self,boxes,parent,move,keeper):
        self.boxes = boxes # mapa actual state
        self.parent = parent
        self.move = move
        self.keeper = keeper

class SokobanTree:
    def __init__ (self, map_state, init_boxes, goal_boxes):

        self.map_state = map_state
        self.init_boxes = init_boxes
        self.goal_boxes = goal_boxes # [(x,y), (z,w)...]
        self.Util = Util(self.map_state, self.init_boxes)
        self.root = Node(self.init_boxes, None, None, self.Util.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL]) )
        self.open_nodes = [self.root]
        self.path_solution= None
        
        self.used_nodes = []

        self.search()
    
    """ 
        Quando passa de nível atribui um novo estado à SokobanTree e reseta os nodes
    """
    def update_level (self, new_map_state, new_init_boxes, new_goal_boxes):
        self.map_state = new_map_state
        self.init_boxes = new_init_boxes
        self.Util = Util(self.map_state, self.init_boxes)
        self.goal_boxes = new_goal_boxes
        self.root = Node(self.init_boxes, None, None)
        self.open_nodes = [self.root]
        self.search()
        
    def get_move_path(self,node):
        if node.parent == None:
            return []
        path = self.get_move_path(node.parent)
        path += [node.move]
        return path

    def get_path(self,node):
        if node.parent == None:
            return [node.boxes]
        path = self.get_path(node.parent)
        path += [node.boxes]
        return path

    def next_move(self):
        if self.path_solution is not None:
            nxt=self.path_solution[0]
            self.path_solution = self.path_solution[1:]
            return nxt

    def search(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.used_nodes.append(node.boxes)

            if Util.completed(node.boxes, self.goal_boxes):
                self.path_solution = self.get_move_path(node)
                return

            lnewnodes = []
    
    
            for box_actions in self.Util.possible_actions(node.boxes):
                for action in box_actions:
                    
                    newnode = Node(node.boxes, node, action,)


                keeper = filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL], node.boxes)[0]
                newnode = Node(move(keeper, key, deepcopy(node.boxes)), node, key)

                if newnode.boxes not in self.used_nodes:
                    lnewnodes.append(newnode) 

            self.add_to_open(lnewnodes)
        return None

    def search_keeper_path(self, node):
         while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.used_nodes.append(node.boxes)

            if Util.completed(node.boxes, self.goal_boxes):
                self.path_solution = self.get_move_path(node)
                return

            lnewnodes = []
    
    
            for box_actions in self.Util.possible_actions(node.boxes):


                if newnode.boxes not in self.used_nodes:
                    lnewnodes.append(newnode) 

            self.add_to_open(lnewnodes)
        return None
