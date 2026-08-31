# 定义游戏的"规则"

from typing import List
from engine.agent import BaseAgent
from engine.constant import FOOD_SCORE
from engine.core import GameState, Action
from engine.layout import GameLayout
from engine.renderer import GameRenderer
from utils.pos_utils import manhattan_distance, Position2D


class SimpleRules:
    """
    简化版规则, 用于调试代码:
    - 墙面碰撞
    - 碰到豆后吃掉并计数和得分
    """
    @staticmethod
    def get_legal_action(state: GameState, action: Action, action_tol: float = 0.001):
        pacman_pos = state.pacman_position
        x_int, y_int = int(pacman_pos.x + 0.5), int(pacman_pos.y + 0.5)

        # 在两个点之间, 必须和之前的方向一致
        if manhattan_distance(pacman_pos, Position2D(x_int, y_int)) > action_tol:
            return [action]

        results = []
        for possible_action in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]:
            dx, dy = possible_action.direction_vector
            next_x, next_y = int(x_int + dx), int(y_int + dy)
            if not state.layout.walls[(next_x, next_y)]:
                results.append(possible_action)
        return results

    @staticmethod
    def apply_action(state: GameState, action: Action):
        legal_actions = SimpleRules.get_legal_action(state, action)
        if action not in legal_actions:
            # 停止移动
            state.pacman_action = Action.STOP
        else:
            act_dir = action.direction_vector
            next_pos = state.pacman_position + act_dir * Position2D(state.pacman_speed, state.pacman_speed)
            for food in state.layout.foods:
                if manhattan_distance(next_pos, Position2D(food[0], food[1])) < 0.5:
                    # 吃掉豆豆
                    state.score += FOOD_SCORE
                    state.layout.foods.remove(food)
                    break
            state.pacman_action = action

class BacisPacmanRules(SimpleRules):
    """
    经典吃豆人游戏规则
    """
    pass