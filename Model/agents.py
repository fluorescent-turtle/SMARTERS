import math

import mesa


def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


class Robot(mesa.Agent):
    def __init__(self, pos, model):
        """
        Create a new robot.
        Args:
            pos: The robot's coordinates on the grid.
            model: Standard model reference for agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.condition = "High"

    def step(self):
        if self.condition == "Cutting":
            """for neighbor in self.model.grid.iter_neighbors(self.pos, True):
            if neighbor.condition == "Fine":
                neighbor.condition = "On Fire"""
            self.condition = "Cut"


class GrassTassel(mesa.Agent):
    """
    A grass tassel.

    Attributes:
        x, y: Grid coordinates
        condition: Can be "High", "Cutting", or "Cut"
        unique_id: (x,y) tuple.
    """

    def __init__(self, pos, model, dimension, condition):
        """
        Create a new tassel.
        Args:
            pos: The tassel's coordinates on the grid.
            model: Standard model reference for agent.
            dimension: The tassel's dimension
        """
        super().__init__(pos, model)
        self.pos = pos
        self.condition = "High"
        self.dimension = dimension

    def step(self):
        if self.condition == "Cutting":
            self.condition = "Cut"


class CircularIsolation:
    def __init__(self, pos, radius, coverage):
        self.pos = pos
        self.radius = radius
        self.coverage = coverage

    def contained_by_circle(self, target_pos):
        max_dist = euclidean_distance(self.pos, target_pos)
        return self.radius >= max_dist >= self.radius * (1 - self.tolerance)

    @property
    def tolerance(self):
        return self.coverage / 100


class IsolatedArea:
    def __init__(self, unique_id):
        self.unique_id = unique_id


class BaseStation:
    def __init__(self, pos):
        self.pos = pos


class SquaredBlockedArea:
    def __init__(self, pos, width, length):
        self.pos = pos
        self.width = width
        self.length = length


class CircledBlockedArea:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius


class GuideLine:
    def __init__(self, pos):
        self.pos = pos
