
# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2019,
#  Inteligência Artificial, 2014-2019

from abc import ABC, abstractmethod

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent, depth=0, cost=0, heuristic=0): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost # Custo de cada no
        self.heuristic = heuristic # 

    def in_parent(self, node):
        if self.parent is None:
            return False
        if self.parent.state == node.state:
            return True
        return self.parent.in_parent(node) 

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:

    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        root = SearchNode(problem.initial, None, 0, 0, self.problem.domain.heuristic(self.problem.initial, self.problem.goal))
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.length = 0
        self.terminals = 0 #nao conseguimos expandir (open-nodes nas extremidades ainda por abrir)
        self.non_terminals = 0
        self.avg_branching = None

        self.cost = 0 # Custo total solucao encontrada (soma custos transicoes)

        self.max_accumulated_cost = [root] # Lista com no(s) com maior custo acumulado

        self.avg_depth = 0 # Profundidade media
        self.depths = [] # Profundidade de todos os nos percorridos

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)
    
    # procurar a solucao
    def search(self, limit=None):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            # Verificar nos com maior custo acumulado
            if node.cost == self.max_accumulated_cost[0].cost and node not in self.max_accumulated_cost:
                self.max_accumulated_cost.append(node)
            elif node.cost > self.max_accumulated_cost[0].cost:
                self.max_accumulated_cost = [node]
            # Calculo da profundidade media
            self.depths.append(node)
            self.avg_depth = sum(self.depths)/len(self.depths)
            # Caso o no seja o pretendido
            if self.problem.goal_test(node.state):
                self.solution = node
                self.length = node.depth
                self.terminals = len(self.open_nodes)+1
                self.avg_branching = (self.terminals+self.non_terminals-1)/self.non_terminals          
                self.cost = node.cost
                return self.get_path(node)
            self.non_terminals += 1
            # No caso do limite nao ser nulo e a profundidade do no ser superior ao limite
            if limit is not None and node.depth >= limit:
                continue
            lnewnodes = []
            # for each possible action in the set of actions for that state
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                ct = self.problem.domain.cost(node.state, a)
                newnode = SearchNode(newstate, node, node.depth+1, node.cost+ct, self.problem.domain.heuristic(newstate, self.problem.goal))
                newnode.action = a
                if newstate not in self.get_path(node):
                    lnewnodes.append(newnode)        
            
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform': # Para a pesquisa de custo uniforme! Cidades ordenadas pelos custos
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key = lambda node: node.cost) # Ordenar nos pelos custos
        elif self.strategy == 'greedy': # Para a pesquisa gulosa
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key = lambda node: node.heuristic) # Ordenar nos pela heuristica
        elif self.strategy == 'a*': # Para a pesquisa gulosa
            self.open_nodes = sorted(self.open_nodes+lnewnodes, key = lambda node: node.heuristic+node.cost) # Ordenar nos pela heuristica



