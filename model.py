import itertools
import math
import random

import mesa
from mesa import Agent

from agents import (
    euclidean_distance,
    CircularIsolation,
    IsolatedArea,
    SquaredBlockedArea,
    CircledBlockedArea,
    GuideLine,
    BaseStation,
)


class MovingAgent(Agent):
    """
    An agent that moves on the grid.
    """

    def __init__(self, unique_id, model, grid, pos, resources):
        """
        Initialize a new MovingAgent.

        Args:
            unique_id (int): Unique identifier for the agent.
            model (Simulator): Reference to the simulation model.
            grid: Reference to the grid space.
            pos (tuple): Initial position of the agent.
            resources (list): List of resource positions.
        """
        super().__init__(unique_id, model)
        self.pos = pos  # Current position of the agent
        self.grid = grid  # Reference to the grid space
        self.resources = resources  # List of resource positions

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
        # Get all possible moves (neighbors) where the agent can move to
        possible_moves = [
            move
            for move in self.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            if move not in self.resources
        ]
        # Choose a random move from the list of possible moves
        new_position = random.choice(possible_moves)
        print("NEW AGENT POSITION ----- ", new_position)
        # Move the agent to the new position on the grid
        self.grid.move_agent(self, new_position)


def find_grid_center(width, height):
    """
    Find the center of a Mesa grid.

    Args:
        width (int): Width of the environment
        height (int): Height of the environment

    Returns:
        tuple: A tuple containing the x and y coordinates of the center of the grid.
    """
    center_row = height // 2  # Integer division to get the center row index
    center_col = width // 2  # Integer division to get the center column index
    if height % 2 == 0 and width % 2 == 0:
        center_row -= 1
        center_col -= 1
    return center_row, center_col


def tuple_with_least_difference(tuples, target_tuple):
    """
    Find the tuple in a list of tuples with the least difference from a target tuple.

    Args:
        tuples (list of tuple): List of tuples.
        target_tuple (tuple): The target tuple.

    Returns:
        tuple: The tuple from the list with the least difference from the target tuple.
    """
    min_difference = float("inf")
    closest_tuple = None
    for t in tuples:
        difference = abs(t[0] - target_tuple[0]) + abs(t[1] - target_tuple[1])
        if difference < min_difference:
            min_difference = difference
            closest_tuple = t
    return closest_tuple


def find_empty_neighbor(grid, coords):
    """
    Find an empty neighboring cell to the given coordinates.

    Parameters:
        grid (mesa.space.Grid): The grid space.
        coords (tuple): The coordinates to find an empty neighbor for.

    Returns:
        tuple: The coordinates of the empty neighbor, or the original coordinates if no empty neighbor is found.
    """
    neighbors = grid.get_neighborhood(coords, moore=True, include_center=False)
    for neighbor in neighbors:
        if grid.is_cell_empty(neighbor):
            return neighbor
    return coords


def calculate_position(self, center, biggest_area_coords, width, height):
    if center:
        center_coords = find_grid_center(width, height)
        least_diff_tuple = tuple_with_least_difference(
            biggest_area_coords, center_coords
        )
        least_diff_tuple = find_empty_neighbor(self.grid, least_diff_tuple)
        return least_diff_tuple
    else:
        random_coords = random.choice(biggest_area_coords)
        random_coords = find_empty_neighbor(self.grid, random_coords)
        return random_coords


def get_blocked_area_size(blocked_area):
    """
    Calculate the size (area) of a blocked area.

    Parameters:
        blocked_area (Agent): The blocked area agent.

    Returns:
        int: The size (area) of the blocked area.
    """

    if isinstance(blocked_area, SquaredBlockedArea):
        return blocked_area.width * blocked_area.length
    elif isinstance(blocked_area, CircledBlockedArea):
        return math.pi * blocked_area.radius ** 2
    else:
        return 0  # Return 0 for unsupported blocked area types


