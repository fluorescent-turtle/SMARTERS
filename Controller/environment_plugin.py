import math
import random

from scipy.spatial import KDTree

from Controller.default_grid import RandomGrid
from Model.agents import (
    SquaredBlockedArea,
    CircledBlockedArea,
    CircularIsolation,
    IsolatedArea,
    Opening,
)
from Utils.utils import set_guideline_cell, draw_line, contains_resource, within_bounds


def can_place_blocked(grid, pos):
    """
    Check if a blocked area can be placed at the specified position on the grid.

    Args:
        grid (Grid): The grid.
        pos (tuple): Position to check (x, y).

    Returns:
        bool: True if the position is within grid bounds and empty, False otherwise.
    """
    return within_bounds(grid, (pos[0], pos[1])) and grid.is_cell_empty(pos)


def add_resource(grid, resource, x, y):
    """
    Place a resource onto the grid at the specified position if the space is within bounds and currently vacant.

    Args:
        grid (Grid): A Grid object storing agents.
        resource (AgentResource): AgentResource subclass defining a type of agent.
        x (int): Horizontal position for placing the resource.
        y (int): Vertical position for placing the resource.
    """
    if within_bounds(grid, (x, y)) and grid.is_cell_empty((x, y)):
        grid.place_agent(resource, (x, y))


def build_squared_isolated_area(
        x_start,
        y_start,
        isolated_area_width,
        isolated_area_length,
        grid,
        isolated_area_tassels,
        dim_opening,
        dim_tassel,
):
    """
    Build a squared isolated area on the grid.

    Args:
        x_start (int): Starting x-coordinate of the isolated area.
        y_start (int): Starting y-coordinate of the isolated area.
        isolated_area_width (int): Width of the isolated area.
        isolated_area_length (int): Length of the isolated area.
        grid (Grid): The grid to build the isolated area on.
        isolated_area_tassels (list): List to store isolated area tassels.
        dim_opening : Dimension of the opening.
        dim_tassel: Dimension of tassels.
    """
    enclosure_tassels = []

    def create_resources(x_range, y_range):
        """Create resources within specified ranges."""
        for x in x_range:
            for y in y_range:
                new_resource = IsolatedArea((x, y))
                add_resource(grid, new_resource, x, y)
                isolated_area_tassels.append((x, y))

                if (
                        (x == x_start or x == x_start + isolated_area_width - 1)
                        and y_start <= y < y_start + isolated_area_length
                ) or (
                        (y == y_start or y == y_start + isolated_area_length - 1)
                        and x_start <= x < x_start + isolated_area_width
                ):
                    enclosure_tassels.append((x, y))
                    print("isolated area: ", (x, y))
                else:

                    if (
                            (x == x_start or x == x_start - isolated_area_width + 1)
                            and y >= y_start - isolated_area_length + 1
                    ) or (
                            (y == y_start or y == y_start - isolated_area_length + 1)
                            and x >= x_start - isolated_area_width + 1
                    ):
                        enclosure_tassels.append((x, y))
                        print("isolated area: ", (x, y))

    if x_start == 0:
        if y_start == 0:
            # Both x_start and y_start are zero
            create_resources(
                range(x_start, x_start + isolated_area_width),
                range(y_start, y_start + isolated_area_length),
            )
        else:
            # x_start is zero but y_start is not zero
            create_resources(
                range(x_start, x_start + isolated_area_width),
                range(y_start, y_start - isolated_area_length, -1),
            )
    elif y_start == 0:
        # x_start is not zero
        create_resources(
            range(x_start, x_start - isolated_area_width, -1),
            range(y_start, y_start + isolated_area_length),
        )
    else:
        create_resources(
            range(x_start, x_start - isolated_area_width, -1),
            range(y_start, y_start - isolated_area_length, -1),
        )

    if len(enclosure_tassels) > 1:
        removal_points = [
            (0, 0),
            (0, y_start),
            (x_start, 0),
            (x_start, y_start),
        ]
        for point in removal_points:
            if point in enclosure_tassels:
                enclosure_tassels.remove(point)

    if not enclosure_tassels:
        return

    opening = random.choice(enclosure_tassels)

    opening_x, opening_y = opening
    index_opening = enclosure_tassels.index(opening)

    while dim_opening > 0:
        opening_new = Opening(opening)
        print("OPENING: ", (opening_x, opening_y))
        add_resource(grid, opening_new, opening_x, opening_y)

        dim_opening -= dim_tassel  # Decrease the opening dimension

        next_index = index_opening + 1
        if next_index >= len(enclosure_tassels) or next_index < 0:
            # Handle wrapping around or staying at the same index
            potential_indices = [
                index % len(enclosure_tassels)
                for index in (index_opening, index_opening - 1, index_opening + 1)
            ]
            opening_indices = random.choice(potential_indices)
        else:
            opening_indices = next_index
        opening = random.choice(
            [
                enclosure_tassels[opening_indices][0],
                enclosure_tassels[opening_indices][1],
            ]
        )


