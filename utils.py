from mapa import Map
from consts import Tiles, TILES
import math
import asyncio
import time

class Util:
    def __init__ (self, map_state=None, init_boxes=None):
        self.map_state = map_state
        self.curr_boxes = init_boxes
        self.move = None
        self.goals = set(self.filter_tiles([Tiles.BOX_ON_GOAL, Tiles.GOAL, Tiles.MAN_ON_GOAL])) if map_state is not None else None
        self.dark_list = self.init_darklist() if self.goals is not None else None #init
        self.box = None

    def init_darklist(self):
        horz_tiles, vert_tiles = len(self.map_state[0]), len(self.map_state)

        visited = [[0] * vert_tiles for _ in range(horz_tiles)]
        

        def check_not_blocked(pos):
            x, y = pos

            if visited[x][y] or self.get_tile(pos) == Tiles.WALL:
                return

            visited[x][y] = 1
            if x > -1 and x < horz_tiles and y + 2 > -1 and y + 2 < vert_tiles and not (self.get_tile((x, y + 2)) == Tiles.WALL):
                check_not_blocked((x, y + 1))
            if x + 2 > -1 and x + 2 < horz_tiles and y > -1 and y < vert_tiles and not (self.get_tile((x + 2, y)) == Tiles.WALL):
                check_not_blocked((x + 1, y))
            if x > -1 and x < horz_tiles and y - 2 > -1 and y - 2< vert_tiles and not (self.get_tile((x, y - 2)) == Tiles.WALL):
                check_not_blocked((x, y - 1))
            if x - 2 > -1 and x - 2< horz_tiles and y > -1 and y < vert_tiles and not (self.get_tile((x - 2, y)) == Tiles.WALL):
                check_not_blocked((x - 1, y))
            return

        [check_not_blocked((x,y)) for x in range(horz_tiles) for y in range(vert_tiles) if (x,y) in self.goals]

        return visited


    def heuristic_boxes(self, box):
        calc_costs = sorted([(b, goal) for goal in self.goals  for b in box],key=lambda tpl : self.heuristic(tpl[0],tpl[1]))
        matchedBoxes=[]
        matchedGoals=[]
        heur=0
        while calc_costs != []:
            (b,goal)=calc_costs.pop(0)
            if b not in matchedBoxes and goal not in matchedGoals:
                heur+=self.heuristic(b,goal)
                matchedBoxes.append(b)
                matchedGoals.append(goal)
        for b in box:
            if b not in matchedBoxes:
                heur += min([self.heuristic(goal,b) for goal in self.goals])
        return heur

    def heuristic(self, pos1, pos2):
        return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

    def completed(self, curr_boxes, goal_boxes):
        """
            Given the goal boxes and the current boxes, checks if they match
        """
        return all(box in goal_boxes for box in curr_boxes)

    async def possible_keeper_actions(self, keeper_pos):
        await asyncio.sleep(0)  # this should be 0 in your code and this is REQUIRED
        possible_moves = []

        x, y = keeper_pos
        left = (x - 1, y)
        right = (x + 1, y)
        up = (x, y - 1)
        down = (x, y + 1)

        # Left
        self.move = "left"
        if not self.is_blocked(left):
            possible_moves.append((left, "a"))
        # Right
        self.move = "right"
        if not self.is_blocked(right):
            possible_moves.append((right, "d"))
        # Up
        self.move = "up"
        if not self.is_blocked(up):
            possible_moves.append((up, "w"))
        # Down
        self.move = "down"
        if not self.is_blocked(down):
            possible_moves.append((down, "s"))

        return possible_moves

    async def possible_actions(self, curr_boxes):
        """
            Possible actions vai ser a lista de ações possiveis de todas as caixas
            Devolve uma lista de ações possiveis
        """
        await asyncio.sleep(0)  # this should be 0 in your code and this is REQUIRED
        self.curr_boxes = curr_boxes
        possible_actions =[]
        i = 0
        for box in curr_boxes:
            possible_actions.append((i, self.possible_moves(box)))
            i += 1

        return possible_actions

    def possible_moves(self, box):
        self.box = box
        possible_moves = []

        x, y = box
        left = (x - 1, y)
        right = (x + 1, y)
        up = (x, y - 1)
        down = (x, y + 1)
        # Left
        self.move = "left"
        if self.dark_list[x-1][y] and left not in self.curr_boxes and not self.is_blocked(right) and not self.freeze_deadlock(left,set()):
            possible_moves.append(left)
        # Right
        self.move = "right"
        if self.dark_list[x+1][y] and right not in self.curr_boxes and not self.is_blocked(left) and not self.freeze_deadlock(right,set()):
            possible_moves.append(right)
        # Up
        self.move = "up"
        if self.dark_list[x][y-1] and up not in self.curr_boxes and not self.is_blocked(down) and not self.freeze_deadlock(up,set()):
            possible_moves.append(up)
        # Down
        self.move = "down"
        if self.dark_list[x][y+1] and down not in self.curr_boxes and not self.is_blocked(up) and not self.freeze_deadlock(down,set()):
            possible_moves.append(down)
        return possible_moves

    # def is_dead_end(self, pos):
    #     if self.is_blocked(pos) or self.is_trapped(pos):
    #         return True
    #     return False
        
    def is_blocked(self, pos):
        """
            Verifica se a pos não é uma parede, ou outra caixa
        """
        if self.get_tile(pos) == Tiles.WALL: 
            return True
        if pos in self.curr_boxes: 
            return True
        return False

    def freeze_deadlock(self, pos,  boxes_checked,tipo=None):

        boxes_checked.add(pos)

        horizontal_block = True
        # Verificar se existe uma WALL a esqueda ou direita da caixa - bloqueio horizontal
        if tipo == "horizontal" or tipo is None:
            left = (pos[0]-1, pos[1])
            right = (pos[0]+1, pos[1])
            horizontal_block = False
            if self.get_tile(left) == Tiles.WALL or self.get_tile(right) == Tiles.WALL:
                horizontal_block = True

            if not horizontal_block and not self.dark_list[pos[0]-1][pos[1]] and  not self.dark_list[pos[0]+1][pos[1]]:
                horizontal_block = True

            # verificar se uma das caixas ao lado está blocked
            if not horizontal_block and left in self.curr_boxes and left != self.box and self.freeze_deadlock(left,  boxes_checked, "vertical"):
                horizontal_block = True
            if not horizontal_block and right in self.curr_boxes and right != self.box and self.freeze_deadlock(right, boxes_checked, "vertical"):
                horizontal_block = True

        vertical_block = True
        # Verificar se existe uma WALL acima ou embaixo da caixa - bloqueio vertical
        if tipo == "vertical" or tipo is None:
            up = (pos[0], pos[1]-1)
            down = (pos[0], pos[1]+1)
            vertical_block = False
            if self.get_tile(up) == Tiles.WALL or self.get_tile(down) == Tiles.WALL:
                vertical_block = True
            
            # Verificar se esta na darklist
            if not vertical_block and not self.dark_list[pos[0]][pos[1]-1] and not self.dark_list[pos[0]][pos[1]+1]:
                vertical_block = True

            # verificar se uma das caixas ao lado está blocked
            if not vertical_block and up in self.curr_boxes and up != self.box and self.freeze_deadlock(up, boxes_checked, "horizontal"):
                vertical_block = True
            if not vertical_block and down in self.curr_boxes and down != self.box and self.freeze_deadlock(down, boxes_checked, "horizontal"):
                vertical_block = True

        if all(box in self.goals for box in boxes_checked):
            return False
        return vertical_block and horizontal_block

        
    def is_trapped(self, pos, no_check=[]):
        """
            Verifica se a pos esta encurralada
        """
        #print(pos)
        no_check.append(pos)
        # Verificar se e um GOAL
        if pos in self.goals:
            return False
        
        # Verificar se existe uma WALL a esqueda ou direita da caixa - bloqueio horizontal
        left = (pos[0]-1, pos[1])
        right = (pos[0]+1, pos[1])
        horizontal_block = False
        if self.get_tile(left) == Tiles.WALL or self.get_tile(right) == Tiles.WALL:
            #print("HORIZONTAL BLOCK")
            horizontal_block = True

        # Verificar se existe uma WALL acima ou embaixo da caixa - bloqueio vertical
        up = (pos[0], pos[1]-1)
        down = (pos[0], pos[1]+1)
        vertical_block = False
        if self.get_tile(up) == Tiles.WALL or self.get_tile(down) == Tiles.WALL:
            #print("VERTICAL BLOCK")
            vertical_block = True

        # Verificar se esta na darklist
        if not horizontal_block and left in self.dark_list and right in self.dark_list:
            #print("HORIZONTAL BLOCK DARKLIST")
            horizontal_block = True
        if not vertical_block and up in self.dark_list and down in self.dark_list:
            #print("VERTICAL BLOCK DARKLIST")
            vertical_block = True

        # # Se existe uma caixa a esquerda ou direita, a pos esta blocked se a outra caixa estiver blocked
        # if not horizontal_block and left in self.curr_boxes and left not in no_check:
        #     if self.is_trapped(left, no_check):
        #         #print("HORIZONTAL BLOCK NO-CHECK L")
        #         horizontal_block = True
        # if not horizontal_block and right in self.curr_boxes and right not in no_check:
        #     if self.is_trapped(right, no_check):
        #         #print("HORIZONTAL BLOCK NO-CHECK R")
        #         horizontal_block = True
        # # Se existe uma caixa acima ou embaixo, a pos esta blocked se a outra caixa estiver blocked
        # if not vertical_block and up in self.curr_boxes and up not in no_check:
        #     if self.is_trapped(up, no_check):
        #         #print("VERTICAL BLOCK NO-CHECK U")
        #         vertical_block = True
        # if not vertical_block and down in self.curr_boxes and down not in no_check:
        #     if self.is_trapped(down, no_check):
        #         #print("VERTICAL BLOCK NO-CHECK D")
        #         vertical_block = True
        
        if vertical_block and horizontal_block:
            print(pos)

        return vertical_block and horizontal_block

    
    def get_tile(self, pos):      
        """Retrieve tile at position pos."""
        x, y = pos
        return self.map_state[y][x]
    

    def filter_tiles (self, list_to_filter):
        """Util to retrieve list of coordinates of given tiles."""
        return [
            (x, y)
            for y, l in enumerate(self.map_state)
            for x, tile in enumerate(l)
            if tile in list_to_filter
        ]
