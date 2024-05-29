import math
from datetime import datetime

import mesa

from Model.agents import GrassTassel, Robot
from Utils.utils import create_csv, tassels_csv


class GrassCuttingMovementPlugin:
    def __init__(self, movement_plugin, cutting_type, grid, resources, pos):
        self.movement_plugin = movement_plugin
        self.cutting_type = cutting_type
        self.grid = grid
        self.resources = resources
        self.pos = pos

    def move(self):
        self.movement_plugin.move()


class Simulator(mesa.Model):
    """
    A model representing the behavior of a lawnmower robot.

    Parameters:
    """

    def __init__(self, grid, cycles, dim_tassel, base_station_pos, robot_plugin, speed):
        super().__init__()
        self.schedule = mesa.time.StagedActivation(self)
        self.grid = grid
        self.cycles = cycles

        self.speed = speed

        self.dim_tassel = dim_tassel
        self.base_station_pos = base_station_pos

        self.grass_tassels = []

        # Add grass tassels
        for contents, (x, y) in self.grid.coord_iter():
            new_grass = GrassTassel(
                int(datetime.now().time().microsecond), (x, y), self
            )
            self.grid.place_agent(new_grass, (x, y))
            self.schedule.add(new_grass)
            self.grass_tassels.append(new_grass)

        self.robot = Robot(0, self, robot_plugin, self.grass_tassels)

        # Add robot
        self.grid.place_agent(self.robot, self.base_station_pos)
        self.schedule.add(self.robot)
        self.running = True

    def step(self):
        self.schedule.step()
        for i in range(
                0, self.cycles, math.ceil(self.speed * self.dim_tassel)
        ):  # todo: quando sa che e' passata un'ora?
            self.robot.step()

        self.running = False
        tassels_csv(
            self.grid.width - 1, self.grid.height - 1, "tassels_counts", self.grid
        )
        create_csv(self.grid, self.base_station_pos)