def get_circular_neighbors(cell, width, height, dim_tassel):
    """
    Return all valid neighbors of a specific cell considering circular boundary conditions.
    Neighbors are defined as points at most one 'dim_tassel' away along each axis.

    Args:
        cell (tuple[int, int]): Current cell coordinate (x, y)
        width (int): Grid width
        height (int): Grid height
        dim_tassel (int): Dimension of tassels

    Returns:
        set[tuple[int, int]]: Set of valid neighbor coordinates
    """

    # Helper function to validate a single coordinate value
    def _valid_coordinate(h, max_val):
        """Check if a coordinate value is inside grid bounds"""
        return -1 < h < max_val

    neighbors = set()  # Initialize empty set to store unique neighbor coordinates
    x, y = cell

    # Loop through possible relative offsets (-1, 0, 1) along both axes
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx * dim_tassel, y + dy * dim_tassel

            # Check if the potential neighbor is within grid boundaries and has no common tassel
            if (_valid_coordinate(nx, width) and _valid_coordinate(ny, height)) and (
                    (abs(dx) + abs(dy)) == 1
            ):
                neighbors.add((nx, ny))

    return neighbors


def circular_isolation(
        grid,
        radius,
        x_start,
        y_start,
        dim_tassel,
        resources,
        isolated_area_tassels,
        dim_opening,
):
    """
    Create a circular isolated area within the grid.

    Args:
        grid: The grid to create the isolated area on.
        radius (int): The radius of the circular isolated area.
        x_start (int): The x-coordinate of the starting point for the isolation.
        y_start (int): The y-coordinate of the starting point for the isolation.
        dim_tassel (float): The dimension of each tassel.
        resources (list): List of resources.
        isolated_area_tassels (list): List of tassels in the isolated area.
        dim_opening (float): The dimension of the opening in the isolated area.

    Returns:
        None
    """
    enclosure_tassels = []
    for i in range(-radius, radius + 1):  # Iterate over the possible x-coordinates
        for j in range(-radius, radius + 1):  # Iterate over the possible y-coordinates
            if i ** 2 + j ** 2 <= radius ** 2:  # Check if within the circular area
                p = (x_start + i, y_start + j)  # Calculate the position
                if within_bounds(grid, p) and can_place_blocked(
                        grid, p
                ):  # Check if the position is within bounds and can be blocked
                    isolated_area_tassels.append(
                        p
                    )  # Add the position to the isolated area
                    add_resource(
                        grid, CircularIsolation(p, radius), p[0], p[1]
                    )  # Add CircularIsolation resource to the grid
                    print("CIRCULAR ISOLATION: ", (p[0], p[1]))

                    # Check for perimeter tassels
                    if any(
                            nb in enclosure_tassels
                            for nb in get_circular_neighbors(p, *grid.shape)
                    ):  # Check if the position is a perimeter tassel
                        enclosure_tassels.append(
                            p
                        )  # Add the position to the perimeter tassels

    if enclosure_tassels:  # If there are perimeter tassels
        current_opening = random.choice(
            enclosure_tassels
        )  # Choose a random perimeter tassel as the current opening
        index_current_opening = enclosure_tassels.index(
            current_opening
        )  # Get the index of the current opening

        while dim_opening > 0:  # While the opening dimension is greater than 0
            next_openings = [
                (i % len(enclosure_tassels))
                for i in (
                    index_current_opening,
                    index_current_opening - 1,
                    index_current_opening + 1,
                )
            ]  # Calculate indices for potential next openings
            index_next_opening = random.choice(
                next_openings
            )  # Choose a random index for the next opening
            current_opening = enclosure_tassels[
                index_next_opening
            ]  # Get the coordinates of the next opening

            new_resource = Opening(current_opening)  # Create a new Opening resource
            add_resource(
                grid, new_resource, *current_opening[:2]
            )  # Add the opening to the grid
            resources.append(
                (current_opening[0], current_opening[1])
            )  # Add the opening to the resources list
            dim_opening -= dim_tassel  # Decrease the opening dimension


