import math
import random
from collections import namedtuple
from agents import (
    SquaredBlockedArea,
    CircledBlockedArea,
    IsolatedArea,
    CircularIsolation,
    GuideLine,
    BaseStation,
)

Point = namedtuple("Point", "x y")


def generate_pair(width, length):
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


def generate_valid_agent_position(grid):
    """
    Generate a valid agent position on the grid.

    Args:
        grid (mesa.space.Grid): The grid space.

    Returns:
        tuple: A tuple containing the x and y coordinates of the valid position.
    """
    while True:
        x = random.randrange(grid.width)
        y = random.randrange(grid.height)
        if not grid.is_cell_occupied((x, y)):
            return x, y


def find_grid_center(width, height):
    """
    Find the center of a Mesa grid.

    Args:
        width (int): Width of the environment
        height (int): Height of the environment

    Returns:
        tuple: A tuple containing the x and y coordinates of the center of the grid.
    """
    center_row = height // 2
    center_col = width // 2
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

    Args:
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


def calculate_position(grid, center, biggest_area_coords, width, height):
    """
    Calculate the position for initializing an agent on the grid.

    Args:
        grid (SingleGrid): The grid space.
        center (bool): Whether to place the agent near the center of the grid.
        biggest_area_coords (list[tuple]): Coordinates of the biggest area on the grid.
        width (int): The width of the grid.
        height (int): The height of the grid.

    Returns:
        tuple: The coordinates of the position to initialize the agent.

    Notes:
        This function calculates the position to initialize an agent on the grid. If 'center' is True,
        it finds the center coordinates of the grid and selects the empty neighbor of the biggest area
        closest to the center. Otherwise, it randomly chooses one of the coordinates of the biggest area
        and selects its empty neighbor as the position to initialize the agent.
    """
    if center:
        center_coords = find_grid_center(width, height)
        least_diff_tuple = tuple_with_least_difference(
            biggest_area_coords, center_coords
        )
        least_diff_tuple = find_empty_neighbor(grid, least_diff_tuple)
        return least_diff_tuple
    else:
        random_coords = random.choice(biggest_area_coords)
        random_coords = find_empty_neighbor(grid, random_coords)
        return random_coords


