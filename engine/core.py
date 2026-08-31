from enum import IntEnum
from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional, Set
import copy
import numpy as np

from engine.agent import BaseAgent, GhostAgent, AgentState
from engine.layout import GameLayout
from engine.renderer import GameRenderer
from engine.rule import BacisPacmanRules, SimpleRules
from utils.pos_utils import Position2D


class Action(IntEnum):
    STOP = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    @property
    def direction_vector(self) -> Position2D:
        return {
            Action.STOP: Position2D(0, 0),  # x, y
            Action.UP: Position2D(0, 1),
            Action.DOWN: Position2D(0, -1),
            Action.LEFT: Position2D(1, 0),
            Action.RIGHT: Position2D(-1, 0),
        }[self]


class GameState:

    def __init__(self, layout: GameLayout):
        self.layout = layout
        self.score: float = 0.0
        self.step_count: int = 0
        self.ghost_positions: List[Position2D] = []

        # 初始化出生点
        for idx, ghost_init_pos in enumerate(layout.ghost_starts):
            self.ghost_positions.append(ghost_init_pos)
        self.pacman_position: Position2D = layout.pacman_start

        # 玩家速度
        self.pacman_speed = 1.0
        self.pacman_action = Action.STOP

        # 玩家
        self.ghost_speeds = [1.0] * self.layout.num_ghost
        self.ghost_actions = [Action.STOP] * self.layout.num_ghost

        self.is_gameOver = False


class BasicGameRunner:
    # 主逻辑
    def __init__(self,
        layout: GameLayout,
        pacman_agent: BaseAgent,
        renderer: GameRenderer,
        quiet: bool = False,
        user_input: bool = True
    ):
        self._layout = layout
        self._pacman_agent = pacman_agent
        self._ghost_agents = [GhostAgent() for _ in range(self._layout.num_ghost)]
        self._renderer = renderer
        self._agents = [self._pacman_agent] + self._ghost_agents  # 玩家永远先行动
        self._quiet = quiet
        self._rule = SimpleRules
        self._user_input = user_input

        self._init()

    def _init(self):
        self._game_state = GameState(self._layout)
        self._agent_states = {}

    def _update(self):
        pacman_action = self._agent_states["pacman"]["next_action"]
        self._rule.apply_action(self._game_state, pacman_action)

    def run(self):

        while True:

            # 1. 玩家行动
            self._agent_states["pacman"] = self._pacman_agent.act(self._game_state)
            # 2. Ghost 行动
            for one_agent in self._ghost_agents:
                self._agent_states[f"ghost_{one_agent.agent_index}"] = one_agent.act(self._game_state)

            # 3. 更新游戏状态
            self._update()

            # 4. 判断游戏是否结束
            if self._game_state.is_gameOver:
                break

            # 5. 渲染
            self._renderer.render(self._game_state)

        # TODO: log

        self._renderer.close()

