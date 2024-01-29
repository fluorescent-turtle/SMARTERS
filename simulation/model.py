import random

import mesa
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
import numpy as np

from simulation.agent_isolated_area import IsolatedTassel
from simulation.agent_tassel import GrassTassel

"""class BaseStation:
    def __init__(self, resource_type, pos):
        self.resource_type = resource_type
        self.pos = pos
"""


class BlockedArea:
    def __init__(self, pos, width, length, shape):
        self.pos = pos
        self.width = width
        self.length = length
        self.shape = shape


class Simulator(mesa.Model):
    """
    Lawnmower's Behaviour model.
    """

    def __init__(self, dimension_tassel, width, height, min_height_blocked, max_height_blocked,
                 min_width_blocked, max_width_blocked, num_blocked_squares, angle_x, angle_y):

        # num_blocked_areas non e' necessario, perche' si puo' ricavare

        """
        Create a new model.

        Args:
            width, height: The size of the grid to model
            dimension_tassel: Grass tassel parameter

        """

        super().__init__()

        # Set up model objects
        self.dimension_tassel = dimension_tassel
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        self.min_height_blocked = min_height_blocked
        self.max_height_blocked = max_height_blocked
        self.min_width_blocked = min_width_blocked
        self.max_width_blocked = max_width_blocked
        self.num_blocked_squares = num_blocked_squares
        self.angle_x = angle_x
        self.angle_y = angle_y

        self.datacollector = mesa.DataCollector(
            {
                "High": lambda m: self.count_type(m, "High"),
                "Cut": lambda m: self.count_type(m, "Cut"),
                "Cutting": lambda m: self.count_type(m, "Cutting")
                # "HighIsolated": lambda m: self.count_type(m, "HighIsolated"),
                # "CuttingIsolated": lambda m: self.count_type(m, "CuttingIsolated"),
                # "CutIsolated": lambda m: self.count_type(m, "CutIsolated")
            }
        )

        # Place a grass tassel everywhere
        for contents, (x, y) in self.grid.coord_iter():
            new_tassel = GrassTassel((x, y), self, dimension_tassel)
            new_tassel.condition = "High"
            self.grid.place_agent(new_tassel, (x, y))
            self.schedule.add(new_tassel)

        # History of added resources (blocked areas)
        self.resources = []

        # Add to the map blocked squares
        for _ in range(num_blocked_squares):
            x = random.randint(0, width)
            y = random.randint(0, height)
            self.add_resource(BlockedArea(
                (x, y),
                self.random.randrange(min_height_blocked, max_height_blocked),
                self.random.randrange(min_width_blocked, max_width_blocked),
                "squares"), x, y)

        # todo: Add to the map circled squares

        # Add the isolated area
        self.add_resource(IsolatedTassel((angle_x, angle_y), self, dimension_tassel), angle_x, angle_y)

        self.running = True
        self.datacollector.collect(self)

    def add_resource(self, resource, x, y):
        # Place the base station
        self.grid.place_agent(resource, (x, y))

    def random_position(self, width, height):
        while True:
            x, y = random.randint(0, height - 1), random.randint(0, width - 1)
            if (not (x, y) in self.grid.get_cell_list_contents([(x, y)]) and
                    (x, y) not in [res.pos for res in self.resources]):
                break
        return x, y

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        """while self.repetitions > 0 & self.hours > 0.0:
            self.count_type(self, "Cut")  # todo: questo pero' lo dovrei mettere in un file

        self.running = False"""

    @staticmethod
    def count_type(model, tassel_condition):
        """
        Helper method to count tassels in a given condition in a given model.
        """
        count = 0
        for tassel in model.schedule.agents:
            if tassel.condition == tassel_condition:  # todo: qui dovrebbe segnalare le coordinate del tassello
                count += 1  # todo: qui dovrebbe segnalare se il tassello e' dell'area isolata  o meno
        return count

# todo: serve una funzione per determinare l'angolo della macchina
# todo: dovrebbe stampare la mappa generata in un file
# todo: dovrebbe stampare la mappa generata con la posizione della stazione base
# todo: pero' ci deve essere il vincolo che non deve passare nelel aree bloccate, e vedere come cambia
