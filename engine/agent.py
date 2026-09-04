from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, Tuple, Dict, TYPE_CHECKING
import random

from engine.constant import Action
from engine.rule import SimpleRules, get_legal_actions

if TYPE_CHECKING:
    from engine.core import GameState


class BaseAgent:

    def __init__(self, agent_index: int = 0):
        self.agent_index: int = agent_index

    def act(self, game_state: GameState) -> Action:
        raise NotImplementedError()


class GhostChaserAgent(BaseAgent):
    """
    追赶 pacman 的鬼魂, 贪心策略
    """
    def __init__(self, agent_index: int = 0):
        super().__init__(agent_index)
        self.prob_chasing = 0.8
        self.prob_flee = 0.8

    def act(self, game_state: GameState) -> Action:
        is_scared = game_state.ghost_scared_time[self.agent_index] > 0
        speed = game_state.ghost_speeds[self.agent_index]
        ghost_pos = game_state.ghost_positions[self.agent_index]
        
        if is_scared:
            speed = speed / 2
        
        legal = get_legal_actions(ghost_pos, game_state.layout.walls)
        
        # 如果没有合法动作则停止
        if len(legal) == 0:
            return Action.STOP
        
        new_pos = [ghost_pos + action.direction_vector * Position2D(speed, speed) for action in legal]
        dist = [manhattan_distance(pos, game_state.pacman_position) for pos in new_pos]
        if is_scared:
            # 尽可能远离 pacman
            best_idx = max(range(len(dist)), key=lambda i: dist[i])
            prob = self.prob_flee
        else:
            # 尽可能接近 pacman
            best_idx = min(range(len(dist)), key=lambda i: dist[i])
            prob = self.prob_chasing
        
        if random.random() < prob:
            return legal[best_idx]
        else:
            return random.choice(legal)

class GhostRandomWalkAgent(BaseAgent):
    def act(self, game_state: GameState) -> Action:
        pos = game_state.ghost_positions[self.agent_index]
        
        legal = get_legal_actions(pos, game_state.layout.walls)
        # 存在合法动作的时候不会随机到 STOP
        if len(legal) == 0:
            return Action.STOP
        else:
            return random.choice(legal)



class PacmanKeyBoardAgent(BaseAgent):

    WEST_KEY = 'a'
    EAST_KEY = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    KEY_TO_ACTION = {
        WEST_KEY: Action.LEFT,
        EAST_KEY: Action.RIGHT,
        NORTH_KEY: Action.UP,
        SOUTH_KEY: Action.DOWN,
        STOP_KEY: Action.STOP,
    }

    def __init__(self, agent_index: int = 0):
        super().__init__(agent_index)
        self.pressed_keys: Set[str] = set()
        self.waiting_keys: List[str] = []
        self.last_key = self.STOP_KEY

    def on_key_press(self, key: str) -> None:
        """由 renderer 的按键按下事件回调调用。"""
        if key in self.KEY_TO_ACTION:
            self.pressed_keys.add(key)
            self.waiting_keys.append(key)

    def on_key_release(self, key: str) -> None:
        """由 renderer 的按键释放事件回调调用。"""
        if key in self.KEY_TO_ACTION:
            self.pressed_keys.discard(key)

    def keys_waiting(self) -> List[str]:
        """返回自上次调用以来按下的键，并清空等待队列。"""
        keys = list(self.waiting_keys)
        self.waiting_keys = []
        return keys

    def keys_pressed(self) -> Set[str]:
        """返回当前仍按住的键。"""
        return set(self.pressed_keys)

    def _get_key(self) -> str:
        """优先取 waiting，其次取 pressed，都没有则使用上一次按键。"""
        keys = self.keys_waiting()
        if keys:
            return keys[-1]
        keys = self.keys_pressed()
        if keys:
            return keys.pop()
        return self.last_key

    def act(self, game_state: GameState) -> Action:
        """将按键映射为 Action；若新方向不可达则保持上一次方向。"""
        # 局部导入避免 agent.py 与 rule.py 循环引用

        key = self._get_key()
        action = self.KEY_TO_ACTION.get(key, Action.STOP)

        # 停止键直接响应
        if action == Action.STOP:
            self.last_key = key
            return Action.STOP

        legal_actions = SimpleRules.get_legal_action(game_state)
        if action in legal_actions:
            self.last_key = key
            return action

        # 新按键方向不可达，保持上一次按键方向
        fallback_action = self.KEY_TO_ACTION.get(self.last_key, Action.STOP)
        if fallback_action in legal_actions:
            return fallback_action
        
        # 新按键方向不可达，上一次按键方向也不可达，停止移动
        self.last_key = Action.STOP
        return Action.STOP
