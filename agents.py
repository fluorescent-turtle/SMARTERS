import math

from mesa import Agent, Model


def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


class CircularIsolation(Agent):
    def __init__(self, unique_id, pos, radius, coverage, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.radius = radius
        self.coverage = coverage

    def contained_by_circle(self, target_pos):
        max_dist = euclidean_distance(self.pos, target_pos)
        return self.radius >= max_dist >= self.radius * (1 - self.tolerance)

    @property
    def tolerance(self):
        return self.coverage / 100


class IsolatedArea(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.unique_id = unique_id


class BaseStation(Agent):
    def __init__(self, pos, unique_id: int, model: Model):
        super().__init__(unique_id, model)
        self.pos = pos


class SquaredBlockedArea(Agent):
    def __init__(self, pos, width, length, unique_id: int, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.width = width
        self.length = length


class CircledBlockedArea(Agent):
    def __init__(self, pos, radius, unique_id: int, model):
        super().__init__(unique_id, model)
        self.pos = pos
        self.radius = radius


class GuideLine(Agent):
    def __init__(self, pos, unique_id: int, model: Model):
        super().__init__(unique_id, model)
        self.pos = pos
