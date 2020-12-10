from utils import *
from copy import deepcopy
import asyncio
import time
import heapq
from collections import deque
import time


class Node:
    __slots__ = ['boxes', 'parent', 'move', 'keeper', 'heuristic']
    def __init__(self,boxes,parent,move,keeper, heuristic):
        self.boxes = boxes # mapa actual state
        self.parent = parent
        self.move = move
        self.keeper = keeper
        self.heuristic = heuristic
    

class SokobanTree:
    def __init__ (self, map_state=None, init_boxes=None, goal_boxes=None):
        self.map_state = map_state
        self.init_boxes = init_boxes
        self.goal_boxes = goal_boxes # [(x,y), (z,w)...]
        self.Util = None
        self.root = None
        self.open_nodes = None
        self.path_solution= None
        self.used_states = None
        self.KeeperTree = None

    """ 
        Quando passa de nível atribui um novo estado à SokobanTree e reseta os nodes
    """
    def update_level (self, new_map_state, new_init_boxes, new_goal_boxes):
        start = time.time()
        self.map_state = new_map_state
        self.init_boxes = tuple(new_init_boxes)
        self.Util = Util(self.map_state, self.init_boxes)
        self.goal_boxes = new_goal_boxes
        self.root = Node(self.init_boxes, None, "", self.Util.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0], 0)
        self.open_nodes = []
        self.count=0
        heapq.heappush(self.open_nodes, (0, self.count, self.root))
        self.KeeperTree = KeeperTree(self.Util)
        self.used_states = {hash(self.init_boxes) : {self.root.keeper}}
        end = time.time()
        print(end - start)
        
    async def search(self):
        start = time.time()
        while self.open_nodes:

            node =  heapq.heappop(self.open_nodes)[2]

            if self.Util.completed(node.boxes):
                end = time.time()
                print(end - start)
                return node.move

            lnewnodes = []
    
            for cbox, box in self.Util.possible_actions(node.boxes):
                for nboxes, action in box:
                    x, y = cbox
                    left = (- 1, 0)
                    right = (1, 0)
                    up = (0, - 1)
                    down = (0, 1)   
                    
                    sub = (action[0] - cbox[0], action[1] - cbox[1])

                    if sub==left:
                        push = "a"
                    elif sub==right:
                        push = "d"
                    elif sub==up:
                        push = "w"
                    else:
                        push = "s"  
                    # 2*pos atual da caixa - posição para onde vai
                    keeper_target = (cbox[0]*2 - action[0], cbox[1]*2 - action[1])
                    keeper_moves =  self.KeeperTree.search_keeper(keeper_target, node.keeper)
                    await asyncio.sleep(0) 
                    if keeper_moves is not None:
                        
                        newnode = Node(nboxes, node, f"{node.move}{keeper_moves}{push}", cbox, self.Util.heuristic_boxes(nboxes))
                        h = hash(nboxes)

                        if not h in self.used_states:
                            self.used_states[h] = {newnode.keeper}
                            heapq.heappush(self.open_nodes, (newnode.heuristic, self.count,newnode))
                            self.count +=1
                        else:
                            x = False
                            for pos in self.used_states[h]:
                                if self.KeeperTree.search_keeper(newnode.keeper, pos, 0) is not None:
                                    x = True
                                    break
                            if not x:
                                heapq.heappush(self.open_nodes, (newnode.heuristic, self.count, newnode))
                                self.count +=1
                            self.used_states[h].add(newnode.keeper)

            #self.add_to_open(lnewnodes)
        return None

class KeeperNode:
    __slots__ = ['parent', 'keeper_pos', 'move', 'heuristic']
    def __init__(self, parent, keeper_pos, move, heuristic=None):
        self.parent = parent
        self.keeper_pos = keeper_pos
        self.move = move
        self.heuristic = heuristic

class KeeperTree:
    def __init__(self, Util):
        self.Util = Util
        self.keeper_nodes = None

    def get_path(self, node, pos):
        if node.parent == None:
            return node.keeper_pos == pos
        if node.keeper_pos == pos:
            return True
        return self.get_path(node.parent,pos)

    
    def search_keeper(self, target_pos, keeper_pos, strat=1):
        self.used_states_k=set()

        if strat:
            self.keeper_nodes= [KeeperNode(None, keeper_pos, "", self.Util.heuristic(keeper_pos, target_pos))]
        else:
            self.keeper_nodes = deque()
            self.keeper_nodes.append(KeeperNode(None, keeper_pos, "", 0))

        while self.keeper_nodes:

            node = self.keeper_nodes.pop()
            
            if node.keeper_pos == target_pos:
                return node.move

            if len(node.move)!=0:
                self.used_states_k.add((node.keeper_pos,node.move[-1]))
            
            lnewnodes = []
            
            for action, key in  self.Util.possible_keeper_actions(node.keeper_pos):
                if not (action,key) in self.used_states_k:
                    if strat:
                        newnode = KeeperNode(node, action, f"{node.move}{key}", len(node.move)+ self.Util.heuristic(action, target_pos))
                        lnewnodes.append(newnode)    
                    else:
                        newnode = KeeperNode(node, action, f"{node.move}{key}", 0)
                        self.keeper_nodes.append(newnode)
            if strat:
                self.add_to_open(lnewnodes)
        return None

    def add_to_open(self,lnewnodes):
        self.keeper_nodes.extend(lnewnodes)
        self.keeper_nodes.sort(key=lambda node : node.heuristic, reverse=True)
