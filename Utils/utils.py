import math
import random

from Model.agents import BaseStation, GuideLine


class StationGuidelinesStrategy:
    """
    Abstract class representing different strategies to place base stations
    based on guidelines.
    """

    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, resources, width, length
    ):
        pass


class PerimeterPairStrategy(StationGuidelinesStrategy):
    """
    Class to represent the strategy of placing a base station at a perimeter pair
    """

    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, resources, width, length
    ):
        base_station = None

        while not base_station:
            base_station = generate_perimeter_pair(width, length)

        return add_base_station(grid, base_station, resources)


# todo: biggest blocked area e' l'insieme dei tasselli perimetrali attorno all'area bloccata piu' grande
def generate_biggest_pair(biggest_blocked_area):
    random_tassel = random.choice(biggest_blocked_area)
    return random_tassel


def generate_perimeter_pair(width, length):
    """
    Generate a random pair of coordinates within the grid bounds.

    Args:
        width (int): Width of the grid.
        length (int): Length of the grid.

    Returns:
        tuple: Randomly generated a pair of coordinates.
    """
    choice = random.choice([0, 1])
    if choice == 0:
        return 0, random.randint(0, width - 1)
    else:
        return random.randint(0, length - 1), 0


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


def generate_biggest_center_pair(center_tassel, biggest_blocked_area):  # todo: fix
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
        strategy, grid, width, length, resources, random_corner_perimeter, central_tassel, biggest_area_blocked
):
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


def add_base_station(grid, position, resources):
    """
    Add a base station to the grid.

    Args:
        grid (MultiGrid): MultiGrid object.
        position (tuple): Position to add the base station.
        resources (list): List of resources on the grid.

    Returns:
        tuple or None: Position of the base station if added, None otherwise.
    """
    if within_bounds(grid, position):
        base_station = BaseStation((position[0], position[1]))
        add_resource(grid, base_station, position[0], position[1])
        resources.append(position)
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

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    # Initialize current position and direction vectors
    x, y = x1, y1
    dx_, dy_ = sx, sy

    cells_to_add = []
    while (x, y) != (x2, y2):

        # Check if the current cell already contains a GuideLine
        if grid[x][y] is not None and isinstance(grid[x][y], GuideLine):
            # Change direction randomly to avoid the GuideLine
            possible_dirs = [(-dx_, -dy_), (-dx_, dy_), (dx_, -dy_), (dx_, dy_)]
            dir_idx = random.randint(0, 3)  # Choose a random new direction
            dx_, dy_ = possible_dirs[dir_idx]

        cells_to_add.append((x, y))
        resources.append((x, y))
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += dx_
        if e2 < dx:
            err += dx
            y += dy_

    cells_to_add.append((x2, y2))
    resources.append((x2, y2))


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
    print("GUIDELINE: ", (x, y))
    guideline = GuideLine((x, y))
    add_resource(grid, guideline, x, y)
    resources.append((x, y))


def add_resource(grid, resource, x, y):
    if within_bounds(grid, (x, y)) and grid.is_cell_empty((x, y)):
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
