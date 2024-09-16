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

    Args:
        pos (tuple): The current position.
        grid: The grid object representing the environment.
        diameter (float): The cutting diameter of the mower.
        grass_tassels: The grass tassels object.
        agent: The agent performing the action.
        dim_tassel (int): The dimension of each tassel.
    """
    radius = math.floor(diameter / 2)  # Calculate the radius for neighbor search
    neighbors = grid.get_neighborhood(
        pos, moore=False, include_center=True, radius=radius
    )  # Get neighboring positions

    for neighbor in neighbors:
        if within_bounds(grid.width, grid.height, neighbor):
            pass_on_current_tassel(
                grass_tassels, neighbor, agent, diameter, dim_tassel
            )  # Pass on the current tassel to the neighbor


def pass_on_current_tassel(grass_tassels, new_pos, agent, cut_diameter, dim_tassel):
    """
    Increments the grass tassel at the new position and updates the agent's autonomy and path taken.

    Args:
        grass_tassels: The grass tassels object.
        new_pos (tuple): The new position.
        agent: The agent performing the action.
        cut_diameter (float): The cutting diameter of the mower.
        dim_tassel:
    """
    grass_tassel = get_grass_tassel(
        grass_tassels, new_pos
    )  # Get the grass tassel at the new position
    if grass_tassel is not None:  # If there is a grass tassel
        grass_tassel.increment()  # Increment the grass tassel

        mowing_t = mowing_time(  # Calculate the mowing time
            agent.speed, agent.get_autonomy(), cut_diameter, (dim_tassel * dim_tassel)
        )
        agent.decrease_autonomy(mowing_t)  # Decrease the agent's autonomy
        agent.path_taken.add(new_pos)  # Add the new position to the agent's path taken


class DefaultMovementPlugin(MovementPlugin, ABC):
    """
    Default movement plugin for controlling the agent's movement in the grid.

    Args:
        movement_type (str): The type of movement ("random" or "systematic").
        grid: The grid object representing the environment.
        base_station_pos (tuple): The position of the base station.
        boing (str): Unused parameter.
        cut_diameter (int): The cutting diameter of the mower.
        grid_width (int): The width of the grid.
        grid_height (int): The height of the grid.
        dim_tassel (int): The dimension of each tassel.
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
        super().__init__(
            grid, base_station_pos, grid_width, grid_height
        )  # Initialize the superclass

        self.movement_type = movement_type  # Set the movement type
        self.boing = boing  # Set the boing parameter
        self.cut_diameter = cut_diameter  # Set the cutting diameter
        self.dim_tassel = dim_tassel  # Set the tassel dimension

        self.directions = [  # Define the possible movement directions
            (0, 1),
            (1, 0),
            (0, -1),
            (1, -1),
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (1, 1),
        ]
        self.dx_tassel = {  # Define the direction to tassel mappings
            (1, 0): (0, -1),
            (1, -1): (-1, -1),
            (0, -1): (-1, 0),
            (-1, -1): (-1, 1),
            (-1, 0): (0, 1),
            (-1, 1): (1, 1),
            (0, 1): (1, 0),
            (1, 1): (1, -1),
        }
        self.sx_tassel = {  # Define the opposite direction to tassel mappings
            (1, 0): (0, 1),
            (1, -1): (-1, -1),
            (0, -1): (-1, 0),
            (-1, -1): (0, -1),
            (-1, 0): (-1, -1),
            (-1, 1): (1, 0),
            (0, 1): (1, 0),
            (1, 1): (0, 1),
        }

        self.up_sx_tassel = {  # Define the upward opposite direction to tassel mappings
            (1, 0): (1, 1),
            (1, -1): (1, 0),
            (0, -1): (1, -1),
            (-1, -1): (0, -1),
            (-1, 0): (-1, -1),
            (-1, 1): (-1, 0),
            (0, 1): (-1, 1),
            (1, 1): (0, 1),
        }

    def move(self, agent):
        """
        Moves the agent based on the specified movement type.

        Args:
            agent: The agent to be moved.
        """
        if self.movement_type == "random":  # If movement type is random
            self.random_move(agent, agent.get_gt())  # Perform random movement
        elif self.movement_type == "systematic":  # If movement type is systematic
            pass  # Placeholder for systematic movement

    def random_move(self, agent, grass_tassels):
        """
        Moves the agent randomly within the grid, updating its path and autonomy.

        Args:
            agent: The agent to be moved.
            grass_tassels: The grass tassels object.
        """
        if agent.get_first():  # If it's the agent's first move
            aux_pos = self.pos  # Get the current position
            agent.dir = random.choice(self.directions)  # Choose a random direction
            aux_pos = (
                aux_pos[0] + agent.dir[0],
                aux_pos[1] + agent.dir[1],
            )  # Calculate the new position

            while (  # While the new position is out of bounds or already in the path taken
                    not within_bounds(self.grid_width, self.grid_height, aux_pos)
                    or aux_pos in agent.path_taken
            ):
                aux_pos = self.pos  # Reset the position
                agent.dir = random.choice(
                    self.directions
                )  # Choose a new random direction
                aux_pos = (
                    aux_pos[0] + agent.dir[0],
                    aux_pos[1] + agent.dir[1],
                )  # Calculate the new position
            self.pos = aux_pos  # Update the current position
            agent.path_taken.add(self.pos)  # Add the new position to the path taken
            agent.not_first()  # Mark that the first move is complete

        agent.dx = self.dx_tassel[
            agent.dir
        ]  # Update the agent's direction to tassel mapping
        self.pos = (
            self.pos[0] + agent.dir[0],
            self.pos[1] + agent.dir[1],
        )  # Update the current position

        if within_bounds(
                self.grid_width, self.grid_height, self.pos
        ):  # If the new position is within bounds
            if within_bounds(  # If the next position in the same direction is within bounds
                    self.grid_width,
                    self.grid_height,
                    (self.pos[0] + agent.dir[0], self.pos[1] + agent.dir[1]),
            ) and not contains_any_resource(  # And the next position doesn't contain any resources
                self.grid,
                (self.pos[0] + agent.dir[0], self.pos[1] + agent.dir[1]),
                [CircledBlockedArea, SquaredBlockedArea],
                self.grid_width,
                self.grid_height,
            ):
                if (  # If the current position is not isolated without an opening or is a guideline
                        not (
                                IsolatedArea in self.grid.get_cell_list_contents(self.pos)
                                and Opening not in self.grid.get_cell_list_contents(self.pos)
                        )
                        or GuideLine in self.grid.get_cell_list_contents(agent.dx)
                        and CircledBlockedArea
                        not in self.grid.get_cell_list_contents(self.pos)
                        and SquaredBlockedArea
                        not in self.grid.get_cell_list_contents(self.pos)
                ):
                    if (
                            self.pos not in agent.path_taken
                    ):  # If the position is not already in the path taken
                        self.grid.move_agent(
                            agent, self.pos
                        )  # Move the agent to the new position

                        pass_on_tassels(
                            self.pos,
                            self.grid,
                            self.cut_diameter,
                            grass_tassels,
                            agent,
                            self.dim_tassel,
                        )
                    else:  # If the position is already in the path taken
                        aux_pos = self.pos  # Reset the position
                        agent.dir = random.choice(
                            self.directions
                        )  # Choose a new random direction
                        aux_pos = (
                            aux_pos[0] + agent.dir[0],
                            aux_pos[1] + agent.dir[1],
                        )  # Calculate the new position

                        while (  # While the new position is out of bounds, contains resources, or is isolated
                                not within_bounds(
                                self.grid_width, self.grid_height, aux_pos
                                )
                                or contains_any_resource(
                            self.grid,
                            aux_pos,
                            [CircledBlockedArea, SquaredBlockedArea],
                            self.grid_width,
                            self.grid_height,
                        )
                                or (
                                        IsolatedArea
                                        in self.grid.get_cell_list_contents(self.pos)
                                        and Opening
                                        not in self.grid.get_cell_list_contents(self.pos)
                                )
                        ):
                            aux_pos = self.pos  # Reset the position
                            agent.dir = random.choice(
                                self.directions
                            )  # Choose a new random direction
                            aux_pos = (
                                aux_pos[0] + agent.dir[0],
                                aux_pos[1] + agent.dir[1],
                            )  # Calculate the new position
                        self.pos = aux_pos  # Update the current position

                        self.grid.move_agent(
                            agent, self.pos
                        )  # Move the agent to the new position

                        pass_on_tassels(
                            self.pos,
                            self.grid,
                            self.cut_diameter,
                            grass_tassels,
                            agent,
                            self.dim_tassel,
                        )

                else:  # If the position is isolated without an opening
                    self.bounce(agent, grass_tassels)  # Bounce the agent
            else:  # If the next position contains resources
                self.bounce(agent, grass_tassels)  # Bounce the agent
        else:  # If the new position is out of bounds
            self.bounce(agent, grass_tassels)  # Bounce the agent

    def move_back(self, agent, grass_tassels):
        """
        Moves the agent back a specified number of tassels.

        Args:
            agent: The agent to be moved.
            grass_tassels: The grass tassels object.
        """
        num_tass_back = math.ceil(
            self.cut_diameter / self.dim_tassel
        )  # Calculate the number of tassels to move back
        for _ in range(num_tass_back):  # For each tassel to move back
            aux_pos = (self.pos[0] - agent.dir[0]), (
                    self.pos[1] - agent.dir[1]
            )  # Calculate the new position
            if (  # If the new position is within bounds and doesn't contain blocked areas
                    within_bounds(self.grid_width, self.grid_height, aux_pos)
                    and SquaredBlockedArea not in self.grid.get_cell_list_contents(aux_pos)
                    and CircledBlockedArea not in self.grid.get_cell_list_contents(aux_pos)
                    and not (
                    IsolatedArea in self.grid.get_cell_list_contents(aux_pos)
                    and Opening not in self.grid.get_cell_list_contents(aux_pos)
            )
            ):
                self.pos = aux_pos
                pass_on_tassels(
                    self.pos,
                    self.grid,
                    self.cut_diameter,
                    grass_tassels,
                    agent,
                    self.dim_tassel,
                )
            else:
                break

    def bounce(self, agent, grass_tassels):
        self.move_back(agent, grass_tassels)
        agent.dir = self.up_sx_tassel[agent.dir]
