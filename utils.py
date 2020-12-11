# AUTHORS: Francisca Barros (93102), Jose Sousa (93019) e Margarida Martins (93169)

from consts import Tiles, TILES
import math
from queue import Queue
class Util:
    def __init__ (self, map_state=None, init_boxes=None):
        self.map_state = map_state # Estado inicial do mapa
        self.curr_boxes = init_boxes # Coordenadas atuais das caixas
        self.deadends={} # Dicionário de deadends (usado na função 'possible moves')
        self.goals = set(self.filter_tiles([Tiles.BOX_ON_GOAL, Tiles.GOAL, Tiles.MAN_ON_GOAL])) if map_state is not None else None # Posições dos goals 
        self.dark_list, self.distanceToGoal = self.init_darklist() if self.goals is not None else (None,None) # Chama a função 'init_darklist'
        self.box = None # Usada para manter track da caixa em análise quando funcções são chamdas recursivamente

    def init_darklist(self):
        """
            A dark list é um array de arrays em que as poições que podem ser visitadas têm o valor de 1 e as que não podem ser têm o valor 0
            Esta função é chamada no init do Util, quando a SokobanTree é criada ou quando é feito um novo nível (update da tree).
            A distanceToGoal é um dicionário cuja chaves são posições dos goals e para cada chave temos uma matriz com os movimentos necessários de cada coordenada para esse goal. Peermite-nos calcular a heurística.
        """

        # Calcula o tamanho do nível
        horz_tiles, vert_tiles = len(self.map_state[0]), len(self.map_state)

        # inicializa o visited e distanceToGoal
        visited = [[0] * vert_tiles for _ in range(horz_tiles)]
        distanceToGoal={goal:[[1000] * vert_tiles for _ in range(horz_tiles)] for goal in self.goals}

        def check_not_blocked(pos):
            """
                Função definida em Dynamic Programming para facilitar o calculo dos valores da dark list.
            """
            x, y = pos

            if visited[x][y] or self.get_tile(pos) == Tiles.WALL:
                return

            visited[x][y] = 1

            # Verificar que a caixa pode ser empurrada ou não para as seguintes 4 coordenadas:
            #left
            if x - 2 > -1 and x - 2< horz_tiles and y > -1 and y < vert_tiles and not (self.get_tile((x - 2, y)) == Tiles.WALL):
                check_not_blocked((x - 1, y))
            # right
            if x + 2 > -1 and x + 2 < horz_tiles and y > -1 and y < vert_tiles and not (self.get_tile((x + 2, y)) == Tiles.WALL):
                check_not_blocked((x + 1, y))
            # down
            if x > -1 and x < horz_tiles and y + 2 > -1 and y + 2 < vert_tiles and not (self.get_tile((x, y + 2)) == Tiles.WALL):
                check_not_blocked((x, y + 1))
            #up
            if x > -1 and x < horz_tiles and y - 2 > -1 and y - 2< vert_tiles and not (self.get_tile((x, y - 2)) == Tiles.WALL):
                check_not_blocked((x, y - 1))
            return

        def distanceG(goal):
            """
                Caixa mais distante -> heuristica maior
                Calcula o número de movimentos necessários para chegar a um goal
            """
            distanceToGoal[goal][goal[0]][goal[1]]=0
            open_goals = Queue()
            open_goals.put(goal)
            while not open_goals.empty():
                x,y= open_goals.get()
                
                # left
                if distanceToGoal[goal][x-1][y] == 1000 and not (self.get_tile((x - 1, y )) == Tiles.WALL) and not (self.get_tile((x - 2, y)) == Tiles.WALL):
                    distanceToGoal[goal][x-1][y] = distanceToGoal[goal][x][y] + 1
                    open_goals.put((x - 1,y))
                # right
                if distanceToGoal[goal][x+1][y] == 1000 and not (self.get_tile((x + 1, y )) == Tiles.WALL) and not (self.get_tile((x + 2, y)) == Tiles.WALL):
                    distanceToGoal[goal][x+1][y] = distanceToGoal[goal][x][y] + 1
                    open_goals.put((x + 1,y))
                # down
                if distanceToGoal[goal][x][y+1] == 1000 and not (self.get_tile((x, y + 1)) == Tiles.WALL) and not (self.get_tile((x, y +2)) == Tiles.WALL):
                    distanceToGoal[goal][x][y+1] = distanceToGoal[goal][x][y] + 1
                    open_goals.put((x,y+1))
                # up
                if distanceToGoal[goal][x][y-1] == 1000 and not (self.get_tile((x, y - 1)) == Tiles.WALL) and not (self.get_tile((x, y -2)) == Tiles.WALL):
                    distanceToGoal[goal][x][y-1] = distanceToGoal[goal][x][y] + 1
                    open_goals.put((x,y-1))
                
                
        # Chamar as funções para todos os goals
        [check_not_blocked((x,y)) for x in range(horz_tiles) for y in range(vert_tiles) if (x,y) in self.goals]
        [distanceG((x,y)) for x in range(horz_tiles) for y in range(vert_tiles) if (x,y) in self.goals]

        return visited, distanceToGoal

    def heuristic_boxes(self, box):
        """
            Calculo da heurística para um determinado estado das caixas
        """
        # Calcula todas as combinções caixa-goal e ordena pela heurística
        calc_costs = sorted([(b, goal) for goal in self.goals  for b in box],key=lambda tpl : self.distanceToGoal[tpl[1]][tpl[0][0]][tpl[0][1]], reverse=True)

        # Inicializaos sets que vão ter as posições já atribuídas
        matchedBoxes=set()
        matchedGoals=set()

        heur=0
        while calc_costs !=[]:
            b,goal = calc_costs.pop()
            # Se a box e o goal ainda não foram atribuídos
            if not b in matchedBoxes and not goal  in matchedGoals:
                # Calcula a heurística
                h= self.distanceToGoal[goal][b[0]][b[1]]
                # Se a distância não for infinita (ou seja, é possível deslocar a caixa)
                if h!=1000:
                    heur+=h 
                    matchedBoxes.add(b)
                    matchedGoals.add(goal)
                
        # Para cada caixa não atribuída somar a distância mínima
        for b in box:
            if not b in matchedBoxes:
                heur+=min([self.distanceToGoal[goal][b[0]][b[1]] for goal in self.goals])
                matchedBoxes.add(b)
        return heur

    def heuristic(self, pos1, pos2):
        """
            Cálculo da distância de Manhattan - usado na heuristica do keeper
        """
        return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

    def completed(self, curr_boxes):
        """
            Dado os goals e as caixas verifica se as caixas estão todas nos goals.
            (Copiado do código fonte)
        """
        return all(box in self.goals for box in curr_boxes)

    def possible_keeper_actions(self, keeper_pos):
        """
            Calcula as ações possíveis do keeper dada a sua posição
        """
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
            Retorna a lista de ações possiveis de todas as caixas usando a função 'possible_moves'
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
        """
            Para uma dada caixa calcula os seus possíveis movimentos.
        """
        self.box = box
        possible_moves = set()

        x, y = box
        left = (x - 1, y)
        right = (x + 1, y)
        up = (x, y - 1)
        down = (x, y + 1)

        # Left
        # Não é simple deadlock ou parede AND não é uma caixa AND não está bloqueado na posição oposta à que queremos verificar (para o keeper poder empurrar a caixa)
        if self.dark_list[x-1][y] and not left in self.curr_boxes and not self.is_blocked(right):
            li= self.curr_boxes[:i] + (left,) + self.curr_boxes[i+1:]
            l=hash(li)
            # Se a posição ainda não tiver sido marcada como deadend (inválida)
            if not l in self.deadends :
                # Vê não é freeze_deadlock
                if not self.freeze_deadlock(left, set()):
                    possible_moves.add((li, left))
                # Se for adicionamos ao deadend
                else:
                    self.deadends[l] = 1

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
        """
            Verifica para uma dada posição se é freeze deadlock
            (de notar que a posição que é recebida já é o futuro move da caixa)
             
            É freeze deadlock quando:
            STEP 1 - Tem parede do lado direito e esquerdo da caixa - caixa bloqueada no eixo do x.
            STEP 2 - Tem um simple deadlock do lado direito e esquerdo da caixa  - caixa bloqueada no eixo do x.
            STEP 3 - Tem uma caixa do lado direito e esquerdo (uma destas caixas tem de estar bloqueada) - caixa bloqueada no eixo do x.
            ^ Processo igual para o eixo vertical
        """

        # tipo horizontal = 1
        # tipo vertical = 0

        # Para manter track das posições já vistas quando a função é chamada recursivamente (ajuda a evitar cirular checks - andar sempre a ver as mesmas posições)
        boxes_checked.add(pos)

        horizontal_block = True
        # if tipo é horizontal ou se não foi definido nenhum tipo
        if tipo or tipo is None:
            left = (pos[0]-1, pos[1])
            right = (pos[0]+1, pos[1])
            horizontal_block = False

            # STEP 1
            if self.get_tile(left) == Tiles.WALL or self.get_tile(right) == Tiles.WALL:
                horizontal_block = True
            # STEP 2
            if not horizontal_block and not self.dark_list[pos[0]-1][pos[1]] and not self.dark_list[pos[0]+1][pos[1]]:
                horizontal_block = True
            # STEP 3
            if not horizontal_block and left in self.curr_boxes and left != self.box and self.freeze_deadlock(left,  boxes_checked, 0):
                horizontal_block = True
            if not horizontal_block and right in self.curr_boxes and right != self.box and self.freeze_deadlock(right, boxes_checked, 0):
                horizontal_block = True

        vertical_block = True
        # if tipo é vertical (not horizontal) ou se não foi definido nenhum tipo
        if not tipo or tipo is None:
            up = (pos[0], pos[1]-1)
            down = (pos[0], pos[1]+1)
            vertical_block = False

            # STEP 1
            if self.get_tile(up) == Tiles.WALL or self.get_tile(down) == Tiles.WALL:
                vertical_block = True
            # STEP 2
            if not vertical_block and not self.dark_list[pos[0]][pos[1]-1] and not self.dark_list[pos[0]][pos[1]+1]:
                vertical_block = True
            # STEP 3
            if not vertical_block and up in self.curr_boxes and up != self.box and self.freeze_deadlock(up, boxes_checked, 1):
                vertical_block = True
            if not vertical_block and down in self.curr_boxes and down != self.box and self.freeze_deadlock(down, boxes_checked, 1):
                vertical_block = True

        # Verifica se todas as caixas (pelas quais ele passou) estão em goal
        if all(box in self.goals for box in boxes_checked):
            return False
        return vertical_block and horizontal_block

    def get_tile(self, pos):      
        """
            Retorna o tile na posição
            (copiado do código fonte)
        """
        x, y = pos
        return self.map_state[y][x]
    
    def filter_tiles (self, list_to_filter):
        """
            Retorna a lista de coordenadas dada uma lista de tiles
            (copiado do código fonte)
        """
        return [
            (x, y)
            for y, l in enumerate(self.map_state)
            for x, tile in enumerate(l)
            if tile in list_to_filter
        ]
