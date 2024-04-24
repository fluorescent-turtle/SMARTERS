import math
import random

import mesa
from mesa import Agent


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
        self.condition = "High"

    def step(self):
        if self.condition == "Cutting":
            """for neighbor in self.model.grid.iter_neighbors(self.pos, True):
            if neighbor.condition == "Fine":
                neighbor.condition = "On Fire"""
            self.condition = "Cut"


class GrassTassel(mesa.Agent):  # todo: bisogna caricare questo agente
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
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius


class IsolatedArea:
    def __init__(self, pos):
        self.pos = pos


class Opening:
    def __init__(self, pos):
        self.pos = pos


class EnclosureTassel:
    def __init__(self, unique_id):
        self.unique_id = unique_id


class BaseStation:
    def __init__(self, pos):
        self.pos = pos


class SquaredBlockedArea:
    def __init__(
            self,
            pos,
    ):
        self.pos = pos


class CircledBlockedArea:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius


class GuideLine:
    def __init__(self, pos):
        self.pos = pos


class MovingAgent(Agent):
    """
    An agent that moves on the grid.
    """

    def __init__(self, unique_id, grid, robot_data, resources, model, pos):
        """
        Initialize a new MovingAgent.

        Args:
            unique_id (int): Unique identifier for the agent.
            grid: Reference to the grid space.
            robot_data: Data related to the robot.
            resources (list): List of resource positions.
        """
        super().__init__(unique_id, model)
        self.grid = grid  # Reference to the grid space
        self.resources = resources
        self.pos = pos

    """def get_empty_cells(self):

        return [
            cell for cell in self.grid.coord_iter() if self.grid.is_cell_empty(cell)
        ]"""

    def step(self):
        """
        Move the agent to a neighboring cell if available.
        """
        # Get the right neighbour of the agent
        right_neighbor = (self.pos[0] + 1, self.pos[1])

        if (
                0 <= right_neighbor[0] < self.grid.width
                and 0 <= right_neighbor[1] < self.grid.height
        ):
            # Check if the right neighbor contains a GuideLine
            if self.grid.is_cell_empty(right_neighbor):
                contents = self.grid.get_cell_list_contents([right_neighbor])
                # Move forward until a non-GuideLine cell is found to the right
                while contents and isinstance(contents[0], GuideLine):
                    self.move_agent_to_right()
            else:
                # Move to a random neighbor if the right neighbor is not empty
                self.move_to_random_neighbor()

        else:
            # Move back if there's no right neighbor or it's out of bounds
            self.move_agent_to_left()

    def move_agent_to_left(self):
        """
        Move the agent to the left neighbor if available.
        """
        left_neighbor = (self.pos[0] - 1, self.pos[1])
        if self.grid.is_cell_empty(left_neighbor):
            self.grid.move_agent(self, left_neighbor)
            self.pos = left_neighbor
            print("NEW AGENT POSITION ----- ", left_neighbor)
        else:
            # If the left neighbor is not empty, move to a random neighbor
            self.move_to_random_neighbor()

    def move_agent_to_right(self):
        """
        Move the agent to the right neighbor if available.
        """
        right_neighbor = (self.pos[0] + 1, self.pos[1])
        if self.grid.is_cell_empty(right_neighbor):
            self.grid.move_agent(self, right_neighbor)
            self.pos = right_neighbor
            print("NEW AGENT POSITION ----- ", right_neighbor)

    def move_to_random_neighbor(self):
        """
        Move the agent to a random neighboring cell if available.
        """
        # Get all possible moves (neighbors) where the agent can move to
        possible_moves = [
            move
            for move in self.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            if move not in self.resources
        ]
        print("POSSIBLE MOVES ----- ", possible_moves)
        # Choose a random move from the list of possible moves
        new_position = random.choice(possible_moves)
        print("NEW AGENT POSITION ----- ", new_position)
        # Move the agent to the new position on the grid
        if self.grid.is_cell_empty(new_position):
            self.grid.move_agent(self, new_position)