def initialize_isolated_area(
        grid,
        isolated_shape,
        isolated_length,
        isolated_width,
        grid_width,
        grid_length,
        isolated_area_tassels,
        radius,
        dim_tassel,
        resources,
):
    """
    Initialize an isolated area within the grid.

    Args:
        grid (list): The grid to initialize the isolated area on.
        isolated_shape (str): The shape of the isolated area ("Square" or "Circle").
        isolated_length (int): The length of the isolated area.
        isolated_width (int): The width of the isolated area.
        grid_width (int): The width of the grid.
        grid_length (int): The length of the grid.
        isolated_area_tassels (list): List of tassels in the isolated area.
        radius (int): The radius of the circular isolated area.
        dim_tassel (float): The dimension of each tassel.
        resources (list): Dictionary containing resources.

    Returns:
        tuple: Randomly chosen corner coordinates of the isolated area.
    """
    random_corner = choose_random_corner(grid_width, grid_length)

    x_corner, y_corner = random_corner

    if isolated_shape == "Square":
        build_squared_isolated_area(
            x_corner,
            y_corner,
            isolated_length,
            isolated_width,
            grid,
            isolated_area_tassels,
            random.randint(1, isolated_width) * dim_tassel % grid_width,
            dim_tassel,
        )
    else:
        circular_isolation(
            grid,
            radius,
            x_corner,
            y_corner,
            dim_tassel,
            resources,
            isolated_area_tassels,
            random.randint(0, 10) * dim_tassel,
        )
    return random_corner


def choose_random_corner(width, height):
    """
    Choose a random corner among the four available corners of a grid.

    Args:
        width (int): The width of the grid.
        height (int): The height of the grid.

    Returns:
        tuple(int, int): A tuple of two integers representing the selected random corner's x and y coordinates.
    """
    # Define potential corners
    corners = [(0, 0), (0, height - 1), (width - 1, 0), (width - 1, height - 1)]

    # Randomly pick one corner
    return random.choice(corners)


def generate_valid_agent_position(grid):
    """
    Find and return a random, unoccupied position within the given grid.

    Args:
        grid (Grid): An instance of the Grid class representing the board.

    Returns:
        tuple(int, int): A pair of integer coordinates representing a random, unoccupied cell within the grid.
    """
    while True:
        x = random.randrange(grid.width)  # Select a random X coordinate.
        y = random.randrange(grid.height)  # Select a random Y coordinate.

        if grid.is_cell_empty((x, y)):  # If cell is empty...
            return x, y  # ...return these coordinates.


def calculate_variance(value1, value2):
    """
    Calculate the variance between two values.

    Args:
        value1 (float): The first value.
        value2 (float): The second value.

    Returns:
        float: The calculated variance.
    """
    # Calculate the mean of the two values
    mean = (value1 + value2) / 2
    # Calculate the square of the differences and sum them
    sum_of_squares = (value1 - mean) ** 2 + (value2 - mean) ** 2
    # Calculate the variance
    variance = sum_of_squares / 2
    return variance


def neighbor_on_the_perimeter(neighbours, perimeter_cells):
    for neighbor in neighbours:
        if neighbor in perimeter_cells:
            return True

    return False


def find_perimeter_cells(width: int, height: int):
    """
    Find all cells on the perimeter of the grid.

    :param width: Grid width.
    :param height: Grid height.
    :return: A list of tuples representing perimeter cell coordinates.
    """
    return [
        (x, y)
        for x in range(width)
        for y in range(height)
        if x == 0 or y == 0 or x == width - 1 or y == height - 1
    ]


