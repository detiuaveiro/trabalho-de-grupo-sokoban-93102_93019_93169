from mapa import Map
from consts import Tiles, TILES


def filter_tiles(list_to_filter, state_list):
    """Util to retrieve list of coordinates of given tiles."""
    return [
        (x, y)
        for y, l in enumerate(state_list)
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

def possible_actions(state_list):
    possible_actions = []
    keeper = filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL], state_list)[0]

    # move to left
    new_keeper = (keeper[0]-1, keeper[1])
    if not is_blocked(new_keeper, state_list) and not is_dead_end(new_keeper,"left", state_list):
        possible_actions.append((new_keeper,"a"))

    # move to right
    new_keeper = (keeper[0]+1, keeper[1])
    if not is_blocked(new_keeper, state_list) and not is_dead_end(new_keeper,"right", state_list):
        possible_actions.append((new_keeper,"d"))

    # move down
    new_keeper = (keeper[0], keeper[1]-1)
    if not is_blocked(new_keeper, state_list) and not is_dead_end(new_keeper,"down", state_list):
        possible_actions.append((new_keeper,"s"))

    # move up
    new_keeper = (keeper[0], keeper[1]+1)
    if not is_blocked(new_keeper, state_list) and not is_dead_end(new_keeper,"up", state_list):
        possible_actions.append((new_keeper,"w"))
    return possible_actions

    
def is_dead_end(new_keeper, move, state_list):
    """
        Checks if it's a dead end
        dead end: the box ends up on a corner
    """
    if get_tile(new_keeper, state_list) == Tiles.BOX or get_tile(new_keeper, state_list)== Tiles.BOX_ON_GOAL:
        if move == "left":
            new_box = (new_keeper[0]-1, new_keeper[1])
        elif move == "right":
            new_box = (new_keeper[0]+1, new_keeper[1])
        elif move == "down":
            new_box = (new_keeper[0], new_keeper[1]-1)
        else:
            new_box = (new_keeper[0], new_keeper[1]+1)
        if not get_tile(new_box, state_list) == Tiles.GOAL:
            cbx, cby, cwx, cwy = number_possibilities(new_box, state_list)
            # é canto nas paredes
            if cwx+cwy <= 2:
                return True
            # é "canto" nas caixas
            if cbx < 2 and cby < 2:
                return True
            # é "canto" com caixas e paredes
            if (cbx < 2 and cwy < 2) or (cby < 2 and cwx < 2):
                return True
    return False


def number_possibilities(new_box, state_list):
    if is_blocked(new_box, state_list):
        return 0,0,0,0
    cwx = 0
    cbx = 0
    cwy = 0
    cby = 0
    # check left
    if not is_blocked((new_box[0]-1, new_box[1]), state_list):
        cwx +=1
    if not get_tile((new_box[0]-1, new_box[1]), state_list) == Tiles.BOX or get_tile((new_box[0]-1, new_box[1]), state_list)== Tiles.BOX_ON_GOAL:
        cbx+=1
    # check right
    if not is_blocked((new_box[0]+1, new_box[1]), state_list):
        cwx +=1
    if not get_tile((new_box[0]+1, new_box[1]), state_list)== Tiles.BOX or get_tile((new_box[0]+1, new_box[1]), state_list) == Tiles.BOX_ON_GOAL:
        cbx+=1
    # check down
    if not is_blocked((new_box[0], new_box[1]-1), state_list):
        cwy+=1
    if not get_tile((new_box[0], new_box[1]-1), state_list) == Tiles.BOX or get_tile((new_box[0], new_box[1]-1), state_list) == Tiles.BOX_ON_GOAL:
        cby+=1
    # check up
    if not is_blocked((new_box[0], new_box[1]+1), state_list):
        cwy+=1
    if not get_tile((new_box[0], new_box[1]+1), state_list) == Tiles.BOX or get_tile((new_box[0], new_box[1]+1), state_list) == Tiles.BOX_ON_GOAL:
        cby+=1
    return cbx,cby,cwx,cwy

def move(cur, direction, state_list):
        """
            If you're the keeper, you can push
        """
        cx, cy = cur
        ctile = get_tile(cur, state_list)
        
        npos = cur
        if direction == "w":
            npos = cx, cy + 1
        if direction == "a":
            npos = cx - 1, cy
        if direction == "s":
            npos = cx, cy - 1
        if direction == "d":
            npos = cx + 1, cy
            
        print("NPOS: ", npos)

        if get_tile(npos, state_list) == Tiles.BOX or get_tile(npos, state_list) == Tiles.BOX_ON_GOAL:
            # Updates in that direction
            if direction == "w":
                state_list = update_boxes(state_list, (cx, cy+2))
            if direction == "a":
                state_list = update_boxes(state_list, (cx-2, cy))
            if direction == "s":
                state_list = update_boxes(state_list, (cx, cy-2))
            if direction == "d":
                state_list = update_boxes(state_list, (cx+2, cy))

        # Updates keeper 
        if direction == "w":
            state_list = update_man(state_list, (cx, cy+1))
        if direction == "a":
            state_list = update_man(state_list, (cx-1, cy))
        if direction == "s":
            state_list = update_man(state_list, (cx, cy-1))
        if direction == "d":
            state_list = update_man(state_list, (cx+1, cy))
        
        # Updates old position
        if get_tile(cur, state_list) == Tiles.MAN:
            state_list[cy][cx] = Tiles.FLOOR
        else:
            state_list[cy][cx] = Tiles.GOAL

        return state_list
        
def update_boxes(state_list, pos):
    """
        Checks if that position was on goal
    """
    if get_tile(pos, state_list) == Tiles.GOAL:
        state_list[pos[1]][pos[0]] = Tiles.BOX_ON_GOAL
    else:
        state_list[pos[1]][pos[0]] = Tiles.BOX
    return state_list

def update_man(state_list, pos):
    """
        Checks if that position was on goal
    """
    if get_tile(pos, state_list) == Tiles.GOAL:
        state_list[pos[1]][pos[0]] = Tiles.MAN_ON_GOAL
    else:
        state_list[pos[1]][pos[0]] = Tiles.MAN
    return state_list

def completed(state_list):
    """
        Given the state, checks if the map is completed (no empty goals!)
        state: list of lists
    """
    for individual_state in state_list:
        for element in individual_state:
            if element == Tiles.BOX:
                return False
    return True

def is_blocked(pos, state_list):
    """Determine if mobile entity can be placed at pos."""
    x, y = pos
    print("IsBlocked? ", pos)
    if x not in range(0,len(state_list)) or y not in range(0,len(state_list[0])):
        print("Position out of map")
        return True
    
    if get_tile(pos, state_list) == Tiles.WALL:
        print("Position is a wall")
        return True

    
    return False

def get_tile(pos, state_list):
    """Retrieve tile at position pos."""
    x, y = pos
    return state_list[y][x]