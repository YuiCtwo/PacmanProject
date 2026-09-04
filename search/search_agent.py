import math
import networkx as nx

from collections import deque

from engine.agent import BaseAgent
from engine.core import GameState
from engine.layout import Layout
from .search_utils import generic_search, AStarSearch


class PacmanPrimSearchAgent(BaseAgent):
    
    def __init__(self, layout: Layout):
        super().__init__()
        self.G = nx.Graph()

        self.cached_path = {}
        self._precompute_food_path(layout)

        self.precompute_solution = []
        self._precompute_solution(layout)

        self.action_now = 0
    
    def _precompute_solution(self, layout: Layout):
        mst = self._build_prime_tree()
        visit_order = list(nx.dfs_preorder_nodes(mst, source=self.best_first_food))
        self.precompute_solution.append(self.best_first_actions)
        for i in range(1, len(visit_order)):
            self.precompute_solution.append(self.cached_path[(i - 1, i)])
        
    
    def _precompute_food_path(self, layout: Layout):
        foods = list(layout.foods)
        foods_index = list(range(len(foods)))
        foods_search = []
        for i in range(len(foods)):
            self.G.add_node(foods[i])
            search_problem = AStarSearch(start_position=layout.pacman_start, end_position=foods[i], layout=layout)
            search_result = generic_search(search_problem)
            foods_search.append(search_result)
        
        self.best_first_food = min(foods_index, key=lambda i: foods_search[i].cost)
        self.best_first_actions = foods_search[self.best_first_food].actions

        for i in range(len(foods)):
            for j in range(i + 1, len(foods)):
                search_problem = AStarSearch(start_position=foods[i], end_position=foods[j], layout=layout)
                search_result = generic_search(search_problem)
                cost = search_result.cost
                if math.isinf(cost):
                    raise Exception(f"No path found from {foods[i]} to {foods[j]}")
                
                self.G.add_edge(i, j, weight=cost)
                self.cached_path[(i, j)] = search_result.actions

    def _build_prime_tree(self):
        mst = nx.minimum_spanning_tree(self.G, weight='weight', algorithm='prim')
        return mst
    

    def get_action(self, state: GameState):
        return self.precompute_solution[self.action_now]