def find_and_draw_lines(grid, blocked_tassels, neighbors, resources, dim_tassel):
    """
    Find and draw lines from perimeter guideline cells to their closest valid neighbors.

    This function first filters valid neighbors based on certain conditions and
    then finds the closest valid neighbor for each perimeter guidelines cell.
    If there exists a path between the two cells, a line will be drawn connecting them.

    :param grid: Instance of Grid class containing information about the current state of the grid.
    :type grid: Grid
    :param blocked_tassels: A list of blocked tassels represented by their cell coordinates.
    :type blocked_tassels: List[Tuple[int, int]]
    :param neighbors: A list of potential neighboring cells around the perimeter guidelines cells.
    :type neighbors: List[Tuple[int, int]]
    :param resources: An object containing details about various types of resources present in the grid.
    :type resources: Object
    :param dim_tassel: Diameter of a tassel.
    :type dim_tassel: Int
    """

    perimeter_guidelines = find_perimeter_cells(grid.width, grid.height)

    valid_neighbors = [
        neighbor
        for neighbor in neighbors
        if neighbor not in blocked_tassels
           and not contains_resource(grid, (neighbor[0], neighbor[1]), IsolatedArea)
           and not contains_resource(grid, (neighbor[0], neighbor[1]), CircularIsolation)
           and not is_near_opening(grid, neighbor)
    ]

    if valid_neighbors and not neighbor_on_the_perimeter(
            neighbors, perimeter_guidelines
    ):
        tree = KDTree(valid_neighbors)
        closest_neighbor = None
        nearest_perimeter = None
        min_distance = float("inf")

        for pg_cell in perimeter_guidelines:
            distance, index = tree.query(pg_cell)
            distance = math.ceil(distance * dim_tassel)
            if distance < min_distance:
                closest_neighbor = valid_neighbors[index]
                min_distance = distance
                nearest_perimeter = pg_cell

        if closest_neighbor:
            draw_line(
                closest_neighbor[0],
                closest_neighbor[1],
                nearest_perimeter[0],
                nearest_perimeter[1],
                grid,
                resources,
            )


def fill_circular_blocked_area(
        start_x, start_y, radius, dim_tassel, grid, resources, identifier
):
    """
    Create a series of overlapping circles, blocking off sections of the grid to form
    a circular barrier around the starting point.

    Fills a circular area with blocked spaces,
    creating a polygon formed by connecting the centers of the created blocks.

    Args:
        start_x (int): Starting horizontal position for the circular barrier.
        start_y (int): Starting vertical position for the circular barrier.
        radius : Radius of the circular barrier.
        dim_tassel (int): Diameter of each filled section forming the barrier.
        grid (Grid): A Grid object storing agents.
        resources (list): List of resources managed by the environment.
        identifier (int): Blocked area identifier
    """
    rad = math.ceil(calculate_variance(0, radius))
    squared_circle_count = int((math.pi * rad * rad) / (dim_tassel ** 2))
    angle_delta = math.pi * 2 / squared_circle_count

    blocked_tassels = []

    for idx in range(squared_circle_count):
        angle = angle_delta * idx
        center = (
            round(start_x + rad * math.cos(angle)),
            round(start_y + rad * math.sin(angle)),
        )
        next_center = (
            round(center[0] + math.cos(angle + angle_delta) * dim_tassel * 0.5),
            round(center[1] + math.sin(angle + angle_delta) * dim_tassel * 0.5),
        )
        midpoint = (
            round((next_center[0] + center[0]) / 2),
            round((next_center[1] + center[1]) / 2),
        )

        dist = math.sqrt(
            (midpoint[0] - center[0]) ** 2 + (midpoint[1] - center[1]) ** 2
        )
        assert dist < dim_tassel * 0.5, f"Distance {dist} exceeded allowed limit."

        for i in range(-rad, rad + 1):
            for j in range(-rad, rad + 1):
                if i ** 2 + j ** 2 <= rad ** 2:
                    point = (midpoint[0] + i, midpoint[1] + j)
                    if can_place_blocked(grid, point) and not is_near_opening(
                            grid, point
                    ):
                        new_resource = CircledBlockedArea(point, rad, identifier)
                        add_resource(grid, new_resource, point[0], point[1])
                        resources.append((point[0], point[1]))
                        blocked_tassels.append((point[0], point[1]))
                        print("CIRCLED BLOCKED: ", (point[0], point[1]))

    neighbors = []
    for tassel in blocked_tassels:
        for nb in grid.get_neighborhood(tassel, moore=True, include_center=False):
            if nb not in blocked_tassels and not is_near_opening(grid, tassel):
                neighbors.append((math.floor(nb[0]), math.floor(nb[1])))
                print("NEIGHBOURS CIRCLED: ", (math.floor(nb[0]), math.floor(nb[1])))

    for neighbor in neighbors:
        set_guideline_cell(
            math.floor(neighbor[0]), math.floor(neighbor[1]), grid, resources
        )

    find_and_draw_lines(
        grid, blocked_tassels, neighbors, resources, math.ceil(dim_tassel)
    )


