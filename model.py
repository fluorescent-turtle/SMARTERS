import itertools
import math
import random
from collections import namedtuple

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
        # Get the right neighbor of the agent
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
        self.grid.move_agent(self, new_position)


Point = namedtuple("Point", "x y")


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


def populate_perimeter_guidelines(self):
    rows = [[0, self.length], [0, self.width], [self.length - 1, self.width]]
    cols = [[0, self.length], [0, self.width], [self.width - 1, self.length]]

    for r in rows:
        for i in range(*r):
            if self.grid.is_cell_empty((i, r[1])):
                self._add_guideline((i, r[1]))

    for c in cols:
        for j in range(*c):
            if self.grid.is_cell_empty((c[0], j)):
                self._add_guideline((c[0], j))


def _add_guideline(self, coord):
    guide_line = GuideLine(coord, coord[0] * coord[1], self)
    self.add_resource(guide_line, *coord)
    self.resources.append(coord)
    print("ADDING PERIMETER GUIDELINE, ", coord)


def populate_blocked_areas(num_squares, num_circles, cls_instance, environment_data):
    for _ in range(num_squares):
        (x, y) = cls_instance.generate_valid_agent_position()
        width = cls_instance.random.randint(
            cls_instance.min_width_blocked, cls_instance.max_width_blocked
        )
        length = cls_instance.random.randint(
            cls_instance.min_height_blocked, cls_instance.max_height_blocked
        )

        for i in range(width):
            for j in range(length):
                new_x = x + i
                new_y = y + j
                if cls_instance.can_blocked_place((new_x, new_y)):
                    if cls_instance.grid.is_cell_empty((new_x, new_y)):
                        square_blocked_area = SquaredBlockedArea(
                            (new_x, new_y),
                            random.randint(0, 10000),
                            width,
                            length,
                            cls_instance,
                        )
                        cls_instance.add_resource(square_blocked_area, new_x, new_y)
                        cls_instance.resources.append((new_x, new_y))

    for _ in range(num_circles):
        (x, y) = cls_instance.generate_valid_agent_position()
        ray = environment_data["ray"]
        cls_instance.fill_circular_blocked_area(x, y, int(ray))


def generate_pair(width, length):
    print("width", width)
    print("length", length)
    """
    Generate a pair of integers that can only be (0, random(range(width)-1)) or (random(range(length)-1), 0).

    Parameters:
        width (int): The width of the range.
        length (int): The length of the range.

    Returns:
        tuple: A tuple representing the pair of integers.
    """
    choice = random.choice([0, 1])  # Randomly choose between 0 and 1
    if choice == 0:
        return 0, random.randint(0, width - 1)
    else:
        return random.randint(0, length - 1), 0


def add_two_base_stations(self, base_station_position):
    self.add_resource(
        BaseStation(base_station_position, base_station_position[0], self),
        base_station_position[0],
        base_station_position[1],
    )

    new_position = (base_station_position[0] + 1, base_station_position[1] + 1)
    self.add_resource(
        BaseStation(new_position, base_station_position[0], self),
        new_position[0],
        new_position[1],
    )

    self.schedule.add(
        BaseStation(base_station_position, base_station_position[0], self)
    )

    self.resources.append(base_station_position)


def choose_random_corner(environment_data):
    corners = [
        (0, 0),
        (0, int(environment_data["length"]) - 1),
        (int(environment_data["width"]) - 1, 0),
        (int(environment_data["width"]) - 1, int(environment_data["length"]) - 1),
    ]
    random_corner = random.choice(corners)
    return random_corner


