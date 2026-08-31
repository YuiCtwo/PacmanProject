from dataclasses import dataclass
from typing import Tuple, Dict

from engine.core import Action, GameState


@dataclass(frozen=True)
class AgentState:
    position: Tuple[int, int]
    direction: Action = Action.STOP
    is_alive: bool = True

    def get_legal_neighbors(self, walls: set) -> Dict[Action, 'AgentState']:
        neighbors = {}
        x, y = self.position
        for action in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]:
            dx, dy = action.direction_vector
            nx, ny = x + dx, y + dy
            if (nx, ny) not in walls:
                neighbors[action] = AgentState((nx, ny), action, self.is_alive)
        neighbors[Action.STOP] = self
        return neighbors

class BaseAgent:

    def __init__(self, agent_index: int = 0):
        self.agent_index: int = agent_index

    def act(self, game_state: GameState) -> AgentState:
        raise NotImplementedError()


class RandomGhostAgent(BaseAgent):
    pass


class GhostAgent(BaseAgent):
    pass


class KeyBoardAgent(BaseAgent):
    pass