def add_squared_area(
        coord_x,
        coord_y,
        min_width_blocked,
        max_height_blocked,
        max_width_blocked,
        min_height_blocked,
        dim_tassel,
        resources,
        grid,
        identifier,
):
    """
    Adds squared blocked areas to the grid based on input parameters.

    Parameters:
    coord_x (int): The starting X coordinate of the area to be checked for adding squares.
    coord_y (int): The starting Y coordinate of the area to be checked for adding squares.
    min_width_blocked (int): The minimum width of the blocked area.
    max_height_blocked (int): The maximum height of the blocked area.
    max_width_blocked (int): The maximum width of the blocked area.
    min_height_blocked (int): The minimum height of the blocked area.
    dim_tassel (int): The dimension of each individual square block that will be added to the blocked area.
    resources (list): A list containing all the currently occupied resource locations as tuples.
    grid (object): An object representing the game grid with attributes 'width' and 'height'.

    Returns:
    None
    """
    x = coord_x
    y = coord_y

    columns = calculate_variance(min_width_blocked, max_width_blocked)
    rows = calculate_variance(min_height_blocked, max_height_blocked)
    num_columns = math.ceil(columns + min_width_blocked)
    num_rows = math.ceil(rows + min_height_blocked)

    blocked_area = []

    for j in range(num_rows):
        for i in range(num_columns):
            tassel_x = math.floor(x + i * dim_tassel)
            tassel_y = math.floor(y + j * dim_tassel)

            if 0 <= tassel_x < grid.width and 0 <= tassel_y < grid.height:
                if (
                        not is_near_opening(grid, (tassel_x, tassel_y))
                        and (tassel_x, tassel_y) not in resources
                ):
                    square = SquaredBlockedArea((tassel_x, tassel_y), identifier)
                    add_resource(grid, square, tassel_x, tassel_y)
                    resources.append((tassel_x, tassel_y))
                    blocked_area.append((tassel_x, tassel_y))
                    print("SQUARED BLOCKED: ", (tassel_x, tassel_y))

    neighbors = []
    for cell in blocked_area:
        for move in grid.get_neighborhood(cell, moore=True, include_center=False):
            if move not in blocked_area and not is_near_opening(grid, move):
                neighbors.append(move)
                print("NEIGHBORS::: ", neighbors)

    for neighbor in neighbors:
        set_guideline_cell(
            math.floor(neighbor[0]), math.floor(neighbor[1]), grid, resources
        )
        print("SQUARED NEIGHBOR: ", (neighbor[0]), math.floor(neighbor[1]))

    find_and_draw_lines(grid, blocked_area, neighbors, resources, math.ceil(dim_tassel))


def is_near_opening(grid, point):
    """
    Checks if the given point is near an 'Opening' object.

    Args:
        grid (Grid): The grid.
        point (tuple): The (x, y) coordinates of the point.

    Returns:
        bool: True if the point is near an 'Opening', False otherwise.
    """
    x, y = point
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < grid.width and 0 <= neighbor[1] < grid.height:
                if contains_resource(grid, (neighbor[0], neighbor[1]), Opening):
                    return True
    return False


