from dataclasses import dataclass
from typing import Set, Tuple, List, Dict

from utils.pos_utils import Position2D


@dataclass(frozen=True)
class GameLayout:
    width: int
    height: int
    walls: Dict[Tuple[int, int], bool]
    foods: Set[Tuple[int, int]]
    capsules: Set[Tuple[int, int]]
    pacman_start: Position2D
    ghost_starts: List[Position2D]
    num_ghost: int

    @classmethod
    def from_file(cls, path: str) -> 'GameLayout':
        """
        解析 .lay 格式地图
        """
        with open(path) as f:
            lines = [line.rstrip('\n') for line in f if line.strip()]

        height = len(lines)
        width = max(len(line) for line in lines)
        foods, capsules = set(), set()
        pacman_start = Position2D(0, 0)
        ghost_starts = []
        walls = {}

        for y, line in enumerate(reversed(lines)):
            for x, char in enumerate(line):
                if char == '%':
                    walls[(x, y)] = True
                elif char == '.':
                    foods.add((x, y))
                elif char == 'o':
                    capsules.add((x, y))
                elif char == 'P':
                    pacman_start = Position2D(x, y)
                elif char == 'G':
                    ghost_starts.append(Position2D(x, y))

        num_ghost = len(ghost_starts)
        return cls(width, height, walls, set(foods),
                   set(capsules), pacman_start, ghost_starts, num_ghost)