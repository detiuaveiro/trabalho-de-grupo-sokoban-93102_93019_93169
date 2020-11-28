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

    # def no_goals_on_wall(self, pos):
    #     x, y = pos

    #     if self.move == "up":
    #         return any(p == Tiles.GOAL or Tiles.MAN_ON_GOAL for p in self.map_state[x]) and self.get_tile((x,y-1)) == Tiles.WALL

    #     if self.move == "down":
    #         return any(p == Tiles.GOAL or Tiles.MAN_ON_GOAL for p in self.map_state[x]) and self.get_tile((x,y+1)) == Tiles.WALL

    #     if self.move == "left":
    #         return any(self.map_state[x][y] == Tiles.GOAL or Tiles.MAN_ON_GOAL for i in range(len(self.map_state[y]))) and self.get_tile((x-1,y)) == Tiles.WALL

    #     if self.move == "right":
    #         return any(self.map_state[x][y] == Tiles.GOAL or Tiles.MAN_ON_GOAL for i in range(len(self.map_state[y]))) and self.get_tile((x+1,y)) == Tiles.WALL

    def is_dead_end(self, pos):
        if self.is_blocked(pos) or self.is_trapped(pos):
            #print("Dark List: ", self.dark_list)
            #self.dark_list.add(pos)
            return True
        # if self.no_goals_on_wall(pos):
        #     return True
        return False
        

    def is_blocked(self, pos):
        """
            Verifica se a pos não é uma parede, ou outra caixa
        """
        if self.get_tile(pos) == Tiles.WALL: 
            #self.dark_list.add(pos)
            return True
        if pos in self.curr_boxes: 
            return True
        return False

    def is_trapped(self, pos):
        """
            Verifica se a pos é um canto
            Mais para a frente -> + Adicionar lateral sem goals
        """
        #print(pos)

        if self.get_tile(pos) == Tiles.GOAL:
            return False

        cbx, cby, cwx, cwy = self.num_possibilities(pos)

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

        # Verificar se 3 caixas estao juntas (aka canto)
        # verificar caixas na diagonal 



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



        
        # # é "canto" nas caixas
        # if cbx < 2 and cby < 2:
        #     return True
        # # é "canto" com caixas e paredes
        # if (cbx < 2 and cwy < 2) or (cby < 2 and cwx < 2):
        #     print("c3")
        #     return True
        
        return False
        

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

    # Non possible actions
    """
    keeper goes to wall
    delaying moving of ongoal boxes
    keeper pushes box to corner (dead end)
    keeper pushes box to side when there is no goal
    """
     
    # def possible_actions(state_list):
    #     possible_actions = []
    #     keeper = filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL], state_list)[0]

    #     # move to left
    #     new_keeper = (keeper[0]-1, keeper[1])
    #     if not is_blocked(new_keeper, state_list,"left") and not is_dead_end(new_keeper,"left", state_list):
    #         possible_actions.append((new_keeper,"a"))

    #     # move to right
    #     new_keeper = (keeper[0]+1, keeper[1])
    #     if not is_blocked(new_keeper, state_list,"right") and not is_dead_end(new_keeper,"right", state_list):
    #         possible_actions.append((new_keeper,"d"))

    #     # move down
    #     new_keeper = (keeper[0], keeper[1]+1)
    #     if not is_blocked(new_keeper, state_list,"down") and not is_dead_end(new_keeper,"down", state_list):
    #         possible_actions.append((new_keeper,"s"))

    #     # move up
    #     new_keeper = (keeper[0], keeper[1]-1)
    #     if not is_blocked(new_keeper, state_list,"up") and not is_dead_end(new_keeper,"up", state_list):
    #         possible_actions.append((new_keeper,"w"))
    #     return possible_actions

        
    # def is_dead_end(new_keeper, move, state_list):
    #     """
    #         Checks if it's a dead end
    #         dead end: the box ends up on a corner
    #     """
    #     if get_tile(new_keeper, state_list) == Tiles.BOX or get_tile(new_keeper, state_list)== Tiles.BOX_ON_GOAL:
    #         if move == "left":
    #             new_box = (new_keeper[0]-1, new_keeper[1])
    #         elif move == "right":
    #             new_box = (new_keeper[0]+1, new_keeper[1])
    #         elif move == "down":
    #             new_box = (new_keeper[0], new_keeper[1]+1)
    #         else:
    #             new_box = (new_keeper[0], new_keeper[1]-1)
    #         if not get_tile(new_box, state_list) == Tiles.GOAL:
    #             cbx, cby, cwx, cwy = number_possibilities(new_box, state_list,move)
    #             print("NP:"+ str(cbx)+str(cby)+str(cwx)+str(cwy))
    #             # é canto nas paredes
    #             if cwx+cwy <= 2:
    #                 return True
    #             # é "canto" nas caixas
    #             if cbx < 2 and cby < 2:
    #                 return True
    #             # é "canto" com caixas e paredes
    #             if (cbx < 2 and cwy < 2) or (cby < 2 and cwx < 2):
    #                 return True
    #     return False


    # def number_possibilities(new_box, state_list,move):
    #     if is_blocked(new_box, state_list):
    #         return 0,0,0,0
    #     cwx = 0
    #     cbx = 0
    #     cwy = 0
    #     cby = 0
    #     if move=="left" or move=="right":
    #         cbx+=1
    #     else:
    #         cby+=1
    #     # check left
    #     if not is_blocked((new_box[0]-1, new_box[1]), state_list):
    #         cwx +=1
    #     if not (get_tile((new_box[0]-1, new_box[1]), state_list) == Tiles.BOX or get_tile((new_box[0]-1, new_box[1]), state_list)== Tiles.BOX_ON_GOAL):
    #         cbx+=1
    #     # check right
    #     if not is_blocked((new_box[0]+1, new_box[1]), state_list):
    #         cwx +=1
    #     if not (get_tile((new_box[0]+1, new_box[1]), state_list)== Tiles.BOX or get_tile((new_box[0]+1, new_box[1]), state_list) == Tiles.BOX_ON_GOAL):
    #         cbx+=1
    #     # check down
    #     if not is_blocked((new_box[0], new_box[1]+1), state_list):
    #         cwy+=1
    #     if not (get_tile((new_box[0], new_box[1]+1), state_list) == Tiles.BOX or get_tile((new_box[0], new_box[1]+1), state_list) == Tiles.BOX_ON_GOAL):
    #         cby+=1
    #     # check up
    #     if not is_blocked((new_box[0], new_box[1]-1), state_list):
    #         cwy+=1
    #     if not (get_tile((new_box[0], new_box[1]-1), state_list) == Tiles.BOX or get_tile((new_box[0], new_box[1]-1), state_list) == Tiles.BOX_ON_GOAL):
    #         cby+=1
    #     return cbx,cby,cwx,cwy

    # def move(cur, direction, state_list):
    #         """
    #             If you're the keeper, you can push
    #         """
    #         cx, cy = cur
    #         ctile = get_tile(cur, state_list)
            
    #         npos = cur
    #         if direction == "w":
    #             npos = cx, cy - 1
    #         if direction == "a":
    #             npos = cx - 1, cy
    #         if direction == "s":
    #             npos = cx, cy + 1
    #         if direction == "d":
    #             npos = cx + 1, cy
                
    #         print("NPOS: ", npos)

    #         if get_tile(npos, state_list) == Tiles.BOX or get_tile(npos, state_list) == Tiles.BOX_ON_GOAL:
    #             # Updates in that direction
    #             if direction == "w":
    #                 state_list = update_boxes(state_list, (cx, cy-2))
    #             if direction == "a":
    #                 state_list = update_boxes(state_list, (cx-2, cy))
    #             if direction == "s":
    #                 state_list = update_boxes(state_list, (cx, cy+2))
    #             if direction == "d":
    #                 state_list = update_boxes(state_list, (cx+2, cy))

    #         # Updates keeper 
    #         if direction == "w":
    #             state_list = update_man(state_list, (cx, cy-1))
    #         if direction == "a":
    #             state_list = update_man(state_list, (cx-1, cy))
    #         if direction == "s":
    #             state_list = update_man(state_list, (cx, cy+1))
    #         if direction == "d":
    #             state_list = update_man(state_list, (cx+1, cy))
            
    #         # Updates old position
    #         if get_tile(cur, state_list) == Tiles.MAN:
    #             state_list[cy][cx] = Tiles.FLOOR
    #         else:
    #             state_list[cy][cx] = Tiles.GOAL

    #         return state_list
            
    # def update_boxes(state_list, pos):
    #     """
    #         Checks if that position was on goal
    #     """
    #     if get_tile(pos, state_list) == Tiles.GOAL:
    #         state_list[pos[1]][pos[0]] = Tiles.BOX_ON_GOAL
    #     else:
    #         state_list[pos[1]][pos[0]] = Tiles.BOX
    #     return state_list

    # def update_man(state_list, pos):
    #     """
    #         Checks if that position was on goal
    #     """
    #     if get_tile(pos, state_list) == Tiles.GOAL or get_tile(pos, state_list) == Tiles.BOX_ON_GOAL:
    #         state_list[pos[1]][pos[0]] = Tiles.MAN_ON_GOAL
    #     else:
    #         state_list[pos[1]][pos[0]] = Tiles.MAN
    #     return state_list

    

    # def is_blocked(pos, state_list,direction=None):
    #     """Determine if mobile entity can be placed at pos."""
    #     x, y = pos
    #     print("IsBlocked? ", pos)
    #     if x not in range(0,len(state_list[0])) or y not in range(0,len(state_list)):
    #         print("Position out of map")
    #         return True
        
    #     if get_tile(pos, state_list) == Tiles.WALL:
    #         print("Position is a wall")
    #         return True
    #     if direction == "left"  :
    #         if (get_tile((x,y), state_list) == Tiles.BOX or get_tile((x,y), state_list) == Tiles.BOX_ON_GOAL) and (get_tile((x-1,y), state_list) == Tiles.BOX or get_tile((x-1,y), state_list) == Tiles.BOX_ON_GOAL):
    #             return True
    #     elif direction == "right"  :
    #         if (get_tile((x,y), state_list) == Tiles.BOX or get_tile((x,y), state_list) == Tiles.BOX_ON_GOAL) and (get_tile((x+1,y), state_list) == Tiles.BOX or get_tile((x+1,y), state_list) == Tiles.BOX_ON_GOAL):
    #             return True
    #     elif direction == "up"  :
    #         if (get_tile((x,y), state_list) == Tiles.BOX or get_tile((x,y), state_list) == Tiles.BOX_ON_GOAL) and (get_tile((x,y-1), state_list) == Tiles.BOX or get_tile((x,y-1), state_list) == Tiles.BOX_ON_GOAL):
    #             return True
    #     elif direction == "down"  :
    #         if (get_tile((x,y), state_list) == Tiles.BOX or get_tile((x,y), state_list) == Tiles.BOX_ON_GOAL) and (get_tile((x,y+1), state_list) == Tiles.BOX or get_tile((x,y+1), state_list) == Tiles.BOX_ON_GOAL):
    #             return True
    #     return False

   

    # def s(state_list):
    #     map_str = ""
    #     screen = {tile: symbol for symbol, tile in TILES.items()}
    #     for line in state_list:
    #         for tile in line:
    #             map_str += screen[tile]
    #         map_str += "\n"

    #     return map_str.strip()