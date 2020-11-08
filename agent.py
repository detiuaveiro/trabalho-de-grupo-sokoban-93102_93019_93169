from consts import Tiles, TILES
from mymap import *
from copy import deepcopy
class Node:
    def __init__(self,mapa,parent,move):
        self.mapa = mapa #mapa actual state
        self.parent = parent
        self.move=move

class SockobanTree:
    def __init__ (self, mapa):
        self.mapa = mapa # list with map elements
        root = Node(self.mapa, None, None)
        self.open_nodes = [root]
        self.path_solution= None
        
        self.used_nodes = []

        self.search()
    
    def update_level (self, mapa):
        self.mapa = mapa
        root = Node(self.mapa, None, None)
        self.open_nodes = [root]
        self.search()
        
    def get_move_path(self,node):
        if node.parent == None:
            return []
        path = self.get_move_path(node.parent)
        path += [node.move]
        return path

    def get_path(self,node):
        print("Get Path: ", node.mapa)
        if node.parent == None:
            return [node.mapa]
        path = self.get_path(node.parent)
        path += [node.mapa]
        return path

    def next_move(self):
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& SOLUTION: " + str(self.path_solution))
        if self.path_solution is not None:
            nxt=self.path_solution[0]
            self.path_solution=self.path_solution[1:]
            return nxt

    def search(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.used_nodes.append(node.mapa)

            if completed(node.mapa):
                print("!!!!!!!!!!!!!!!!")
                self.path_solution = self.get_move_path(node)
                print(self.path_solution)
                return
            lnewnodes = []
            # for each possible action in the set of actions for that state
            #print("[SEARCH] Possible Actions:", possible_actions(node.mapa))
    
            for m,key in possible_actions(node.mapa):
                keeper = filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL], node.mapa)[0]
                newnode = Node(move(keeper, key, deepcopy(node.mapa)), node, key)
                print(s(newnode.mapa))
                if newnode.mapa not in self.used_nodes:
                    print("Node appended")
                    lnewnodes.append(newnode) 
                
                """if newnode.mapa not in self.get_path(node):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& IF")
                    lnewnodes.append(newnode)""" 

            self.add_to_open(lnewnodes)
        return None
    
    def add_to_open(self,lnewnodes):
        self.open_nodes[:0]=lnewnodes
        