class Simulator(mesa.Model):
    """
    A model representing the behavior of a lawnmower robot.

    Parameters:
        robot_data (dict): Data related to the robot.
        environment_data (dict): Data related to the environment.
        tassel_dim (int): Dimension of the tassel.
        repetitions (int): Number of repetitions.
        cycle (int): Cycle number.
        position (tuple): Position of the base station.
        center (boolean): Center of the isolated area.
    """

    def __init__(
            self,
            robot_data,
            environment_data,
            tassel_dim,
            repetitions,
            cycle,
            position,
            center,
    ):
        """
        Initialize the Simulator model.

        Args:
            robot_data (dict): Data related to the robot.
            environment_data (dict): Data related to the environment.
            tassel_dim (int): Dimension of the tassel.
            repetitions (int): Number of repetitions.
            cycle (int): Cycle number.
            position (tuple): Position of the base station.
            center (boolean): Center of the isolated area.
        """
        super().__init__()
        # Initialize attributes from parameters
        self.environment_data = environment_data
        self.robot_data = robot_data
        self.width = environment_data["width"]
        self.length = environment_data["length"]
        self.schedule = mesa.time.StagedActivation(self)
        self.grid = mesa.space.SingleGrid(
            int(self.width), int(self.length), torus=False
        )
        self.counter = itertools.count
        self.dimension_tassel = tassel_dim
        self.repetitions = repetitions
        self.cycle = cycle
        self.position = position
        self.center = center
        self.min_height_blocked = environment_data["min_height_square"]
        self.max_height_blocked = environment_data["max_height_square"]
        self.min_width_blocked = environment_data["min_width_square"]
        self.max_width_blocked = environment_data["max_width_square"]
        self.num_blocked_squares = environment_data["num_blocked_squares"]
        self.num_blocked_circles = environment_data["num_blocked_circles"]
        self.radius = environment_data["radius"]
        self.resources = []

        corners = [
            (0, 0),
            (0, int(environment_data["length"]) - 1),
            (int(environment_data["width"]) - 1, 0),
            (int(environment_data["width"]) - 1, int(environment_data["length"]) - 1),
        ]
        random_corner = random.choice(corners)
        self.x_start, self.y_start = random_corner
        self.isolated_area_tassels = []
        if environment_data["isolated_area_shape"] == "Square":
            for i in range(
                    self.x_start,
                    int(self.x_start + self.environment_data["isolated_area_width"]),
            ):
                for j in range(
                        self.y_start,
                        int(self.y_start + self.environment_data["isolated_area_length"]),
                ):
                    randint = random.randint(0, 10256)
                    print("ISOLATED AREA POSITION: ", (i, j))
                    self.add_resource(IsolatedArea(randint, self), i, j)
                    self.schedule.add(IsolatedArea(randint, self))
                    self.resources.append((i, j))
                    self.isolated_area_tassels.append((i, j))
        else:
            self.fill_circular_area()

        for _ in range(self.num_blocked_squares):
            (x, y) = self.generate_valid_agent_position()
            squared_blocked_area = SquaredBlockedArea(
                (x, y),
                self.random.randint(self.min_width_blocked, self.max_width_blocked),
                self.random.randint(self.min_height_blocked, self.max_height_blocked),
                random.randint(0, 10000),
                self,
            )
            if self.grid.is_cell_empty((x, y)):
                print("SQUARED BLOCKED AREA: ")
                print((x, y))
                self.add_resource(squared_blocked_area, x, y)
                self.resources.append((x, y))

        for _ in range(self.num_blocked_circles):
            (x, y) = self.generate_valid_agent_position()
            circled_blocked_area = CircledBlockedArea(
                (x, y), environment_data["ray"], random.randint(0, 10000), self
            )
            if self.grid.is_cell_empty((x, y)):
                print("CIRCLED BLOCKED AREA: ")
                print((x, y))
                self.add_resource(circled_blocked_area, x, y)
                self.resources.append((x, y))

        # Populate the grid with perimeter guidelines
        for i in range(int(self.width)):
            for j in range(int(self.length)):
                if self.grid.is_cell_empty((i, j)):
                    perimeter_guide_line = GuideLine((i, j), i * j, self)
                    self.add_resource(perimeter_guide_line, i, j)
                    self.resources.append((i, j))
                else:
                    if any(
                            self.grid.is_cell_empty((i + dx, j + dy))
                            for dx in range(-1, 2)
                            for dy in range(-1, 2)
                            if 0 <= i + dx < int(self.width)
                               and 0 <= j + dy < int(self.length)
                    ):
                        for dx in range(-1, 2):
                            for dy in range(-1, 2):
                                new_x, new_y = i + dx, j + dy
                                if (
                                        0 <= new_x < int(self.width)
                                        and 0 <= new_y < int(self.length)
                                        and self.grid.is_cell_empty((new_x, new_y))
                                ):
                                    perimeter_guide_line = GuideLine(
                                        (new_x, new_y), new_x * new_y, self
                                    )
                                    self.add_resource(
                                        perimeter_guide_line, new_x, new_y
                                    )
                                    self.resources.append((new_x, new_y))
                                    break
                                else:
                                    continue
                        break
                    else:
                        print(f"Warning: no empty cell found near cell ({i}, {j}).")

        # If position for base station isn't known
        if position[0] < 0:
            biggest_area, coords = self.find_largest_blocked_area()
            # Calculate position for the base station
            self.base_station_position = calculate_position(
                self,
                center,
                coords,
                self.width,
                self.length,
            )
            # Add the base station to the grid
            self.add_resource(
                BaseStation(
                    self.base_station_position, self.base_station_position[0], self
                ),
                self.base_station_position[0],
                self.base_station_position[1],
            )
            self.schedule.add(
                BaseStation(
                    self.base_station_position, self.base_station_position[0], self
                )
            )
            self.resources.append(self.base_station_position)
        # If position for base station is known
        else:
            # Add the base station to the grid
            self.add_resource(
                BaseStation((position[0], position[1]), position[0], self),
                position[0],
                position[1],
            )
            self.schedule.add(
                BaseStation((position[0], position[1]), position[0], self)
            )
            self.resources.append(self.base_station_position)

        # Draw a line from the base station to a random tassel
        random_tassel = random.choice(self.isolated_area_tassels)
        if position[0] > 0:
            self.draw_line(position[0], position[1], random_tassel[0], random_tassel[1])
        else:
            self.draw_line(
                self.base_station_position[0],
                self.base_station_position[1],
                random_tassel[0],
                random_tassel[1],
            )

        print(self.resources)

        # Add a moving agent to the grid
        if self.grid.is_cell_empty((4, 5)):
            moving_agent = MovingAgent(1, self, self.grid, (4, 5), self.resources)
            self.add_resource(moving_agent, 4, 5)
            self.schedule.add(moving_agent)
        else:
            print("(4,5) not empty")

        self.running = True
        self.datacollector.collect(self)

    def fill_circular_area(self):
        """
        Fill the isolated circular area.
        """
        sqr_count = int(
            (math.pi * self.radius * self.radius) / (self.dimension_tassel ** 2)
        )
        angle_delta = math.pi * 2 / sqr_count
        for idx in range(sqr_count):
            ang = angle_delta * idx
            sx = round(self.x_start + self.radius * math.cos(ang))
            sy = round(self.y_start + self.radius * math.sin(ang))
            ox = round(sx + math.cos(ang + angle_delta) * self.dimension_tassel * 0.5)
            oy = round(sy + math.sin(ang + angle_delta) * self.dimension_tassel * 0.5)
            cx = round((ox + sx) / 2)
            cy = round((oy + sy) / 2)
            dist = euclidean_distance((cx, cy), (sx, sy))
            assert (
                    dist < self.dimension_tassel * 0.5
            ), f"Distance {dist} exceeded allowed limit."
            for i in range(-1, 2):
                for j in range(-1, 2):
                    p = (cx + i, cy + j)
                    if self.can_place(p):
                        self.add_resource(
                            CircularIsolation(
                                next(self.counter),
                                p,
                                self.radius,
                                (2 * math.pi * self.radius),
                                self,
                            ),
                            cx + i,
                            cx + j,
                        )
                        self.resources.append((cx + i, cx + j))
                        self.isolated_area_tassels.append((cx + i, cx + j))

    def find_largest_blocked_area(self):
        """
        Find the largest blocked area among all blocked areas.

        Returns:
            tuple or None: A tuple containing the largest blocked area agent and its coordinates,
                           or None if no blocked areas are present.
        """
        largest_blocked_area = None
        largest_area = 0
        largest_coords = None
        for cell_content, x, y in self.grid.coord_iter():
            if isinstance(cell_content, SquaredBlockedArea) or isinstance(cell_content, CircledBlockedArea):
                area = get_blocked_area_size(cell_content)
                if area > largest_area:
                    largest_area = area
                    largest_blocked_area = cell_content
                    largest_coords = (x, y)
        if largest_blocked_area:
            return largest_blocked_area, largest_coords
        else:
            return None

    def can_place(self, pos):
        """
        Check if a resource can be placed at a given position.

        Parameters:
            pos (tuple): Position to check.

        Returns:
            bool: True if a resource can be placed, False otherwise.
        """
        return (
                self.grid.is_cell_empty(*pos)
                and self.within_bounds(pos)
                and not any(
            euclidean_distance(pos, c) <= self.radius for c in self.get_circles()
        )
        )

    def within_bounds(self, pos):
        """
        Check if a position is within the bounds of the grid.

        Parameters:
            pos (tuple): Position to check.

        Returns:
            bool: True if the position is within bounds, False otherwise.
        """
        x, y = pos
        return 0 <= x < self.grid.width and 0 <= y < self.grid.height

    def get_circles(self):
        """
        Get the positions of all circular isolated areas.

        Returns:
            list: List of positions.
        """
        return [
            c.pos
            for c in self.grid.get_cell_list_contents
            if isinstance(c, CircularIsolation)
        ]

    def add_resource(self, resource, x, y):
        """
        Add a resource to the grid.

        Parameters:
            resource (Agent): The resource to add.
            x (int): X-coordinate of the position.
            y (int): Y-coordinate of the position.
        """
        if self.grid.is_cell_empty((x, y)):
            self.grid.place_agent(resource, (x, y))

    def generate_valid_agent_position(self):
        """
        Generate a valid position for an agent on the grid.

        Returns:
            tuple: A tuple containing the x and y coordinates of the valid position.
        """
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            if not self.grid.is_cell_occupied((x, y)):
                return x, y

    def draw_line(self, x1, y1, x2, y2):
        """
        Draw a line on the grid from the starting point (x1, y1) to the ending point (x2, y2).

        Args:
            x1 (int): The x-coordinate of the starting point.
            y1 (int): The y-coordinate of the starting point.
            x2 (int): The x-coordinate of the ending point.
            y2 (int): The y-coordinate of the ending point.
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while (x1, y1) != (x2, y2):
            self.set_cell(x1, y1)
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        self.set_cell(x1, y1)

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        self.datacollector.collect(self)

    def set_cell(self, x, y):
        """
        Set a cell on the grid with a perimeter guide line.

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
        """
        perimeter_guide_line = GuideLine((x, y), x * y, self)
        self.add_resource(perimeter_guide_line, x, y)
        self.resources.append((x, y))
