import random

import mesa
from mesa import Agent

from agents import GuideLine


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

    def get_empty_cells(self):
        """
        Get a list of empty cells on the grid.

        Returns:
            list: List of empty cell positions.
        """
        return [
            cell for cell in self.grid.coord_iter() if self.grid.is_cell_empty(cell)
        ]

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
                if contents and isinstance(contents[0], GuideLine):
                    # Move forward until a non-GuideLine cell is found to the right
                    while self.grid.is_cell_empty(right_neighbor) and isinstance(
                            contents[0], GuideLine
                    ):
                        self.move_agent_to_right()
                else:
                    # Move to a random neighbor if the right neighbor is not empty
                    self.move_to_random_neighbor()
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

    def __init__(self, grid, robot_data, resources):
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
