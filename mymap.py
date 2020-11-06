from mapa import Map
from consts import Tiles, TILES

class Mymap(Map):

    # Non possible actions
    """
        keeper goes to wall
        delaying moving of ongoal boxes
        keeper pushes box to corner (dead end)
        keeper pushes box to side when there is no goal
    """
    def possible_actions(self):
        possible_actions=[]
        # move to left
        new_keeper = (self.keeper[0]-1,self.keeper[1])
        if not self.is_blocked(new_keeper) and not self.is_dead_end(new_keeper,"left"):
            possible_actions.append((new_keeper,"a"))

        # move to right
        new_keeper = (self.keeper[0]+ 1,self.keeper[1])
        if not self.is_blocked(new_keeper) and not self.is_dead_end(new_keeper,"right"):
            possible_actions.append((new_keeper,"d"))

        # move down
        new_keeper = (self.keeper[0],self.keeper[1]-1)
        if not self.is_blocked(new_keeper) and not self.is_dead_end(new_keeper,"down"):
            possible_actions.append((new_keeper,"s"))

        # move to left
        new_keeper = (self.keeper[0],self.keeper[1]+1)
        if not self.is_blocked(new_keeper) and not self.is_dead_end(new_keeper,"up"):
            possible_actions.append((new_keeper,"w"))
        return possible_actions
    
        
    def is_dead_end(self, new_keeper,move):
        if self.get_tile(new_keeper) == Tiles.BOX or self.get_tile(new_keeper)== Tiles.BOX_ON_GOAL:
            if move == "left":
                new_box= (new_keeper[0] -1, new_keeper[1])
            elif move == "right":
                new_box = (new_keeper[0] +1, new_keeper[1])
            elif move == "down":
                new_box = (new_keeper[0] , new_keeper[1]-1)
            else:
                new_box = (new_keeper[0] , new_keeper[1]+1)
            if not (self.get_tile(new_box) == Tiles.GOAL):
                cbx,cby,cwx,cwy= self.number_possibilities(new_box)
                # é canto nas paredes
                if cwx+cwy<=2:
                    return True
                # é "canto" nas caixas
                if cbx<2 and cby<2:
                    return True
                # é "canto" com caixas e paredes
                if (cbx<2 and cwy<2) or (cby<2 and cwx<2):
                    return True
        return False
    
    def number_possibilities(self,new_box):
        if self.is_blocked(new_box):
            return 0,0,0,0
        cwx =0
        cbx =0
        cwy =0
        cby =0
        # check left
        if not (self.is_blocked((new_box[0]-1, new_box[1]))):
            cwx +=1
        if not (self.get_tile((new_box[0]-1, new_box[1]))== Tiles.BOX or self.get_tile((new_box[0]-1, new_box[1]))== Tiles.BOX_ON_GOAL):
            cbx+=1
        # check right
        if not (self.is_blocked((new_box[0]+1, new_box[1]))):
            cwx +=1
        if not (self.get_tile((new_box[0]+1, new_box[1]))== Tiles.BOX or self.get_tile((new_box[0]+1, new_box[1]))== Tiles.BOX_ON_GOAL):
            cbx+=1
        # check down
        if not (self.is_blocked((new_box[0], new_box[1]-1))):
            cwy+=1
        if not (self.get_tile((new_box[0], new_box[1]-1))== Tiles.BOX or self.get_tile((new_box[0], new_box[1]-1))== Tiles.BOX_ON_GOAL):
            cby+=1
        # check up
        if not (self.is_blocked((new_box[0], new_box[1]+1))):
            cwy+=1
        if not (self.get_tile((new_box[0], new_box[1]+1))== Tiles.BOX or self.get_tile((new_box[0], new_box[1]+1))== Tiles.BOX_ON_GOAL):
            cby+=1
        return cbx,cby,cwx,cwy

    def __getlevel__(self):
        return self._level
    
        