def populate_blocked_areas(
        resources,
        num_squares,
        num_circles,
        grid,
        min_width_blocked,
        max_width_blocked,
        min_height_blocked,
        max_height_blocked,
        ray,
        dim_tassel,
):
    """
    Populates the grid with blocked areas (both squared and circular).

    Function iterates over a number of squared and circular blocked areas while ensuring they do not overlap.
    Each iteration picks a valid location from the grid before filling either a squared or circular blocked area.

    Args:
        resources (list): Resources dictionary.
        num_squares (int): Number of squared blocked areas to generate.
        num_circles (int): Number of circular blocked areas to generate.
        grid (List[List[Any]]): Empty grid structure.
        min_width_blocked (int): Minimum width of squared blocked areas.
        max_width_blocked (int): Maximum width of squared blocked areas.
        min_height_blocked (int): Minimum height of squared blocked areas.
        max_height_blocked (int): Maximum height of squared blocked areas.
        ray: Radius of circular blocked areas.
        dim_tassel: Dimension of tassels.

    No explicit return statement since values get modified directly through passed arguments.
    """

    # Loop 'num_squares' times
    for i in range(num_squares):
        # Get valid agent positions
        (x, y) = generate_valid_agent_position(grid)
        # Add squared area at the obtained position
        add_squared_area(
            x,
            y,
            min_width_blocked,
            max_height_blocked,
            max_width_blocked,
            min_height_blocked,
            dim_tassel,
            resources,
            grid,
            i,
        )

    # Loop 'num_circles' times
    for j in range(num_circles):
        # Get valid agent positions
        (x, y) = generate_valid_agent_position(grid)
        # Fill circular blocked area at the obtained position
        fill_circular_blocked_area(
            x, y, ray, dim_tassel, grid, resources, j * dim_tassel
        )


class DefaultRandomGrid(RandomGrid):
    """
    Generate a default random grid according to user input parameters.

    This class generates a random grid based on various inputs such as the desired
    dimension sizes, shapes, obstacles, etc. Once instantiated, you can call its `begin` method
    which initializes the internal state of the object and produces the final grid layout.

    Attributes:
        _isolated_shape (tuple[int, int]): A tuple specifying the shape of the
            isolated region where tassels may spawn.
        _min_height_blocked (int): Minimum height of blocked regions.
        _max_height_blocked (int): Maximum height of blocked regions.
        _min_width_blocked (int): Minimum width of blocked regions.
        _max_width_blocked (int): Maximum width of blocked regions.
        _radius (int): Radius used when generating circular blockages.
        _dim_tassel (float): Size of each individual tassel.
        _isolated_area_tassels (list[Tuple[int, int]]): List containing tuples of
            2 elements - row index & column index, describing all the cells occupied
            by tassels.
        _num_blocked_squares (int): Number of square blockages to generate.
        _num_blocked_circles (int): Number of circle blockages to generate.
        _resources (dict[str, Any]): Dictionary holding any additional data required
            during generation process.

    Methods:
        begin(): Initializes the grid generation process and returns relevant details.
    """

    def __init__(
            self,
            width,
            length,
            isolated_shape,
            min_height_blocked,
            max_height_blocked,
            min_width_blocked,
            max_width_blocked,
            radius,
            dim_tassel,
            isolated_area_tassels,
            num_blocked_squares,
            num_blocked_circles,
            ray,
            resources,
            grid,
            isolated_width,
            isolated_length,
    ):
        super().__init__(width, length, grid)

        self._isolated_width = isolated_width
        self._isolated_length = isolated_length
        self._ray = ray
        self._isolated_shape = isolated_shape
        self._min_height_blocked = min_height_blocked
        self._max_height_blocked = max_height_blocked
        self._min_width_blocked = min_width_blocked
        self._max_width_blocked = max_width_blocked
        self._radius = radius
        self._dim_tassel = dim_tassel
        self._isolated_area_tassels = isolated_area_tassels
        self._num_blocked_squares = num_blocked_squares
        self._num_blocked_circles = num_blocked_circles
        self._resources = resources

    def begin(self):
        _isolated_area_tassels = []
        random_corner = initialize_isolated_area(
            self._grid,
            self._isolated_shape,
            self._isolated_length,
            self._isolated_width,
            self._width,
            self._length,
            self._isolated_area_tassels,
            self._radius,
            self._dim_tassel,
            self._resources,
        )

        populate_blocked_areas(
            self._resources,
            self._num_blocked_squares,
            self._num_blocked_circles,
            self._grid,
            self._min_width_blocked,
            self._max_width_blocked,
            self._min_height_blocked,
            self._max_height_blocked,
            self._ray,
            self._dim_tassel,
        )

        return self._grid, self._resources, random_corner
