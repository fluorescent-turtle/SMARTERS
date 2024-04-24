import random

import mesa
from mesa import Agent

from Model.agents import GuideLine, GrassTassel


def find_first_empty_cell(model):
    grid = model.grid
    width, height = grid.width, grid.height
    for x in range(width):
        for y in range(height):
            cell_content = grid.get_cell_list_contents([(x, y)])
            if len(cell_content) == 0:
                return x, y
    return None


class Simulator(mesa.Model):
    """
    A model representing the behavior of a lawnmower robot.

    Parameters:
    """

    def __init__(self, grid, robot_data, resources, dim_tassel, robot):
        """
        Initialize the Simulator model.

        """
        super().__init__()
        self.schedule = mesa.time.StagedActivation(self)

        self.grid = grid

        self.datacollector = mesa.DataCollector(
            {
                "High": lambda m: self.count_type(m, "High"),
                "Cut": lambda m: self.count_type(m, "Cut"),
                "Cutting": lambda m: self.count_type(m, "Cutting"),
            }
        )

        # todo: ---sample ---- prendi la prima cella libera
        cell = find_first_empty_cell(self)
        print("FIRST EMPTY CELL: ", cell)
        if cell is not None:
            self.grid.place_agent(
                MovingAgent(1, grid, robot_data, resources, self, (cell[0], cell[1])),
                (cell[0], cell[1]),
            )
            self.schedule.add(
                MovingAgent(1, grid, robot_data, resources, self, (cell[0], cell[1]))
            )

        self.add_grass_tassels(
            self,
            self.grid,
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()

        self.datacollector.collect(self)

    @staticmethod
    def count_type(model, tassel_condition):
        """
        Helper method to count tassels in a given condition.
        """
        count = 0
        for tassel in model.schedule.agents:
            # if tassel.condition == tassel_condition:
            count += 1
        return count

    def add_grass_tassels(self, grid, dim_tassel):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if not get_instance(self.grid, x, y):
                    grass_tassel = GrassTassel((x, y), self, dim_tassel, "High")
                    add_resource(grid, grass_tassel, x, y)

    def find_neighbors(self, pos, radius):
        # Implementazione del metodo per trovare i vicini
        pass

    def notify(self, event_type, event_data):
        # Implementazione del metodo per notificare gli eventi
        pass
