import unittest

import mesa


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
