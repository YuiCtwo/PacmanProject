from dataclasses import dataclass



@dataclass(frozen=True)
class Position2D:
    x: int | float
    y: int | float

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other):
        return Position2D(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Position2D(self.x - other.x, self.y - other.y)
    def __mul__(self, other):
        return Position2D(self.x * other.x, self.y * other.y)

    def copy(self):
        return Position2D(self.x, self.y)

def manhattan_distance(pos1: Position2D | tuple, pos2: Position2D | tuple):
    if isinstance(pos1, Position2D) and isinstance(pos2, Position2D):
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
    elif isinstance(pos1, tuple) and isinstance(pos2, tuple):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    else:
        raise TypeError("pos1 and pos2 must be both Position2D or both tuple")
