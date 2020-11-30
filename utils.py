from mapa import Map
from consts import Tiles, TILES
import math

class Util:
    def __init__ (self, map_state=None, init_boxes=None):
        self.map_state = map_state
        self.curr_boxes = init_boxes
        self.move = None
        self.goals = self.filter_tiles([Tiles.BOX_ON_GOAL, Tiles.GOAL, Tiles.MAN_ON_GOAL]) if map_state is not None else None
        self.dark_list=self.init_darklist() if self.goals is not None else None #init

    def init_darklist(self):
        """
            Tracks WALLS and rows without goals
        """
        dk_list=[]
        block_positions=[]
        tile_goal=False
        for x in range(1, len(self.map_state[0])-1):
            for y in range(1,len(self.map_state)):
                block_positions.append((x,y))
                if (x,y) in self.goals or (self.get_tile((x+1,y))!=Tiles.WALL and self.get_tile((x-1,y))!=Tiles.WALL):
                    tile_goal= True
                if self.get_tile((x,y))== Tiles.WALL:
                    if not tile_goal:
                        dk_list.extend(block_positions)
                    block_positions=[]
                    tile_goal=False
            block_positions=[]
            tile_goal=False

        for y in range(1, len(self.map_state)-1):
            for x in range(1,len(self.map_state[0])):
                block_positions.append((x,y))
                if (x,y) in self.goals or (self.get_tile((x,y+1))!=Tiles.WALL and self.get_tile((x,y-1))!=Tiles.WALL):
                    tile_goal= True
                if self.get_tile((x,y))== Tiles.WALL:
                    if not tile_goal:
                        dk_list.extend(block_positions)
                    block_positions=[]
                    tile_goal=False
            block_positions=[]
            tile_goal=False
        return dk_list

    """ def init_darklist(self):
        dark_list = {}

        for x, y in self.goals:
            visited_nodes = [(x,y)]
            open_nodes = [(x,y)]
            while open_nodes != []:
                node = open_nodes.pop(0)
                print(node)
                x, y = node

                left = (x - 1, y)

                if left not in visited_nodes:
                    if self.get_tile(left) != Tiles.WALL:
                        if self.get_tile((x - 2, y)) == Tiles.WALL:
                            if left in dark_list:
                                dark_list[left] += 1
                            else:
                                dark_list[left] = 0

                right = (x + 1, y)
                if right not in visited_nodes:
                    if self.get_tile(right) != Tiles.WALL:
                        if self.get_tile((x + 2, y)) == Tiles.WALL:
                            if right in dark_list:
                                dark_list[right] += 1
                            else:
                                dark_list[right] = 0

                up = (x, y - 1)
                if up not in visited_nodes:
                    if self.get_tile(up) != Tiles.WALL:
                        if self.get_tile((x, y - 2)) == Tiles.WALL:
                            if up in dark_list:
                                dark_list[up] += 1
                            else:
                                dark_list[up] = 0

                down = (x, y + 1)
                if down not in visited_nodes:
                    if self.get_tile(down) != Tiles.WALL:
                        if self.get_tile((x, y + 2)) == Tiles.WALL:
                            if down in dark_list:
                                dark_list[down] += 1
                            else:
                                dark_list[down] = 0

        print(dark_list)

        return dark_list """


    def heuristic_boxes(self, box):
        calc_costs=sorted([(b, goal) for goal in self.goals  for b in box],key=lambda tpl : self.heuristic(tpl[0],tpl[1]))
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
                heur+= min([self.heuristic(goal,b) for goal in self.goals])
        return heur

    def heuristic(self, pos1, pos2):
        return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

    def completed(self, curr_boxes, goal_boxes):
        """
            Given the goal boxes and the current boxes, checks if they match
        """
        return all(box in goal_boxes for box in curr_boxes)

    def possible_keeper_actions(self, keeper_pos):
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

    def possible_actions(self, curr_boxes):
        """
            Possible actions vai ser a lista de ações possiveis de todas as caixas
            Devolve uma lista de ações possiveis
        """
        self.curr_boxes = curr_boxes
        possible_actions =[]
        i = 0
        for box in curr_boxes:
            possible_actions.append((i, self.possible_moves(box)))
            i += 1
        return possible_actions

    def possible_moves(self, box):

        possible_moves = []

        x, y = box
        left = (x - 1, y)
        right = (x + 1, y)
        up = (x, y - 1)
        down = (x, y + 1)
        # Left
        self.move = "left"
        if not self.is_blocked(right) and  left not in self.dark_list and  not self.is_dead_end(left):
            possible_moves.append(left)
    
        # Right
        self.move = "right"
        if not self.is_blocked(left) and right not in self.dark_list and not self.is_dead_end(right):
            possible_moves.append(right)
        # Up
        self.move = "up"
        if not self.is_blocked(down) and up not in self.dark_list and not self.is_dead_end(up):
            possible_moves.append(up)
        # Down
        self.move = "down"
        if not self.is_blocked(up) and down not in self.dark_list and not self.is_dead_end(down):
            possible_moves.append(down)
        
        return possible_moves

    def is_dead_end(self, pos):
        if self.is_blocked(pos) or self.is_trapped(pos):
            return True
        return False
        

    def is_blocked(self, pos):
        """
            Verifica se a pos não é uma parede, ou outra caixa
        """
        if self.get_tile(pos) == Tiles.WALL: 
            return True
        if pos in self.curr_boxes: 
            return True
        return False

    def is_trapped(self, pos, no_check=[]):
        """
            Verifica se a pos esta encurralada
        """
        #print(pos)
        no_check.append(pos)
        # Verificar se e um GOAL
        if self.get_tile(pos) == Tiles.GOAL:
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
        
        # Se existe uma caixa a esquerda ou direita, a pos esta blocked se a outra caixa estiver blocked
        if not horizontal_block and left in self.curr_boxes and left not in no_check:
            if self.is_trapped(left, no_check):
                #print("HORIZONTAL BLOCK NO-CHECK L")
                horizontal_block = True
        if not horizontal_block and right in self.curr_boxes and right not in no_check:
            if self.is_trapped(right, no_check):
                #print("HORIZONTAL BLOCK NO-CHECK R")
                horizontal_block = True
        # Se existe uma caixa acima ou embaixo, a pos esta blocked se a outra caixa estiver blocked
        if not vertical_block and up in self.curr_boxes and up not in no_check:
            if self.is_trapped(up, no_check):
                #print("VERTICAL BLOCK NO-CHECK U")
                vertical_block = True
        if not vertical_block and down in self.curr_boxes and down not in no_check:
            if self.is_trapped(down, no_check):
                #print("VERTICAL BLOCK NO-CHECK D")
                vertical_block = True
        
        if vertical_block and horizontal_block:
            print(pos)

        return vertical_block and horizontal_block


        """ cbx, cby, cwx, cwy = self.num_possibilities(pos)

        #print(cbx, cby, cwx, cwy)
        #print("POSITION: ", pos)

        # é canto nas paredes
        if cwx+cwy < 2 or (cwx <= 1 and cwy <= 1):
            #print("CANTO NAS PAREDES")
            return True
        if (cwx==0 and cby<=1) or (cwy==0 and cbx<=1):
            return True
            
        #if cbx == 1 and cby == 1:
            #print("CANTO NAS CAIXAS")
        #    return True

        return False """

        # # Verificar se 4 caixas estao juntas (aka canto)
        # diagonal_left_up = self.get_tile((pos[0]-1, pos[1]-1))
        # diagonal_left_down = self.get_tile((pos[0]-1, pos[1]+1))
        # left = self.get_tile((pos[0]-1, pos[1]))
        # diagonal_right_up = self.get_tile((pos[0]+1, pos[1]-1))
        # diagonal_right_down = self.get_tile((pos[0]+1, pos[1]+1))
        # right = self.get_tile((pos[0]+1, pos[1]))
        # up = self.get_tile((pos[0], pos[1]-1))
        # down = self.get_tile((pos[0], pos[1]+1))
        # if self.move == "left":
        #     if ((diagonal_left_up == Tiles.BOX or diagonal_left_up == Tiles.BOX_ON_GOAL or diagonal_left_up == Tiles.WALL) 
        #         and (left == Tiles.BOX or left == Tiles.BOX_ON_GOAL) 
        #         and (up == Tiles.BOX or up == Tiles.BOX_ON_GOAL)):
        #         print("DIAGONAL LEFT UP ", self.curr_boxes, pos)
        #         return True
        #     elif ((diagonal_left_down == Tiles.BOX or diagonal_left_down == Tiles.BOX_ON_GOAL or diagonal_left_down == Tiles.WALL) 
        #         and (left == Tiles.BOX or left == Tiles.BOX_ON_GOAL) 
        #         and (down == Tiles.BOX or down == Tiles.BOX_ON_GOAL)):
        #         print("DIAGONAL LEFT DOWN ", self.curr_boxes, pos)
        #         return True

        # if self.move == "right":
        #     if ((diagonal_right_up == Tiles.BOX or diagonal_right_up == Tiles.BOX_ON_GOAL or diagonal_right_up == Tiles.WALL) 
        #         and (right == Tiles.BOX or right == Tiles.BOX_ON_GOAL) 
        #         and (up == Tiles.BOX or up == Tiles.BOX_ON_GOAL)):
        #         print("DIAGONAL RIGHT UP", self.curr_boxes, pos)
        #         return True
        #     elif ((diagonal_right_down == Tiles.BOX or diagonal_right_down == Tiles.BOX_ON_GOAL or diagonal_right_down == Tiles.WALL) 
        #         and (right == Tiles.BOX or right == Tiles.BOX_ON_GOAL) 
        #         and (down == Tiles.BOX or down == Tiles.BOX_ON_GOAL)):
        #         print("DIAGONAL RIGHT DOWN", self.curr_boxes, pos)
        #         return True

        # if self.move == "down":
        #     if ((diagonal_left_down == Tiles.BOX or diagonal_left_down == Tiles.BOX_ON_GOAL or diagonal_left_down == Tiles.WALL) 
        #         and (left == Tiles.BOX or left == Tiles.BOX_ON_GOAL) 
        #         and (down == Tiles.BOX or down == Tiles.BOX_ON_GOAL)):
        #         print("DIAGONAL DOWN LEFT", self.curr_boxes, pos)
        #         return True
        #     elif ((diagonal_right_down == Tiles.BOX or diagonal_right_down == Tiles.BOX_ON_GOAL or diagonal_right_down == Tiles.WALL) 
        #         and (right == Tiles.BOX or right == Tiles.BOX_ON_GOAL) 
        #         and (down == Tiles.BOX or down == Tiles.BOX_ON_GOAL)):
        #         print("DIAGONAL DOWN RIGHT", self.curr_boxes, pos)
        #         return True

        # if self.move == "up":
        #     if ((diagonal_right_up == Tiles.BOX or diagonal_right_up == Tiles.BOX_ON_GOAL or diagonal_right_up == Tiles.WALL) 
        #         and (right == Tiles.BOX or right == Tiles.BOX_ON_GOAL) 
        #         and (up == Tiles.BOX or up == Tiles.BOX_ON_GOAL)):
        #         print("DIAGONAL UP RIGHT", self.curr_boxes, pos)
        #         return True
        #     elif ((diagonal_left_up == Tiles.BOX or diagonal_left_up == Tiles.BOX_ON_GOAL or diagonal_left_up == Tiles.WALL) 
        #         and (left == Tiles.BOX or left == Tiles.BOX_ON_GOAL ) 
        #         and (up == Tiles.BOX or up == Tiles.BOX_ON_GOAL )):
        #         print("DIAGONAL UP LEFT", self.curr_boxes, pos)
        #         return True
        
        

    def num_possibilities(self, pos):
        """
            Verifica quantas possibilidades uma caixa tem de se mover para todas as direções
        """
        cbx, cby, cwx, cwy = 0, 0, 0, 0

        if self.move == "left" or self.move == "right":
            cbx += 1
        else:
            cby += 1

        x, y = pos
        left = (x - 1, y)
        right = (x + 1, y)
        up = (x, y - 1)
        down = (x, y + 1)

        # check left
        if not self.get_tile(left) == Tiles.WALL:
            cwx +=1
        if left not in self.curr_boxes:
            cbx+=1
        # check right
        if not self.get_tile(right) == Tiles.WALL:
            cwx +=1
        if right not in self.curr_boxes:
            cbx+=1
        # check down
        if not self.get_tile(down) == Tiles.WALL:
            cwy+=1
        if down not in self.curr_boxes:
            cby+=1
        # check up
        if not self.get_tile(up) == Tiles.WALL:
            cwy+=1
        if up not in self.curr_boxes:
            cby+=1
        return cbx,cby,cwx,cwy

    
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
