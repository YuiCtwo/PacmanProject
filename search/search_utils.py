from __future__ import annotations

from collections import Queue, PriorityQueue
from typing import Protocol

from engine.core import GameState
from engine.layout import Layout
from engine.constant import Action
from engine.rule import get_legal_actions
from utils.pos_utils import Position2D, manhattan_distance


@dataclass
class SearchResult:
    actions: List[Action]
    cost: float

# 求 A 到 B 的最短路径, 经典寻路问题
class SearchProblem(Protocol):
    def get_start_state(self): ...
    def is_goal_state(self, state): ...
    def get_successors(self, state): ...


class BFSSearch(SearchProblem):
    """
    state: 
    """
    def __init__(
        self,
        start_position: Tuple[int, int],
        end_position: Tuple[int, int],
        layout: Layout,
    ):
        self.walls = layout.walls
        self.start_state = (start_position[0], start_position[1])
        self.end_state = (end_position[0], end_position[1])
        self.frontier = Queue()
    
    def get_start_state(self):
        return self.start_state, 0
    
    def is_goal_state(self, state)
        return state == self.end_state
    
    def get_successors(self, state):
        pos_x, pos_y = state
        results = []
        legal_actions = get_legal_actions(game_state, pos_x, pos_y)
        for action in legal_actions:
            dx, dy = action.direction_vector
            state = (pos_x + dx, pos_y + dy)
            cost = 1
            results.append((state, action, cost))
        return results

class AStarSearch(SearchProblem):
    def __init__(
        self,
        start_position: Tuple[int, int],
        end_position: Tuple[int, int],
        layout: Layout,
        heuristic_method: str = "manhattan"
    ):
        self.walls = layout.walls
        self.start_state = (start_position[0], start_position[1])
        self.end_state = (end_position[0], end_position[1])
        self.frontier = PriorityQueue()
        self.heuristic_method = heuristic_method
    
    def get_start_state(self):
        return self.start_state, 0

    def is_goal_state(self, state):
        return state == self.end_state
    
    def get_successors(self, state):
        pos_x, pos_y = state
        results = []
        legal_actions = get_legal_actions(game_state, pos_x, pos_y)
        for action in legal_actions:
            dx, dy = action.direction_vector
            state = (pos_x + dx, pos_y + dy)
            cost = 1 + get_heuristic_cost(state)
            results.append((state, action, cost))
        return results

    def get_heuristic_cost(self, state):
        if self.heuristic_method == "manhattan":
            return manhattan_distance(state, self.end_state)
        else:
            return 0


def generic_search(problem):
    """
    problem: SearchProblem 实例
    frontier: 存储待扩展节点的数据结构（Stack/Queue/PriorityQueue）
    """
    # 已访问集合，避免重复扩展
    visited = set()
    frontier = problem.frontier
    
    # 初始节点：(state, actions_so_far, cost_so_far)
    start, cost = problem.get_start_state()
    frontier.push((start, [], cost))
    
    while not frontier.isEmpty():
        state, actions, cost = frontier.pop()
        
        # 找到目标，返回动作序列, cost
        if problem.is_goal_state(state):
            return SearchResult(actions, cost)
        
        # 已访问过就跳过
        if state in visited:
            continue
        visited.add(state)
        
        # 扩展后继
        for successor, action, stepCost in problem.get_successors(state):
            if successor not in visited:
                new_actions = actions + [action]
                new_cost = cost + stepCost
                frontier.push((successor, new_actions, new_cost))
    
    return SearchResult([], float('inf'))  # 无解
