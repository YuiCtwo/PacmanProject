# 定义游戏的"规则"

from __future__ import annotations

from typing import List, TYPE_CHECKING, Dict
from engine.constant import (
    Action, FOOD_SCORE, GHOST_SCORE, GHOST_SCARE_TIME,
    COLLISION_TOL, GAMEOVER_SCORE, CAPSULE_SCORE
)
from engine.layout import GameLayout
from utils.pos_utils import manhattan_distance, Position2D

if TYPE_CHECKING:
    from engine.core import GameState


def get_legal_actions(position: Position2D, walls: Dict) -> List[Action]:
    results = []
    x, y = int(position.x + 0.5), int(position.y + 0.5)
    for action in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]:
        dx, dy = action.direction_vector
        nx, ny = x + dx, y + dy
        if (nx, ny) not in walls:
            results.append(action)
    return results

class SimpleRules:
    """
    简化版规则, 用于调试代码:
    - 墙面碰撞
    - 碰到豆后吃掉并计数和得分
    """
    @staticmethod
    def get_legal_action(state: GameState):
        pacman_pos = state.pacman_position
        return get_legal_actions(pacman_pos, state.layout.walls)

    @staticmethod
    def apply_collision(state: GameState):
        pacman_pos = state.pacman_position
        for idx, ghost_pos in enumerate(state.ghost_positions):
            if manhattan_distance(pacman_pos, ghost_pos) <= COLLISION_TOL:
                if state.ghost_scared_time[idx] > 0:
                    # kill ghost
                    state.score += GHOST_SCORE
                    state.ghost_positions[idx] = state.layout.ghost_starts[idx].copy()
                    state.ghost_scared_time[idx] = 0
                    state.ghost_prev_pos[idx] = state.layout.ghost_starts[idx].copy()
                    state.ghost_actions[idx] = Action.STOP
                else:
                    # killed by ghost
                    state.score -= GAMEOVER_SCORE
                    state.is_gameOver = True
    @staticmethod
    def apply_ghost_action(state: GameState, ghost_idx: int, action: Action):
        # 幽灵之间没有碰撞
        state.ghost_prev_pos[ghost_idx] = state.ghost_positions[ghost_idx].copy()

        if state.ghost_scared_time[ghost_idx] > 0:
            speed = state.ghost_speeds[ghost_idx] / 2
        else:
            speed = state.ghost_speeds[ghost_idx]

        state.ghost_positions[ghost_idx] = state.ghost_positions[ghost_idx] + action.direction_vector * Position2D(speed, speed)
        state.ghost_scared_time[ghost_idx] = max(0, state.ghost_scared_time[ghost_idx] - 1)

    @staticmethod
    def apply_pacman_action(state: GameState, action: Action):
        legal_actions = SimpleRules.get_legal_action(state)
        state.pacman_prev_pos = state.pacman_position

        # 每走一步时间步加 1，分数扣 1
        state.step_count += 1
        state.score -= 1

        if action not in legal_actions:
            # 停止移动
            state.pacman_action = Action.STOP
        else:
            act_dir = action.direction_vector
            next_pos = state.pacman_position + act_dir * Position2D(state.pacman_speed, state.pacman_speed)

            # 吃豆子
            food_pos = (int(next_pos.x + 0.5), int(next_pos.y + 0.5))
            if state.food_visible.get(food_pos, False):
                state.score += FOOD_SCORE
                state.food_visible[food_pos] = False

            # 吃大力丸
            if state.capsule_visible.get(food_pos, False):
                state.score += CAPSULE_SCORE
                state.capsule_visible[food_pos] = False
                for i in range(state.layout.num_ghost):
                    state.ghost_scared_time[i] = GHOST_SCARE_TIME

            state.pacman_action = action

        # 吃完所有豆子，游戏胜利
        if all(not visible for visible in state.food_visible.values()):
            state.is_gameWin = True

class BacisPacmanRules(SimpleRules):
    """
    经典吃豆人游戏规则
    """
    pass