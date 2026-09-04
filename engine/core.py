from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional, Set, TYPE_CHECKING
from copy import deepcopy

from engine.agent import BaseAgent, GhostRandomWalkAgent, PacmanKeyBoardAgent
from engine.constant import Action
from engine.layout import GameLayout
from engine.rule import BacisPacmanRules, SimpleRules
from utils.pos_utils import Position2D

if TYPE_CHECKING:
    from engine.renderer import GameRenderer


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
        self.is_gameWin = False

        # 豆子和大力丸的可见状态，由 renderer 读取
        self.food_visible: Dict[Tuple[int, int], bool] = {
            (x, y): True for x, y in layout.foods
        }
        self.capsule_visible: Dict[Tuple[int, int], bool] = {
            (x, y): True for x, y in layout.capsules
        }

        # 上一帧位置，供 renderer 做动画插值
        self.pacman_prev_pos = deepcopy(self.pacman_position)
        self.ghost_prev_pos = deepcopy(self.ghost_positions)

        self.ghost_scared_time = [0] * self.layout.num_ghost


class BasicGameRunner:
    # 主逻辑
    def __init__(self,
        layout: GameLayout,
        pacman_agent: BaseAgent,
        renderer: GameRenderer
    ):
        self._layout = layout
        self._pacman_agent = pacman_agent
        self._ghost_agents = [GhostRandomWalkAgent(idx) for idx in range(self._layout.num_ghost)]
        self._renderer = renderer
        self._agents = [self._pacman_agent] + self._ghost_agents  # 玩家永远先行动
        self._rule = SimpleRules

        self._init()

    def _init(self):
        self._game_state = GameState(self._layout)
        self._agent_states = {}
        if isinstance(self._pacman_agent, PacmanKeyBoardAgent):
            self._renderer.register_key_press_callback(self._pacman_agent.on_key_press)
            self._renderer.register_key_release_callback(self._pacman_agent.on_key_release)

    def run(self):

        while True:

            # 1. 玩家行动
            pacman_action = self._pacman_agent.act(self._game_state)
            
            # 2. 更新游戏状态
            self._rule.apply_pacman_action(self._game_state, pacman_action)
            self._rule.apply_collision(self._game_state)
            
            # 3. Ghost 行动
            for i, one_agent in enumerate(self._ghost_agents):
                ghost_action = one_agent.act(self._game_state)
                self._rule.apply_ghost_action(self._game_state, i, ghost_action)
            
            # 4. 更新游戏状态
            self._rule.apply_collision(self._game_state)

            # 5. 判断游戏是否结束
            if self._game_state.is_gameOver or self._game_state.is_gameWin:
                break

            # 6. 渲染
            self._renderer.render(self._game_state)

        # TODO: log
        self._renderer.close()

    def get_game_state(self) -> GameState:
        return self._game_state

