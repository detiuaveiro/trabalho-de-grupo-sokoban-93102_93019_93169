# AUTHORS: Francisca Barros (93102), Jose Sousa (93019) e Margarida Martins (93169)

from utils import *
import asyncio
import time
import heapq
from collections import deque

class Node:
    """
        Descreve os nós constituintes da árvore principal de pesquisa. 
    """
    __slots__ = ['boxes', 'parent', 'move', 'keeper', 'heuristic']
    def __init__(self,boxes,parent,move,keeper, heuristic):
        self.boxes = boxes # lista das coordenadas das caixas
        self.parent = parent # nó pai
        self.move = move # string das keys acumuladas que levaram até ao nó
        self.keeper = keeper # posição do keeper 
        self.heuristic = heuristic # heuristica associada ao nó

class SokobanTree:
    """
        Árvore de pesquisa das caixas até aos goals. 
    """
    def __init__ (self, map_state=None, init_boxes=None, goal_boxes=None):
        self.map_state = map_state # Estado inicial do mapa
        self.init_boxes = init_boxes # Posições iniciais das caixas
        self.goal_boxes = goal_boxes # Posições dos goals

        # Os seguintes atributos são atribuídos no 'update_level'
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
        self.map_state = new_map_state # atualiza o estado inicial 
        self.init_boxes = tuple(new_init_boxes) # atualiza as caixas iniciais
        self.goal_boxes = new_goal_boxes # atualiza os goals
        self.Util = Util(self.map_state, self.init_boxes) # Cria um objeto da biblioteca Util
        self.root = Node(self.init_boxes, None, "", self.Util.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0], 0) # Define a raíz da àrvore 
        self.open_nodes = [] # Inicializa os open_nodes vazios
        self.count=0 # Count usado para a heap
        heapq.heappush(self.open_nodes, (0, self.count, self.root)) # Mete a root na heap
        self.KeeperTree = KeeperTree(self.Util) # Inicializa a árvore de pesquisa
        self.used_states = {hash(self.init_boxes) : {self.root.keeper}} # Inicia o dicionário de estados usados (na pesquisa)
        
    """ 
        Inicia a pesquisa 
    """
    async def search(self):
        start = time.time()

        while self.open_nodes:

            node =  heapq.heappop(self.open_nodes)[2]

            if self.Util.completed(node.boxes):
                end = time.time()
                print(end - start)
                return node.move

            lnewnodes = []
            
            # A biblioteca Util calcula as actions para todas as caixas
            for curr_box, box_actions in self.Util.possible_actions(node.boxes):
                # para cada action numa box
                for new_boxes, action in box_actions:
                    # new_boxes - novas coordenadas
                    # action - posição futura da caixa

                    x, y = curr_box
                    left = (- 1, 0)
                    right = (1, 0)
                    up = (0, - 1)
                    down = (0, 1)   
                    
                    # calcula a 'direção' do move, se é left, right, etc...
                    sub = (action[0] - curr_box[0], action[1] - curr_box[1])

                    if sub == left:
                        push = "a"
                    elif sub == right:
                        push = "d"
                    elif sub == up:
                        push = "w"
                    else:
                        push = "s" 
                    
                    # posição para onde queremos que o keeper vá = 2*pos atual da caixa - posição para onde vai
                    keeper_target = (curr_box[0]*2 - action[0], curr_box[1]*2 - action[1])
                    
                    # chama a search do keeper: posição atual do keeper -> target 
                    keeper_moves =  self.KeeperTree.search_keeper(keeper_target, node.keeper)
                    await asyncio.sleep(0) 

                    if keeper_moves is not None:
                        newnode = Node(new_boxes, node, f"{node.move}{keeper_moves}{push}", curr_box, self.Util.heuristic_boxes(new_boxes))
                        h = hash(new_boxes)

                        # Prunning
                        # se ainda não foi verificado
                        if not h in self.used_states:
                            self.used_states[h] = {newnode.keeper} # adiciona aos used_states
                            heapq.heappush(self.open_nodes, (newnode.heuristic, self.count,newnode))
                            self.count +=1
                        else:
                            # Se o keeper conseguir ir a pelo menos uma das posições do estado então significa que o estado é repetido e não vamos querer repetir a suas expensão
                            if not any(self.KeeperTree.search_keeper(newnode.keeper, pos, 0) is not None for pos in self.used_states[h]):
                                heapq.heappush(self.open_nodes, (newnode.heuristic, self.count, newnode))
                                self.count += 1
                            self.used_states[h].add(newnode.keeper)
        return None

class KeeperNode:
    """
        Descreve os nós constituintes da árvore de pesquisa relativa ao keeper.
    """
    __slots__ = ['parent', 'keeper_pos', 'move', 'heuristic']
    def __init__(self, parent, keeper_pos, move, heuristic=None):
        self.parent = parent # nó pai 
        self.keeper_pos = keeper_pos # posição do keeper
        self.move = move # string das keys acumuladas dos movimentos do keeper
        self.heuristic = heuristic # heuristica associada ao nó

class KeeperTree:
    """
        Árvore de pesquisa (pesquisa um caminho da posição atual do keeper até a um dado target). Devolve as respetivas keys caso encontre solução.
    """
    def __init__(self, Util):
        self.Util = Util # herda a Util da SokobanTree
        self.keeper_nodes = None # lista de nós a expandir
    
    def search_keeper(self, target_pos, keeper_pos, strat=1):
        self.used_states_k = set() # lista de estados usados (o estado é constituído pela posição do keeper e do último move que o keeper fez)

        # estratégia A*
        if strat:
            self.keeper_nodes = [KeeperNode(None, keeper_pos, "", self.Util.heuristic(keeper_pos, target_pos))]
        # estretégia breath-first
        else:
            self.keeper_nodes = deque()
            self.keeper_nodes.append(KeeperNode(None, keeper_pos, "", 0))

        while self.keeper_nodes:

            node = self.keeper_nodes.pop()
            
            # se o keeper estiver no target
            if node.keeper_pos == target_pos:
                return node.move

            if len(node.move)!=0:
                self.used_states_k.add((node.keeper_pos, node.move[-1])) # adiiona aos estados utilizados
            
            lnewnodes = []
            
            # action - nova posição do keeper | key - "w", "s", ...
            for action, key in  self.Util.possible_keeper_actions(node.keeper_pos):
                # se o novo state ainda não foi explorado
                if not (action,key) in self.used_states_k:
                    # estratégia A*
                    if strat:
                        newnode = KeeperNode(node, action, f"{node.move}{key}", len(node.move)+ self.Util.heuristic(action, target_pos))
                        lnewnodes.append(newnode)    
                    # estretégia breath-first
                    else:
                        newnode = KeeperNode(node, action, f"{node.move}{key}", 0)
                        self.keeper_nodes.append(newnode)
            if strat:
                self.add_to_open(lnewnodes)
        return None

    def add_to_open(self,lnewnodes):    
        self.keeper_nodes.extend(lnewnodes)
        self.keeper_nodes.sort(key=lambda node : node.heuristic, reverse=True)