def get_blocked_area_size(blocked_area):
    """
    Calculate the size (area) of a blocked area.

    Args:
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


def populate_perimeter_guidelines(width, length, grid, resources):
    """
    Populate perimeter guidelines on the grid.

    Args:
        width (int): Width of the grid.
        length (int): Length of the grid.
        grid (mesa.space.Grid): The grid space.
        resources (list): List of resources on the grid.
    """
    rows = [[0, length], [0, width], [length - 1, width]]
    cols = [[0, length], [0, width], [width - 1, length]]

    for r in rows:
        for i in range(*r):
            if grid.is_cell_empty((i, r[1])):
                _add_guideline(grid, (i, r[1]), resources)

    for c in cols:
        for j in range(*c):
            if grid.is_cell_empty((c[0], j)):
                _add_guideline(grid, (c[0], j), resources)


def _add_guideline(grid, coord, resources):
    """
    Add a guideline to the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        coord (tuple): The coordinates of the guideline.
        resources (list): List of resources on the grid.
    """
    guide_line = GuideLine(coord, coord[0] * coord[1])
    add_resource(grid, guide_line, *coord)
    resources.append(coord)


def add_base_station(grid, position, resources):
    """
    Add a base station to the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        position (tuple): The position to add the base station.
        resources (list): List of resources on the grid.
    """
    if within_bounds(grid, position) and not grid.is_cell_occupied(position):
        base_station = BaseStation((position[0], position[1]), position[0])
        add_resource(grid, base_station, position[0], position[1])
        resources.append(position)


def handle_isolated_area(
        grid,
        shape,
        randint,
        x_start,
        y_start,
        isolated_area_width,
        isolated_area_length,
        isolated_area_tassels,
        radius,
        dimension_tassel,
        resources,
        counter,
):
    """
    Handle the isolated area on the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        shape (str): The shape of the isolated area.
        randint (int): Random integer value.
        x_start (int): X-coordinate to start.
        y_start (int): Y-coordinate to start.
        isolated_area_width (int): Width of the isolated area.
        isolated_area_length (int): Length of the isolated area.
        isolated_area_tassels (list): List of tassels in the isolated area.
        radius (int): Radius of the area.
        dimension_tassel (float): Dimension of the tassel.
        resources (list): List of resources on the grid.
        counter (iterator): Iterator for counting.

    Notes:
        This function handles the placement of the isolated area on the grid based on its shape.
    """
    if shape == "Square":
        for i in range(x_start, int(x_start + isolated_area_width)):
            for j in range(y_start, int(y_start + isolated_area_length)):
                add_resource(grid, IsolatedArea(randint), i, j)
                resources.append((i, j))
                isolated_area_tassels.append((i, j))
    else:
        fill_circular_area(
            grid,
            radius,
            x_start,
            y_start,
            dimension_tassel,
            counter,
            resources,
            isolated_area_tassels,
        )


def choose_random_corner(environment_data):
    """
    Choose a random corner coordinate from the given environment data.

    Args:
        environment_data (dict): Data related to the environment, including width and length.

    Returns:
        tuple: A tuple containing the coordinates of the randomly chosen corner.

    Notes:
        This function randomly selects one of the four corners of the grid based on the width and length
        specified in the environment data. It returns the coordinates of the chosen corner.
    """
    corners = [
        (0, 0),
        (0, int(environment_data["length"]) - 1),
        (int(environment_data["width"]) - 1, 0),
        (int(environment_data["width"]) - 1, int(environment_data["length"]) - 1),
    ]
    random_corner = random.choice(corners)
    return random_corner


def initialize_isolated_area(
        grid,
        isolated_shape,
        isolated_area_width,
        isolated_area_length,
        environment_data,
        isolated_area_tassels,
        radius,
        dimension_tassel,
        resources,
        counter,
):
    """
    Initialize the isolated area on the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        isolated_shape (str): The shape of the isolated area.
        isolated_area_width (int): Width of the isolated area.
        isolated_area_length (int): Length of the isolated area.
        environment_data (dict): Data related to the environment.
        isolated_area_tassels (list): List of tassels in the isolated area.
        radius (int): Radius of the area.
        dimension_tassel (float): Dimension of the tassel.
        resources (list): List of resources on the grid.
        counter (iterator): Iterator for counting.
    """
    randint = random.randint(0, 256)
    random_corner = choose_random_corner(environment_data)
    x_start, y_start = random_corner

    handle_isolated_area(
        grid=grid,
        shape=isolated_shape,
        randint=randint,
        x_start=x_start,
        y_start=y_start,
        isolated_area_width=isolated_area_width,
        isolated_area_length=isolated_area_length,
        isolated_area_tassels=isolated_area_tassels,
        radius=radius,
        dimension_tassel=dimension_tassel,
        resources=resources,
        counter=counter,
    )


def fill_circular_area(
        grid,
        radius,
        x_start,
        y_start,
        dimension_tassel,
        counter,
        resources,
        isolated_area_tassels,
):
    """
    Fill the circular area on the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        radius (int): Radius of the circular area.
        x_start (int): X-coordinate to start.
        y_start (int): Y-coordinate to start.
        dimension_tassel (float): Dimension of the tassel.
        counter (iterator): Iterator for counting.
        resources (list): List of resources on the grid.
        isolated_area_tassels (list): List of tassels in the isolated area.
    """
    sqr_count = int((math.pi * radius * radius) / (dimension_tassel ** 2))
    angle_delta = math.pi * 2 / sqr_count
    for idx in range(sqr_count):
        ang = angle_delta * idx
        sx = round(x_start + radius * math.cos(ang))
        sy = round(y_start + radius * math.sin(ang))
        ox = round(sx + math.cos(ang + angle_delta) * dimension_tassel * 0.5)
        oy = round(sy + math.sin(ang + angle_delta) * dimension_tassel * 0.5)
        cx = round((ox + sx) / 2)
        cy = round((oy + sy) / 2)
        dist = euclidean_distance((cx, cy), (sx, sy))
        assert dist < dimension_tassel * 0.5, f"Distance {dist} exceeded allowed limit."
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i ** 2 + j ** 2 <= radius ** 2:
                    p = (cx + i, cx + j)
                    if can_place(grid, p):
                        add_resource(
                            grid,
                            CircularIsolation(
                                next(counter),
                                p,
                                radius,
                                (2 * math.pi * radius),
                            ),
                            cx + i,
                            cx + j,
                        )
                        resources.append((cx + i, cy + j))
                        isolated_area_tassels.append((cx + i, cy + j))


def fill_circular_blocked_area(self, start_x: int, start_y: int, radius: int):
    """
    Fill the isolated circular area on the grid.

    Args:
        self: The simulator instance.
        start_x (int): The x-coordinate of the center of the circular area.
        start_y (int): The y-coordinate of the center of the circular area.
        radius (int): The radius of the circular area.
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
                center.x + math.cos(angle + angle_delta) * self.dimension_tassel * 0.5
            ),
            round(
                center.y + math.sin(angle + angle_delta) * self.dimension_tassel * 0.5
            ),
        )

        midpoint = Point(
            round((next_center.x + center.x) // 2),
            round((next_center.y + center.y) // 2),
        )

        distance = euclidean_distance((midpoint.x, midpoint.y), (center.x, center.y))
        assert (
                distance < self.dimension_tassel * 0.5
        ), f"Distance {distance} exceeded allowed limit."

        for i in range(-radius, (radius + 1)):
            for j in range(-radius, (radius + 1)):
                if i ** 2 + j ** 2 <= radius ** 2:
                    point = Point(midpoint.x + i, midpoint.y + j)
                    if self.can_blocked_place(point):
                        new_resource = CircledBlockedArea(
                            point, radius, random.randint(0, 256)
                        )
                        self.add_resource(new_resource, point.x, point.y)
                        self.resources.append(point)
                        self.isolated_area_tassels.append(point)


def can_place(grid, pos):
    """
    Check if a resource can be placed at a given position on the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        pos (tuple): Position to check.

    Returns:
        bool: True if a resource can be placed, False otherwise.
    """
    return grid.is_cell_empty((pos[0], pos[1])) and within_bounds(grid, pos)


def can_blocked_place(grid, pos):
    """
    Check if a resource can be placed at a given position on the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        pos (tuple): Position to check.

    Returns:
        bool: True if a resource can be placed, False otherwise.
    """
    return within_bounds(grid, pos) and grid.is_cell_empty((pos[0], pos[1]))


def within_bounds(grid, pos):
    """
    Check if a position is within the bounds of the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        pos (tuple): Position to check.

    Returns:
        bool: True if the position is within bounds, False otherwise.
    """
    x, y = pos
    return 0 <= x < grid.width and 0 <= y < grid.height


def find_largest_blocked_area(grid):
    """
    Find the largest blocked area among all blocked areas on the grid.

    Args:
        grid (mesa.space.Grid): The grid space.

    Returns:
        tuple or None: A tuple containing the largest blocked area agent and its coordinates,
                       or None if no blocked areas are present.
    """
    largest_blocked_area = None
    largest_area = 0
    largest_coords = None
    for cell_content, x, y in grid.coord_iter():
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


def add_resource(grid, resource, x, y):
    """
    Add a resource to the grid.

    Args:
        grid (mesa.space.Grid): The grid space.
        resource (Agent): The resource to add.
        x (int): X-coordinate of the position.
        y (int): Y-coordinate of the position.
    """
    if grid.is_cell_empty((x, y)):
        grid.place_agent(resource, (x, y))


def populate_blocked_areas(
        resources,
        num_squares,
        num_circles,
        grid,
        environment_data,
        min_width_blocked,
        max_width_blocked,
        min_height_blocked,
        max_height_blocked,
):
    """
    Populate blocked areas on the grid.

    Args:
        resources (list): List of resources on the grid.
        num_squares (int): Number of square blocked areas to populate.
        num_circles (int): Number of circular blocked areas to populate.
        grid (mesa.space.Grid): The grid space.
        environment_data (dict): Data related to the environment.
        min_width_blocked (int): Minimum width of a square blocked area.
        max_width_blocked (int): Maximum width of a square blocked area.
        min_height_blocked (int): Minimum height of a square blocked area.
        max_height_blocked (int): Maximum height of a square blocked area.
    """
    # Add blocked squares
    for _ in range(num_squares):
        (x, y) = generate_valid_agent_position(grid)
        square = SquaredBlockedArea(
            (x, y),
            random.randint(min_width_blocked, max_width_blocked),  # noqa: E231
            random.randint(min_height_blocked, max_height_blocked),
            random.randint(0, 256),
        )
        add_resource(grid, square, x, y)
        resources.append((x, y))

    # Add blocked circles
    for _ in range(num_circles):
        (x, y) = generate_valid_agent_position(grid)
        circle = CircledBlockedArea(
            (x, y), random.randint(1, 10), random.randint(0, 256)
        )
        add_resource(grid, circle, x, y)
        resources.append((x, y))


def euclidean_distance(p1, p2):
    """
    Calculate the Euclidean distance between two points.

    Args:
        p1 (tuple): Coordinates of point 1.
        p2 (tuple): Coordinates of point 2.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
