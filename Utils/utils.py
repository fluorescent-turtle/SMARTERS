import csv
import json
import math
import os
import random
from collections import Counter
from pathlib import Path

try:
    from Model.agents import (
        BaseStation,
        GuideLine,
        SquaredBlockedArea,
        GrassTassel,
        CircledBlockedArea,
        Opening,
        Robot,
        CircularIsolation,
        IsolatedArea,
    )
except ImportError:
    print('Error: Could not import `Model.agents`. Make sure it is installed and accessible.')
    exit()


class StationGuidelinesStrategy:
    """
    Abstract class representing different strategies to place base stations
    based on guidelines.
    """

    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, resources, width, length
    ):
        """
        Method to locate the base station on the grid.

        Args:
            grid (list): The grid representing the area.
            center_tassel (tuple): Coordinates of the center tassel.
            biggest_blocked_area (list): List of blocked areas.
            resources (dict): Resources available.
            width (int): Width of the grid.
            length (int): Length of the grid.

        Returns:
            tuple: Coordinates of the located base station.
        """
        pass


class PerimeterPairStrategy(StationGuidelinesStrategy):
    """Class to represent the strategy of placing a base station at a perimeter pair"""

    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, resources, width, length
    ):
        base_station = None

        while base_station is None:
            try:
                base_station = self.generate_perimeter_pair(width, length)
            except ValueError as e:
                print(f"Error generating perimeter pair: {e}")
                base_station = None

        return add_base_station(grid, base_station, resources)

    @staticmethod
    def generate_perimeter_pair(width, length):
        """Generate a random pair of coordinates within the grid bounds."""
        choice = random.choice([0, 1])
        if choice == 0:
            return 0, random.randint(0, width - 1)
        else:
            return random.randint(0, length - 1), 0


def generate_biggest_pair(biggest_blocked_area):
    """
    Function to generate the biggest pair from the blocked area.

    Args:
        biggest_blocked_area (list): List of blocked areas.

    Returns:
        tuple: Coordinates of the generated biggest pair.
    """
    random_tassel = random.choice(biggest_blocked_area)
    return random_tassel


