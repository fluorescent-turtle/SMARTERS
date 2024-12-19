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
import mesa.space as space

from Controller.movement_plugin import MovementPlugin
from Model.agents import (
    CircledBlockedArea,
    SquaredBlockedArea,
    IsolatedArea,
    Opening,
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
    radius = math.ceil((diameter / dim_tassel) / 2)  # Calculate the radius for neighbors search
    neighbors = grid.get_neighborhood(
        pos=pos, include_center=True, radius=radius, moore=False
    )

    for neighbor in neighbors:
        norm_neighbor = (
            neighbor[0] / dim_tassel if isinstance(neighbor[0], float) else neighbor[0],
            neighbor[1] / dim_tassel if isinstance(neighbor[1], float) else neighbor[1],
        )

        grass_tassel = get_grass_tassel(
            grass_tassels, norm_neighbor
        )  # Get the grass tassel at the new position

        if grass_tassel is not None:  # If there is a grass tassel
            grass_tassel.increment()

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
            self.random_move(agent, agent.grass_tassels)
        elif self.movement_type == "systematic":  # If movement type is systematic
            self.systematic_move(agent, agent.grass_tassels)

    def update_agent_autonomy(self, agent):
        mowing_t = mowing_time(agent.speed, agent.aux_autonomy, self.dim_tassel)
        agent.decrease_autonomy(
            mowing_t)
        agent.decrease_cycles(
            mowing_t)

    def random_move(self, agent, grass_tassels):
        """
        Moves the agent randomly using continuous angles for smooth movement.

        :param agent: The agent to be moved.
        :param grass_tassels: The grass tassels object.
        """
        if agent.first:  # First move, initialize angle randomly
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
                self.update_agent_autonomy(agent)
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
        # Step 1: Move back a step to avoid obstacles
        self.move_back(agent, grass_tassels)

        if self.boing == "random":
            # Step 2: Calculate a new direction based on a bounce angle
            bounce_angle = random.uniform(5, 175)  # Random angle for redirection
            self.angle = (math.radians(bounce_angle) + self.angle) % (2 * math.pi)  # Update angle

            # Step 3: Compute the new position
            dx = math.cos(self.angle) * self.dim_tassel
            dy = math.sin(self.angle) * self.dim_tassel
            new_real_pos = (self.pos[0] + dx, self.pos[1] + dy)

            # Step 4: Validate the new position
            if self.is_valid_real_pos(new_real_pos):
                self.real_pos = new_real_pos
                self.pos = self.real_pos
                self.update_agent_autonomy(agent)

                # Update the agent's position on the grid
                self.grid.move_agent(agent, self.real_to_discrete(self.real_pos))

                # Update grass tassels
                pass_on_tassels(
                    self.real_to_discrete(self.real_pos),
                    self.grid,
                    self.cut_diameter,
                    grass_tassels,
                    agent,
                    self.dim_tassel,
                )
            else:
                # Retry bouncing if the new position is invalid
                self.bounce(agent, grass_tassels)

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
                self.update_agent_autonomy(agent)

                pass_on_tassels(
                    self.real_to_discrete(self.pos),
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
