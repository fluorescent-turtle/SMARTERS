""" Copyright 2024 Sara Grecu

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

import math
import random
from abc import ABC

from Controller.movement_plugin import MovementPlugin
from Model.agents import (
    CircledBlockedArea,
    SquaredBlockedArea,
    IsolatedArea,
    Opening,
    GuideLine,
)
from Utils.utils import (
    within_bounds,
    get_grass_tassel,
    mowing_time,
    contains_any_resource,
)

def pass_on_tassels(pos, grid, diameter, grass_tassels, agent, dim_tassel):
    """
    Increments the grass tassels of neighboring cells and updates the agent's autonomy.

    :param pos: Tuple representing the current position of the agent.
    :param grid: The grid object representing the environment.
    :param diameter: The cutting diameter of the mower.
    :param grass_tassels: The grass tassels object.
    :param agent: The agent performing the action.
    :param dim_tassel: The dimension of each tassel.
    """
    radius = math.ceil((diameter / dim_tassel) / 2)  # Calculate the radius for neighbor search
    neighbors = grid.get_neighborhood(
        pos, moore=False, include_center=True, radius=radius
    )  # Get neighboring positions

    for neighbor in neighbors:
        if within_bounds(grid.width, grid.height, neighbor):
            if pass_on_current_tassel(
                grass_tassels, neighbor, agent, diameter, dim_tassel
            ) == 0:  # Pass on the current tassel to the neighbor
                break


def calculate_movement_time(speed, distance):
    return distance / speed

def pass_on_current_tassel(grass_tassels, new_pos, agent, cut_diameter, dim_tassel):
    """
    Increments the grass tassel at the new position and updates the agent's autonomy and path taken.

    :param grass_tassels: The grass tassels object.
    :param new_pos: Tuple representing the new position of the agent.
    :param agent: The agent performing the action.
    :param cut_diameter: The cutting diameter of the mower.
    :param dim_tassel: The dimension of each tassel.
    """
    grass_tassel = get_grass_tassel(
        grass_tassels, new_pos
    )  # Get the grass tassel at the new position
    if grass_tassel is not None:  # If there is a grass tassel
        mowing_t = mowing_time(agent.speed, agent.get_autonomy(), cut_diameter, dim_tassel * dim_tassel)
        if mowing_t > 0:
            agent.decrease_autonomy(mowing_t)  # Decrease the agent's autonomy
            agent.decrease_cycles(mowing_t)
            agent.path_taken.add(new_pos)  # Add the new position to the agent's path taken

            grass_tassel.increment()  # Increment the grass tassel
        else:
            return 0

class DefaultMovementPlugin(MovementPlugin, ABC):
    """
    Default movement plugin for controlling the agent's movement in the grid.

    :param movement_type: The type of movement ("random" or "systematic").
    :param grid: The grid object representing the environment.
    :param base_station_pos: Tuple representing the position of the base station.
    :param cut_diameter: The cutting diameter of the mower.
    :param grid_width: The width of the grid.
    :param grid_height: The height of the grid.
    :param dim_tassel: The dimension of each tassel.
    """

    def __init__(
            self,
            movement_type: str,
            grid,
            base_station_pos,
            boing: str,
            cut_diameter: int,
            grid_width: int,
            grid_height: int,
            dim_tassel,
    ):
        super().__init__(grid, base_station_pos, grid_width, grid_height, dim_tassel)  # Initialize the superclass

        self.real_pos = None
        self.angle = None
        self.movement_type = movement_type  # Set the movement type
        self.boing = boing  # Set the boing parameter
        self.cut_diameter = cut_diameter  # Set the cutting diameter
        self.dim_tassel = dim_tassel  # Set the tassel dimension

    def move(self, agent):
        """
        Moves the agent based on the specified movement type.

        :param agent: The agent to be moved.
        """
        if self.movement_type == "random":  # If movement type is random
            self.random_move(agent, agent.get_gt())
        elif self.movement_type == "systematic":  # If movement type is systematic
            self.systematic_move(agent, agent.get_gt())

    def random_move(self, agent, grass_tassels):
        """
        Moves the agent randomly using continuous angles for smooth movement.

        :param agent: The agent to be moved.
        :param grass_tassels: The grass tassels object.
        """
        if agent.get_first():  # First move, initialize angle randomly
            self.angle = random.uniform(5, 175)  # Random angle in radians
            agent.not_first()
            dx = math.cos(self.angle) * self.dim_tassel
            dy = math.sin(self.angle) * self.dim_tassel

            aux_pos = (self.pos[0] + dx, self.pos[1] + dy)
            agent.dir = (dx, dy)

            while (  # While the new position is out of bounds or already in the path taken
                    not self.is_valid_real_pos(aux_pos)
            ):
                self.angle = random.uniform(5, 175)
                dx = math.cos(self.angle) * self.dim_tassel
                dy = math.sin(self.angle) * self.dim_tassel
                aux_pos = (self.pos[0] + dx, self.pos[1] + dy)

        dx = math.cos(self.angle) * self.dim_tassel
        dy = math.sin(self.angle) * self.dim_tassel

        new_pos = (self.pos[0] + dx, self.pos[1] + dy)
        agent.dir = (dx, dy)

        if self.is_valid_real_pos(new_pos):
            discrete_pos = self.real_to_discrete(new_pos)
            if not contains_any_resource(
                    self.grid,
                    discrete_pos,
                    [CircledBlockedArea, SquaredBlockedArea],
                    self.grid_width,
                    self.grid_height,
            ) and not (  # If the current position is not isolated without an opening or is a guideline
                    IsolatedArea in self.grid.get_cell_list_contents(discrete_pos)
                    and Opening not in self.grid.get_cell_list_contents(discrete_pos)
            ):

                # Move the agent and update its path
                self.grid.move_agent(agent, discrete_pos)
                self.pos = new_pos
                agent.path_taken.add(self.pos)

                # Update grass tassels
                pass_on_tassels(
                    discrete_pos,
                    self.grid,
                    self.cut_diameter,
                    grass_tassels,
                    agent,
                    self.dim_tassel,
                )
            else:
                self.bounce(agent, grass_tassels)  # Perform bouncing
        else:
            self.bounce(agent, grass_tassels)  # Perform bouncing

    def systematic_move(self, agent, grass_tassels):
        pass

    def bounce(self, agent, grass_tassels):
        """
        Handles the bouncing behavior when encountering obstacles.

        :param agent: The agent performing the action.
        :param grass_tassels: The grass tassels object.
        """
        self.move_back(agent, grass_tassels)
        bounce_angle = random.uniform(5, 175)

        if self.boing == "random":
            # Calculate new direction based on bounce angle
            self.angle = (math.radians(bounce_angle) + self.angle) % 360
            dx = (math.cos(self.angle)) * self.dim_tassel
            dy = (math.sin(self.angle)) * self.dim_tassel

            new_real_pos = (
                self.pos[0] + dx,
                self.pos[1] + dy
            )
            agent.dir = (dx, dy)

            if self.is_valid_real_pos(new_real_pos):
                self.real_pos = new_real_pos
            else:
                self.bounce(agent, grass_tassels)

            self.pos = self.real_pos

            pass_on_tassels(
                self.real_to_discrete(self.real_pos),
                self.grid,
                self.cut_diameter,
                grass_tassels,
                agent,
                self.dim_tassel,
            )

            # Move the agent and update its path
            self.grid.move_agent(agent, self.real_to_discrete(self.real_pos))

    def is_valid_real_pos(self, real_pos):
        """
        Checks if the real position is within the grid bounds.

        :param real_pos: Tuple representing the real position.
        :return: True if the real position is valid, False otherwise.
        """
        x, y = real_pos
        return 0 <= x < self.grid_width * self.dim_tassel and 0 <= y < self.grid_height * self.dim_tassel

    def move_back(self, agent, grass_tassels):
        """
        Moves the agent back a specified number of tassels.

        :param agent: The agent to be moved.
        :param grass_tassels: The grass tassels object.
        """
        num_tass_back = math.floor(
            self.cut_diameter / self.dim_tassel
        )  # Calculate the number of tassels to move back
        for _ in range(num_tass_back):  # For each tassel to move back
            aux_real_pos = (self.pos[0] - agent.dir[0]), (self.pos[1] - agent.dir[1])
            aux_pos = self.real_to_discrete(aux_real_pos)

            if (  # If the new position is within bounds and doesn't contain blocked areas
                    within_bounds(self.grid_width, self.grid_height, aux_pos)
                    and SquaredBlockedArea not in self.grid.get_cell_list_contents(aux_pos)
                    and CircledBlockedArea not in self.grid.get_cell_list_contents(aux_pos)
                    and not (
                    IsolatedArea in self.grid.get_cell_list_contents(aux_pos)
                    and Opening not in self.grid.get_cell_list_contents(aux_pos)
            )
            ):
                self.pos = aux_real_pos
                # Move the agent and update its path
                self.grid.move_agent(agent, aux_pos)
                pass_on_tassels(
                    aux_pos,
                    self.grid,
                    self.cut_diameter,
                    grass_tassels,
                    agent,
                    self.dim_tassel,
                )
            else:
                break

    def real_to_discrete(self, real_pos):
        """
        Converts real coordinates to discrete grid coordinates.

        :param real_pos: Tuple representing the real position.
        :return: Tuple of discrete grid coordinates.
        """
        x, y = real_pos

        discrete_pos = math.ceil(x / self.dim_tassel), math.ceil(y / self.dim_tassel)
        if within_bounds(self.grid_width, self.grid_height, discrete_pos):
            return discrete_pos
        else:
            return math.floor(x / self.dim_tassel), math.floor(y / self.dim_tassel)