def euclidean_distance(p1, p2):
    """
    Compute the Euclidean distance between two points.

    Args:
        p1 (Tuple[float]): First point represented as a tuple of float values (x, y).
        p2 (Tuple[float]): Second point represented as a tuple of float values (x, y).

    Returns:
        float: The Euclidean distance between the two points.
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def generate_biggest_center_pair(center_tassel, biggest_blocked_area):
    """
    Function to generate the biggest pair closest to the center tassel.

    Args:
        center_tassel (tuple): Coordinates of the center tassel.
        biggest_blocked_area (list): List of blocked areas.

    Returns:
        tuple or None: Coordinates of the generated biggest pair closest to the center tassel,
        or None if the blocked area is empty.
    """
    if len(biggest_blocked_area) > 0:
        nearest_tuple = biggest_blocked_area[0]

        nearest_distance = euclidean_distance(nearest_tuple, center_tassel)

        for tuple_elem in biggest_blocked_area:
            curr_distance = euclidean_distance(tuple_elem, center_tassel)
            if curr_distance < nearest_distance:
                nearest_distance = curr_distance
                nearest_tuple = tuple_elem

        return nearest_tuple
    else:
        return None


def get_most_frequent_elements(resources, grid):
    """
    Function to get the most frequent elements from a list of resources.

    Args:
        resources (list): List of resources.
        grid: Current grid
    Returns:
        list: List of the most frequent blocked areas.
    """
    # Count occurrences of each label
    label_count = Counter(
        obj
        for obj in resources
        if contains_resource(grid, (obj[0], obj[1]), SquaredBlockedArea)
    )

    if label_count:
        most_frequent_label, frequency = label_count.most_common(1)[0]
        elements_with_most_frequent_label = [
            obj
            for obj in resources
            if obj == most_frequent_label
               and contains_resource(grid, (obj[0], obj[1]), SquaredBlockedArea)
        ]
        return elements_with_most_frequent_label
    else:
        return []


def load_data_from_file(file_path):
    """
    Load data from an external JSON file.

    Parameters:
        file_path (str): The path to the JSON file.

    Returns:
        dict or None: A dictionary containing the loaded data or None if the file doesn't exist.
    """
    if not os.path.exists(file_path):
        print(f"Warning: File '{file_path}' could not be found.")
        return None

    # Open the JSON file and read its contents
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    # Extract relevant configuration data
    robot_config = data.get("robot", {})
    env_config = data.get("env", {})
    simulator_config = data.get("simulator", {})

    return robot_config, env_config, simulator_config


def generate_random_corner(width, length):
    """
    Generate a random corner coordinate pair within the specified dimensions.

    :param width: Width of the area being considered
    :param length: Length of the area being considered
    :return: Tuple representing x and y coordinates of a randomly chosen corner
    """
    return random.choice(
        [(0, 0), (0, length - 1), (width - 1, 0), (width - 1, length - 1)]
    )


class BiggestRandomPairStrategy(StationGuidelinesStrategy):
    """
    Class to represent the strategy of placing a base station at the biggest random pair
    """

    def locate_base_station(
            self, grid, central_tassel, biggest_blocked_area, resources, width, length
    ):

        base_station = None

        while not base_station:
            base_station = generate_biggest_pair(biggest_blocked_area)

        return add_base_station(grid, base_station, resources)


def find_central_tassel(grid, dim_tassel):
    rows = grid.height - 1 / dim_tassel
    cols = grid.width - 1 / dim_tassel

    if rows % 2 == 1 and cols % 2 == 1:
        # Numero dispari di righe e colonne
        central_row = rows // 2
        central_col = cols // 2
        return central_row, central_col
    else:
        # Numero pari di righe o colonne
        central_row = rows // 2 if rows % 2 == 1 else rows // 2 - 1
        central_col = cols // 2 if cols % 2 == 1 else cols // 2 - 1
        return central_row, central_col


class BiggestCenterPairStrategy(StationGuidelinesStrategy):
    """
    Class to represent the strategy of placing a base station at the biggest center pair
    """

    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, resources, width, length
    ):

        base_station = None

        while not base_station:
            base_station = generate_biggest_center_pair(
                center_tassel, biggest_blocked_area
            )

        return add_base_station(grid, base_station, resources)


def put_station_guidelines(
        strategy,
        grid,
        width,
        length,
        resources,
        random_corner_perimeter,
        central_tassel,
        biggest_area_blocked,
):
    """Put station guidelines based on a given strategy."""
    base_station_pos = strategy.locate_base_station(
        strategy, grid, central_tassel, biggest_area_blocked, resources, width, length
    )
    populate_perimeter_guidelines(width, length, grid, resources)
    draw_line(
        base_station_pos[0],
        base_station_pos[1],
        random_corner_perimeter[0],
        random_corner_perimeter[1],
        grid,
        resources,
    )

    # Find the farthest point from base station
    farthest_point = find_farthest_point(
        width, length, base_station_pos[0], base_station_pos[1]
    )

    # If farthest point is found, draw line from base station to it
    if farthest_point is not None:
        draw_line(
            base_station_pos[0],
            base_station_pos[1],
            farthest_point[0],
            farthest_point[1],
            grid,
            resources,
        )

    return base_station_pos


def add_base_station(grid, position, resources):
    """
    Add a base station to the grid.

    Args:
        grid (MultiGrid): MultiGrid object.
        position (tuple): Position to add the base station.
        resources: List of resources on the grid.

    Returns:
        tuple or None: Position of the base station if added, None otherwise.
    """
    if within_bounds(grid, position):
        base_station = BaseStation((position[0], position[1]))
        add_resource(grid, base_station, position[0], position[1])
        resources.append((position[0], position[1]))

        return position

    return None


def draw_line(x1, y1, x2, y2, grid, resources):
    """
    Draw a straight line connecting two points using Bresenham's algorithm, avoiding existing Guideline objects.

    Args:
        x1 (int): Starting point X coordinate.
        y1 (int): Starting point Y coordinate.
        x2 (int): Ending point X coordinate.
        y2 (int): Ending point Y coordinate.
        grid (MultiGrid): Mesa MultiGrid object where the agents and Guideline objects reside.
        resources (list): Resources available during initialization.

    Returns:
        None
    """

    def validate_coordinate(coord):
        i, j = coord
        return 0 <= i < grid.width and 0 <= j < grid.height

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    x, y = x1, y1

    cells_to_add = []
    err = dx - dy

    while (x, y) != (x2, y2) and validate_coordinate((x, y)):
        curr_cell = grid[x][y]
        if curr_cell is not None and not contains_resource(grid, (x, y), GuideLine):
            possible_dirs = [(sx, sy), (sx, -sy), (-sx, sy), (-sx, -sy)]
            dir_idx = random.randint(0, 1)
            new_dir = possible_dirs[dir_idx]
            sx_, sy_ = new_dir
            resources.append((x, y))
        else:
            sx_, sy_ = sx, sy

        cells_to_add.append((x, y))
        resources.append((x, y))

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx_
        if e2 < dx:
            err += dx
            y += sy_

        print("GUIDELINE  DRAW LINE --------------------------: (x, y)", (x, y))

    cells_to_add.append((x2, y2))
    resources.append((x2, y2))
    print("GUIDELINE  DRAW LINE --------------------------: (x2, y2)", (x2, y2))

    return cells_to_add, resources


def create_csv(grid, base_station_pos):
    if base_station_pos is not None:
        name = "grid_base_station.csv"
    else:
        name = "grid.csv"

    with open(Path("./View/" + name), mode="w", newline="") as my_file:
        # Create a writer object
        writer = csv.writer(my_file)

        # Write header row
        writer.writerow(["Width: " + str(grid.width - 1)])
        writer.writerow(["Height: " + str(grid.height - 1)])

        for x in range(grid.width - 1):
            for y in range(grid.height - 1):
                cell_contents = grid.get_cell_list_contents((x, y))
                writer.writerow(["Grid Tassel " f"({x},{y}): "])
                content_row = []
                for agent in cell_contents:
                    if isinstance(agent, GuideLine):
                        content_row.append("GuideLine")
                    elif isinstance(agent, GrassTassel):
                        content_row.append("GrassTassel")
                    elif isinstance(agent, SquaredBlockedArea):
                        content_row.append("SquaredBlockedArea")
                    elif isinstance(agent, CircledBlockedArea):
                        content_row.append("CircledBlockedArea")
                    elif isinstance(agent, Opening):
                        content_row.append("Opening")
                    elif isinstance(agent, Robot):
                        content_row.append("Robot")
                    elif isinstance(agent, CircularIsolation):
                        content_row.append("CircularIsolation")
                    elif isinstance(agent, IsolatedArea):
                        content_row.append("IsolatedArea")
                    elif isinstance(agent, BaseStation) and agent.pos is not None:
                        content_row.append("BaseStation")

                writer.writerow(content_row)


def tassels_csv(width, height, name, grid):
    flat_indices = ((x, y) for x in range(width - 1) for y in range(height - 1))

    with open(Path("./View/" + name + ".csv"), mode="w", newline="") as my_file:
        # Create a writer object
        writer = csv.writer(my_file)

        # Write header row
        writer.writerow(["Width:", str(width - 1), "Height:", str(height - 1)])

        for i, j in flat_indices:
            cell_contents = grid.get_cell_list_contents((i, j))

            specific_agent = next(
                (agent for agent in cell_contents if isinstance(agent, GrassTassel)),
                None,
            )
            writer.writerow(
                [
                    "Grid tassel:" + f"{i},{j}",
                    "counts: " + str(specific_agent.get_counts())
                    if specific_agent
                    else ["N/A"],
                ]
            )


def contains_resource(grid, cell, resource):
    """
    Check if a specific resource is present in a cell of the grid.

    Args:
        grid (Grid): The grid containing the cells.
        cell (tuple): Coordinates of the cell to check.
        resource (type): The type of resource to check for.

    Returns:
        bool: True if the cell contains the specified resource, False otherwise.
    """
    x, y = cell

    # Add these checks to ensure x and y are within bounds
    if 0 <= x < grid.width and 0 <= y < grid.height:
        cell_contents = grid.get_cell_list_contents(cell)

        specific_agent = next(
            (agent for agent in cell_contents if isinstance(agent, resource)), None
        )

        if specific_agent:
            return True
        else:
            return False
    else:
        raise IndexError("Cell coordinates are outside the grid boundaries: ", (x, y))


def set_guideline_cell(x, y, grid, resources):
    """
    Place a Guideline agent at a specific location within the grid.

    Args:
        x (int): X coordinate of the cell.
        y (int): Y coordinate of the cell.
        grid (SingleGrid or MultiGrid): Mesa Space object where the agent resides.
        resources (list): Resources available during initialization.

    Returns:
        None
    """
    guideline = GuideLine((x, y))
    add_resource(grid, guideline, x, y)
    resources.append((x, y))


def add_resource(grid, resource, x, y):
    """
    Add a resource to the specified coordinates on the grid, if within bounds.

    Args:
        grid (Grid): The grid to add the resource to.
        resource: The resource to add.
        x (int): The x-coordinate of the cell.
        y (int): The y-coordinate of the cell.
    """
    if within_bounds(grid, (x, y)):
        grid.place_agent(resource, (x, y))


def within_bounds(grid, pos):
    """
    Check if a position is within the grid bounds.

    Args:
        grid (SingleGrid or MultiGrid): Grid object.
        pos (tuple): Position to check.

    Returns:
        bool: True if position is within bounds, False otherwise.
    """

    x, y = pos
    return 0 <= x < grid.width and 0 <= y < grid.height


def find_farthest_point(width, height, fx, fy):
    """
    Find the farthest point from a fixed point on a rectangular grid.

    Args:
        width (int): Width of the grid.
        height (int): Height of the grid.
        fx (int): X coordinate of the fixed point.
        fy (int): Y coordinate of the fixed point.

    Returns:
        tuple: Coordinates of the farthest point.
    """
    max_dist = 0
    result = (-1, -1)

    for x in range(width):
        for y in range(height):
            if x != fx or y != fy:
                dist = math.sqrt((x - fx) ** 2 + (y - fy) ** 2)
                if dist > max_dist:
                    max_dist = dist
                    result = (x, y)

    print("FARTHEST POINT: ", result)

    return result


def populate_perimeter_guidelines(width, length, grid, resources):
    """
    Populate perimeter guidelines around blocked areas.

    Args:
        width (int): Width of the grid.
        length (int): Length of the grid.
        grid (MultiGrid): MultiGrid object.
        resources (list): List of resources on the grid.

    Returns:
        None
    """

    x = 0
    for y in range(length - 1):
        set_guideline_cell(x, y, grid, resources)
    x = width - 1
    for y in range(length - 1):
        set_guideline_cell(x, y, grid, resources)
    y = 0
    for x in range(width - 1):
        set_guideline_cell(x, y, grid, resources)
    y = length - 1
    for x in range(width - 1):
        set_guideline_cell(x, y, grid, resources)


def get_grass_tassel(grid, resources, pos):
    for res in resources:
        if res == pos and contains_resource(grid, pos, GrassTassel):
            return res

    return None
