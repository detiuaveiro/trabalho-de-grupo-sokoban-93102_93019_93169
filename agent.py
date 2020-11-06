from consts import Tiles, TILES
from mymap import Mymap
class Node:
    def __init__(self,mapa,parent,move):
        self.mapa = mapa #mapa actual state
        self.parent = parent
        self.move=move

class SockobanTree:
    def __init__ (self, mapa):
        self.mapa= mapa
        root = Node(self.mapa,None,None)
        self.open_nodes = [root]
        self.path_solution= None
        self.search()
    
    def update_level (self,mapa):
        self.mapa=mapa
        self.search()
        
    def get_move_path(self,node):
        if node.parent == None:
            return []
        path = self.get_move_path(node.parent)
        path += [node.move]
        return path

    def get_path(self,node):
        if node.parent == None:
            return [node.mapa.__getstate__()]
        path = self.get_path(node.parent)
        path += [node.mapa.__getstate__()]
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
            if node.mapa.completed:
                print("!!!!!!!!!!!!!!!!")
                self.path_solution = self.get_move_path(node)
                return
            lnewnodes = []
            # for each possible action in the set of actions for that state
            print(node.mapa.possible_actions())

            for move,key in node.mapa.possible_actions():

                newnode = Node(Mymap(node.mapa.__getlevel__()),node,key)
                newnode.mapa.move(node.mapa.keeper, key)

                

                print(newnode.mapa)
                print("\n")
                if newnode.mapa.__getstate__() not in self.get_path(node):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& IF")
                    lnewnodes.append(newnode) 

            self.add_to_open(lnewnodes)
        return None
    
    def add_to_open(self,lnewnodes):
        self.open_nodes.extend(lnewnodes)
        