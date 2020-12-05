from utils import *
from copy import deepcopy
import asyncio
import time
import heapq
from collections import deque

class Node:
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
    
        self.map_state = new_map_state
        self.init_boxes = set(new_init_boxes)
        self.Util = Util(self.map_state, self.init_boxes)
        self.goal_boxes = new_goal_boxes
        self.root = Node(self.init_boxes, None, "", self.Util.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0], 0)
        self.open_nodes = []
        self.count=0
        heapq.heappush(self.open_nodes, (0, self.count, self.root))
        self.KeeperTree = KeeperTree(self.Util)
        self.used_states = {hash(frozenset(self.init_boxes)) : [self.root.keeper]}
       
        
    async def search(self):
        while self.open_nodes:

            node =  heapq.heappop(self.open_nodes)[2]

            if self.Util.completed(node.boxes):
                return node.move

            lnewnodes = []
    
            for cbox, box in await self.Util.possible_actions(node.boxes):
                await asyncio.sleep(0)  # this should be 0 in your code and this is REQUIRED
                for action in box:
                    
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

                    keeper_moves = await self.KeeperTree.search_keeper(keeper_target, node.keeper)
                    #print(" ACTION: {} ; BOX POSITION: {}; Keeper_Moves {}".format(action, curr_box_pos,keeper_moves))
                    if keeper_moves is not None:
                        new_boxes = deepcopy(node.boxes)
                        new_boxes.remove(cbox) 
                        new_boxes.add(action)
                        newnode = Node(new_boxes, node, f"{node.move}{keeper_moves}{push}", cbox, self.Util.heuristic_boxes(new_boxes))
                        h = hash(frozenset(newnode.boxes))

                        if not h in self.used_states:
                            self.used_states[h] = [newnode.keeper]
                            heapq.heappush(self.open_nodes, (newnode.heuristic, self.count,newnode))
                            self.count +=1
                        else:

                            x = False
                            for pos in self.used_states[h]:
                                if await self.KeeperTree.search_keeper(newnode.keeper, pos, 0) is not None:
                                    x = True
                                    break
                            if not x:
                                self.used_states[h] += [newnode.keeper]
                                heapq.heappush(self.open_nodes, (newnode.heuristic, self.count, newnode))
                                self.count +=1

            #self.add_to_open(lnewnodes)
        return None

    # def add_to_open(self,lnewnodes):
    #     self.open_nodes[:0] = lnewnodes
    #     self.open_nodes.sort(key=lambda node : node.heuristic)

class KeeperNode:
    def __init__(self, parent, keeper_pos, move, heuristic=None):
        self.parent = parent
        self.keeper_pos = keeper_pos
        self.move = move
        self.heuristic = heuristic

class KeeperTree:
    def __init__(self, Util):
        self.Util = Util
        self.keeper_nodes = None

    def get_path(self, node):
        if node.parent == None:
            return set(node.keeper_pos)
        path = self.get_path(node.parent)
        path.add(node.keeper_pos)
        return set(path)
    
    async def search_keeper(self, target_pos, keeper_pos, strat=1):
        if strat:
            self.keeper_nodes= [KeeperNode(None, keeper_pos, "", self.Util.heuristic(keeper_pos, target_pos))]
        else:
            self.keeper_nodes = deque()
            self.keeper_nodes.append(KeeperNode(None, keeper_pos, "", self.Util.heuristic(keeper_pos, target_pos)))

        while self.keeper_nodes:
            await asyncio.sleep(0)  # this should be 0 in your code and this is REQUIRED

            node = self.keeper_nodes.pop()

            if node.keeper_pos == target_pos:
                return node.move

            lnewnodes = []

            for action, key in await self.Util.possible_keeper_actions(node.keeper_pos):
                newnode = KeeperNode(node, action, f"{node.move}{key}", node.heuristic + self.Util.heuristic(action, target_pos))
                if not newnode.keeper_pos in self.get_path(node):
                    if not strat:
                        self.keeper_nodes.append(newnode)
                    else:
                        lnewnodes.append(newnode)
            if strat:
                self.add_to_open(lnewnodes)

        return None

    def add_to_open(self,lnewnodes):
        self.keeper_nodes.extend(lnewnodes)
        self.keeper_nodes.sort(key=lambda node : node.heuristic, reverse=True)