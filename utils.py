from mapa import Map
from consts import Tiles, TILES
import math
import asyncio
import time
from queue import Queue

#https://www.youtube.com/watch?v=cQ5MsiGaDY8

class Util:
    def __init__ (self, map_state=None, init_boxes=None):
        dt = np.dtype(np.int16, np.int16)
        self.map_state = map_state
        self.curr_boxes = init_boxes
        self.deadends={}
        self.goals = set(self.filter_tiles([Tiles.BOX_ON_GOAL, Tiles.GOAL, Tiles.MAN_ON_GOAL])) if map_state is not None else None
        self.dark_list, self.distanceToGoal = self.init_darklist() if self.goals is not None else (None,None) #init
        #self.box_assignment= self.hungarian_heuristic()
        self.box = None

    # def hungarian_heuristic(self):
    #     gls=self.filter_tiles([Tiles.BOX_ON_GOAL, Tiles.GOAL, Tiles.MAN_ON_GOAL])
    #     matrix= [[self.distanceToGoal[g][b[0]][b[1]] for g in self.goals] for b in self.curr_boxes]
    #     print(matrix)

    #     #Step 1 Subtract row mins from each row.
    #     matrix=[[matrix[x][y] - min(matrix[x])for y in range(len(matrix)) ] for x in range(len(matrix)) ]
    #     print(matrix)

    #     #Step 2 Subtract column mins from each column
    #     matrix=[[matrix[x][y] - min([matrix[c][y] for c in range(len(matrix))]) for y in range(len(matrix))] for x in range(len(matrix)) ]
    #     return [gls[i] for i in range(len(gls)-1,-1,-1) ]


    def init_darklist(self):
        horz_tiles, vert_tiles = len(self.map_state[0]), len(self.map_state)

        visited = [[0] * vert_tiles for _ in range(horz_tiles)]
        distanceToGoal={goal:[[1000] * vert_tiles for _ in range(horz_tiles)] for goal in self.goals}

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

        def distanceG(goal):
            """
                Caixa mais distante -> heuristica maior
            """
            distanceToGoal[goal][goal[0]][goal[1]]=0
            open_goals = Queue()
            open_goals.put(goal)
            while not open_goals.empty():
                x,y= open_goals.get()

                if distanceToGoal[goal][x][y+1] == 1000 and not (self.get_tile((x, y +1)) == Tiles.WALL) and not (self.get_tile((x, y +2)) == Tiles.WALL):
                    distanceToGoal[goal][x][y+1]=distanceToGoal[goal][x][y]+1
                    open_goals.put((x,y+1))

                if distanceToGoal[goal][x][y-1] == 1000 and not (self.get_tile((x, y - 1)) == Tiles.WALL) and not (self.get_tile((x, y -2)) == Tiles.WALL):
                    distanceToGoal[goal][x][y-1]=distanceToGoal[goal][x][y]+1
                    open_goals.put((x,y-1))

                if distanceToGoal[goal][x+1][y] == 1000 and not (self.get_tile((x + 1, y )) == Tiles.WALL) and not (self.get_tile((x + 2, y)) == Tiles.WALL):
                    distanceToGoal[goal][x+1][y]=distanceToGoal[goal][x][y]+1
                    open_goals.put((x + 1,y))

                if distanceToGoal[goal][x-1][y] == 1000 and not (self.get_tile((x - 1, y )) == Tiles.WALL) and not (self.get_tile((x - 2, y)) == Tiles.WALL):
                    distanceToGoal[goal][x-1][y]=distanceToGoal[goal][x][y]+1
                    open_goals.put((x - 1,y))

        [check_not_blocked((x,y)) for x in range(horz_tiles) for y in range(vert_tiles) if (x,y) in self.goals]
        [distanceG((x,y)) for x in range(horz_tiles) for y in range(vert_tiles) if (x,y) in self.goals]

        return visited, distanceToGoal

    # def heuristic_boxes(self,box):
    #     #print(box)
    #     #print(self.box_assignment)
    #     #print(sum([self.distanceToGoal[self.box_assignment[x]][box[x][0]][box[x][1]] for x in range(len(self.box_assignment))] ))
    #     return sum([self.distanceToGoal[self.box_assignment[x]][box[x][0]][box[x][1]] for x in range(len(self.box_assignment))] )

    def heuristic_boxes(self, box):
        calc_costs = sorted([(b, goal) for goal in self.goals  for b in box],key=lambda tpl : self.distanceToGoal[tpl[1]][tpl[0][0]][tpl[0][1]], reverse=True)
        matchedBoxes=set()
        matchedGoals=set()
        heur=0
        while calc_costs !=[]:
            b,goal = calc_costs.pop()
            if not b  in matchedBoxes and not goal  in matchedGoals:
                h= self.distanceToGoal[goal][b[0]][b[1]]
                if h!=1000:
                    heur+=h
                    matchedBoxes.add(b)
                    matchedGoals.add(goal)
        for b in box:
            if not b in matchedBoxes:
                heur+=min([self.distanceToGoal[goal][b[0]][b[1]] for goal in self.goals])
                matchedBoxes.add(b)
        return heur

    # def heuristic_boxes(self, box):
    #     calc_costs = sorted([(b, goal) for goal in self.goals  for b in box],key=lambda tpl : self.heuristic(tpl[0],tpl[1]))
    #     matchedBoxes=set()
    #     matchedGoals=set()
    #     heur=0
    #     for b, goal in calc_costs:
    #         if not b in matchedBoxes and not goal in matchedGoals:
    #             heur+=self.heuristic(b,goal)
    #             matchedBoxes.add(b)
    #             matchedGoals.add(goal)
    #     return heur

    def heuristic(self, pos1, pos2):
        return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

    def completed(self, curr_boxes):
        """
            Given the goal boxes and the current boxes, checks if they match
        """
        return all(box in self.goals for box in curr_boxes)

    def possible_keeper_actions(self, keeper_pos):

        possible_moves = []

        x, y = keeper_pos
        left = (x - 1, y)
        right = (x + 1, y)
        up = (x, y - 1)
        down = (x, y + 1)

        # Left
        if not self.is_blocked(left):
            possible_moves.append((left, "a"))

        # Right
        if not self.is_blocked(right):
            possible_moves.append((right, "d"))

        # Up
        if not self.is_blocked(up):
            possible_moves.append((up, "w"))

        # Down
        if not self.is_blocked(down):
            possible_moves.append((down, "s"))

        return possible_moves

    def possible_actions(self, curr_boxes):
        """
            Possible actions vai ser a lista de ações possiveis de todas as caixas
            Devolve uma lista de ações possiveis
        """
        self.curr_boxes = curr_boxes
        possible_actions = []
        i=0
        for box in curr_boxes:
            a=self.possible_moves(box,i)
            if a:
                possible_actions.append((box,a))
            i+=1
        return possible_actions

    def possible_moves(self, box,i):
        self.box = box
        possible_moves = set()

        x, y = box
        left = (x - 1, y)
        right = (x + 1, y)
        up = (x, y - 1)
        down = (x, y + 1)

        # Left
        if self.dark_list[x-1][y] and not left in self.curr_boxes and not self.is_blocked(right):
            li= self.curr_boxes[:i] + (left,) + self.curr_boxes[i+1:]
            l=hash(li)
            if not l in self.deadends :
                if not self.freeze_deadlock(left,set()):
                    possible_moves.add((li,left))
                else:
                    self.deadends[l]=1

        # Right
        if self.dark_list[x+1][y] and not right in self.curr_boxes and not self.is_blocked(left):
            ri= self.curr_boxes[:i] + (right,) + self.curr_boxes[i+1:]
            r=hash(ri)
            if not r in self.deadends:
                if not self.freeze_deadlock(right,set()):
                    possible_moves.add((ri,right))
                else:
                    self.deadends[r]=1

        # Up
        if self.dark_list[x][y-1] and not up in self.curr_boxes and not self.is_blocked(down) :
            ui= self.curr_boxes[:i] + (up,) + self.curr_boxes[i+1:]
            u= hash(ui)
            if not u in self.deadends:
                if  not self.freeze_deadlock(up,set()):
                    possible_moves.add((ui,up))
                else:
                    self.deadends[u]=1

        # Down
        if self.dark_list[x][y+1] and not down in self.curr_boxes and not self.is_blocked(up):
            di=self.curr_boxes[:i] + (down,) + self.curr_boxes[i+1:]
            d= hash(di) 
            if not d in self.deadends :
                if not self.freeze_deadlock(down,set()):
                    possible_moves.add((di,down))
                else:
                    self.deadends[d]=1

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

            if not horizontal_block and not self.dark_list[pos[0]-1][pos[1]] and not self.dark_list[pos[0]+1][pos[1]]:
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
