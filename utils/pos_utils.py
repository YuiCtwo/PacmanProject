from dataclasses import dataclass



@dataclass
class Position2D:
    x: float
    y: float

    def __add__(self, other):
        return Position2D(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Position2D(self.x - other.x, self.y - other.y)
    def __mul__(self, other):
        return Position2D(self.x * other.x, self.y * other.y)

    def __hash__(self):
        return hash((self.x, self.y))


def manhattan_distance(pos1: Position2D, pos2: Position2D):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)