class Simulator(mesa.Model):
    """
    A model representing the behavior of a lawnmower robot.

    Parameters:
        robot_data (dict): Data related to the robot.
        environment_data (dict): Data related to the environment.
        tassel_dim (int): Dimension of the tassel.
        repetitions (int): Number of repetitions.
        cycle (int): Cycle number.
    """

    def __init__(
            self,
            robot_data,
            environment_data,
            tassel_dim,
            repetitions,
            cycle,
    ):
        """
        Initialize the Simulator model.

        Args:
            robot_data (dict): Data related to the robot.
            environment_data (dict): Data related to the environment.
            tassel_dim (float): Dimension of the tassel.
            repetitions (int): Number of repetitions.
            cycle (int): Cycle number.
        """
        super().__init__()
        # Set environment parameters
        self.environment_data = environment_data
        self.width = environment_data["width"]
        self.length = environment_data["length"]
        self.isolated_shape = environment_data["isolated_area_shape"]
        self.min_height_blocked = environment_data["min_height_square"]
        self.max_height_blocked = environment_data["max_height_square"]
        self.min_width_blocked = environment_data["min_width_square"]
        self.max_width_blocked = environment_data["max_width_square"]
        self.num_blocked_squares = environment_data["num_blocked_squares"]
        self.num_blocked_circles = environment_data["num_blocked_circles"]
        self.radius = environment_data["radius"]
        self.isolated_area_width = environment_data["isolated_area_width"]
        self.isolated_area_length = environment_data["isolated_area_length"]
        self.isolated_area_tassels = []

        # Set robot parameters
        self.robot_data = robot_data

        # Set simulation parameters
        self.dimension_tassel = tassel_dim
        self.repetitions = repetitions
        self.cycle = cycle

        # Initialize model components
        grid_width = int(self.width)
        grid_height = int(self.length)
        self.schedule = mesa.time.StagedActivation(self)
        self.grid = mesa.space.SingleGrid(grid_width, grid_height, torus=False)
        self.counter = itertools.count
        self.resources = []
        self.base_station_position = None

        self.position = generate_pair(
            environment_data["length"], environment_data["width"]
        )

        # Add to the grid the isolated area
        self.initialize_isolated_area(self, self.isolated_shape, self.isolated_area_width, self.isolated_area_length)

        # Populate the grid with blocked areas
        populate_blocked_areas(
            self.num_blocked_squares, self.num_blocked_circles, self, environment_data
        )

        # Populate the grid with perimeter guidelines
        populate_perimeter_guidelines(self)

        print(self.resources)

        self.datacollector = mesa.DataCollector(
            {
                "High": lambda m: self.count_type(m, "High"),
                "Cut": lambda m: self.count_type(m, "Cut"),
                "Cutting": lambda m: self.count_type(m, "Cutting"),
            }
        )

        self.running = True
        self.datacollector.collect(self)

    def fill_circular_area(self, x_start, y_start):
        """
        Fill the isolated circular area.
        """

        sqr_count = int(
            (math.pi * self.radius * self.radius) / (self.dimension_tassel ** 2)
        )
        angle_delta = math.pi * 2 / sqr_count
        for idx in range(sqr_count):
            ang = angle_delta * idx
            sx = round(x_start + self.radius * math.cos(ang))
            sy = round(y_start + self.radius * math.sin(ang))
            ox = round(sx + math.cos(ang + angle_delta) * self.dimension_tassel * 0.5)
            oy = round(sy + math.sin(ang + angle_delta) * self.dimension_tassel * 0.5)
            cx = round((ox + sx) / 2)
            cy = round((oy + sy) / 2)
            dist = euclidean_distance((cx, cy), (sx, sy))
            assert (
                    dist < self.dimension_tassel * 0.5
            ), f"Distance {dist} exceeded allowed limit."
            for i in range(-self.radius, self.radius + 1):
                for j in range(-self.radius, self.radius + 1):
                    if i ** 2 + j ** 2 <= self.radius ** 2:
                        p = (cx + i, cx + j)
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
                            self.resources.append((cx + i, cy + j))
                            self.isolated_area_tassels.append((cx + i, cy + j))

    def fill_circular_blocked_area(self, start_x: int, start_y: int, radius: int):
        """
        Fill the isolated circular area.
        """
        squared_circle_count = int(
            (math.pi * radius * radius) / (self.dimension_tassel ** 2)
        )
        angle_delta = math.pi * 2 / squared_circle_count

        for idx in range(squared_circle_count):
            angle = angle_delta * idx

            center = Point(
                round(start_x + radius * math.cos(angle)),
                round(start_y + radius * math.sin(angle)),
            )
            next_center = Point(
                round(
                    center.x
                    + math.cos(angle + angle_delta) * self.dimension_tassel * 0.5
                ),
                round(
                    center.y
                    + math.sin(angle + angle_delta) * self.dimension_tassel * 0.5
                ),
            )

            midpoint = Point(
                round((next_center.x + center.x) // 2),
                round((next_center.y + center.y) // 2),
            )

            distance = euclidean_distance(
                (midpoint.x, midpoint.y), (center.x, center.y)
            )
            assert (
                    distance < self.dimension_tassel * 0.5
            ), f"Distance {distance} exceeded allowed limit."

            for i in range(-radius, (radius + 1)):
                for j in range(-radius, (radius + 1)):
                    if i ** 2 + j ** 2 <= radius ** 2:
                        point = Point(midpoint.x + i, midpoint.y + j)
                        if self.can_blocked_place(point):
                            new_resource = CircledBlockedArea(
                                point, radius, random.randint(0, 10256), self
                            )
                            self.add_resource(new_resource, point.x, point.y)
                            self.resources.append(point)
                            self.isolated_area_tassels.append(point)

    def can_place(self, pos):
        """
        Check if a resource can be placed at a given position.

        Parameters:
            pos (tuple): Position to check.

        Returns:
            bool: True if a resource can be placed, False otherwise.
        """

        return self.grid.is_cell_empty((pos[0], pos[1])) and self.within_bounds(pos)

    def can_blocked_place(self, pos):
        """
        Check if a resource can be placed at a given position.

        Parameters:
            pos (tuple): Position to check.

        Returns:
            bool: True if a resource can be placed, False otherwise.
        """

        return self.within_bounds(pos) and self.grid.is_cell_empty((pos[0], pos[1]))

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
            if isinstance(cell_content, SquaredBlockedArea) or isinstance(
                    cell_content, CircledBlockedArea
            ):
                area = get_blocked_area_size(cell_content)
                if area > largest_area:
                    largest_area = area
                    largest_blocked_area = cell_content
                    largest_coords = (x, y)
        if largest_blocked_area:
            return largest_blocked_area, largest_coords
        else:
            return None

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
            print("SET CELL: ", (x1, y1))
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
        Set a cell on the grid with a perimeter guideline.

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
        """
        perimeter_guide_line = GuideLine((x, y), x * y, self)
        self.add_resource(perimeter_guide_line, x, y)
        self.resources.append((x, y))

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

    def add_base_station(self, position):
        """
        Add a base station at the given position if it's within bounds and the cell is not occupied.

        Parameters:
            position (tuple): The position to add the base station.
        """
        if self.within_bounds(position) and not self.grid.is_cell_occupied(position):
            base_station = BaseStation((position[0], position[1]), position[0], self)
            self.add_resource(base_station, position[0], position[1])
            self.resources.append(position)
            self.schedule.add(base_station)

    def handle_isolated_area(self, shape, randint, x_start, y_start, isolated_area_width, isolated_area_length):
        if shape == "Square":
            for i in range(x_start, int(x_start + isolated_area_width)):
                for j in range(y_start, int(y_start + isolated_area_length)):
                    print("ISOLATED AREA POSITION: ", (i, j))
                    print(
                        "GRANDEZZA ISOLATED AREA POSITION: ",
                        isolated_area_length,
                        isolated_area_width,
                    )
                    self.add_resource(IsolatedArea(randint, self), i, j)
                    self.schedule.add(IsolatedArea(randint, self))
                    self.resources.append((i, j))
                    self.isolated_area_tassels.append((i, j))
        else:
            self.fill_circular_area(x_start, y_start)

    def initialize_isolated_area(self, isolated_shape, isolated_area_width, isolated_area_length, environment_data):
        randint = random.randint(0, 256)
        random_corner = choose_random_corner(environment_data)
        x_start, y_start = random_corner

        self.handle_isolated_area(isolated_shape, randint, x_start, y_start, isolated_area_width, isolated_area_length)
