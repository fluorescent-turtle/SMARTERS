import math


def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


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
