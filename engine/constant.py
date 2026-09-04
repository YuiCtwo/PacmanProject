from enum import IntEnum

from utils.pos_utils import Position2D


INFO_PANE_HEIGHT = 32

# 得分相关
GHOST_SCORE = 200
FOOD_SCORE = 10
GAMEOVER_SCORE = -500
CAPSULE_SCORE = 0

GHOST_SCARE_TIME = 40

COLLISION_TOL = 0.7


class Action(IntEnum):
    STOP = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    @property
    def direction_vector(self) -> Position2D:
        return {
            Action.STOP: Position2D(0, 0),
            Action.UP: Position2D(0, 1),
            Action.DOWN: Position2D(0, -1),
            Action.LEFT: Position2D(1, 0),
            Action.RIGHT: Position2D(-1, 0),
        }[self]