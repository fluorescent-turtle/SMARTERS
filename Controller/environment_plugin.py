import math
import random

from Model.agents import (
    SquaredBlockedArea,
    CircledBlockedArea,
    CircularIsolation,
    IsolatedArea,
    Opening,
)


def within_bounds(grid, pos):
    x, y = pos
    return 0 <= x < grid.width and 0 <= y < grid.height


def can_blocked_place(grid, pos):
    return within_bounds(grid, pos) and grid.is_cell_empty((pos[0], pos[1]))


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


def fill_circular_blocked_area(
        start_x,
        start_y,
        radius,
        dim_tassel,
        grid,
        resources,
):
    """
    Create a series of overlapping circles, blocking off sections of the grid to form a circular barrier around the starting point.

    Fills a circular area with blocked spaces, creating a polygon formed by connecting the centers of the created blocks.

    Args:
        start_x (int): Starting horizontal position for the circular barrier.
        start_y (int): Starting vertical position for the circular barrier.
        radius : Radius of the circular barrier.
        dim_tassel (int): Diameter of each filled section forming the barrier.
        grid (Grid): A Grid object storing agents.
        resources (list): List of resources managed by the environment.
    """
    squared_circle_count = int((math.pi * radius * radius) / (dim_tassel ** 2))
    angle_delta = math.pi * 2 / squared_circle_count

    for idx in range(squared_circle_count):
        angle = angle_delta * idx
        center = (
            round(start_x + radius * math.cos(angle)),
            round(start_y + radius * math.sin(angle)),
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

        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i ** 2 + j ** 2 <= radius ** 2:
                    point = (midpoint[0] + i, midpoint[1] + j)
                    if can_blocked_place(grid, point):
                        new_resource = CircledBlockedArea(point, radius)
                        print("BLOCKED CIRCLE: ", point)
                        add_resource(grid, new_resource, point[0], point[1])
                        resources.append(point)


def build_squared_isolated_area(
        x_start,
        y_start,
        isolated_area_width,
        isolated_area_length,
        grid,
        isolated_area_tassels,
        resources,
        dim_opening,
        dim_tassel,
):
    enclosure_tassels = []

    def create_resources(x_range, y_range):
        for x in x_range:
            for y in y_range:
                new_resource = IsolatedArea((x, y))
                add_resource(grid, new_resource, x, y)
                resources.append(new_resource)
                isolated_area_tassels.append((x, y))

                print("ISOLATED TASSEL: ", (x, y))
                print(
                    "X ---- XSTART ----- Y----YSTART ------- XSTART+ISWIDTH ------------ YSTART+IS_LENGTH ",
                    x,
                    x_start,
                    y,
                    y_start,
                    (x_start + isolated_area_width - 1),
                    (y_start + isolated_area_length - 1),
                )

                if (
                        (x == x_start or x == x_start + isolated_area_width - 1)
                        and y_start
                        <= y
                        < y_start
                        + isolated_area_length
                        - 1  # todo: se ho i casi (n,n) non funziona
                ) or (
                        (y == y_start or y == y_start + isolated_area_length - 1)
                        and x_start <= x < x_start + isolated_area_width - 1
                ):
                    enclosure_tassels.append((x, y))

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

    print("ENCLOSURE TASSELS: ", enclosure_tassels)

    removal_points = [
        (0, 0),
        (0, y_start),
        (x_start, 0),
        (x_start, y_start),
    ]
    for point in removal_points:
        if point in enclosure_tassels:
            enclosure_tassels.remove(point)

    print("PRIMA DEL RETURN: ", enclosure_tassels)
    if not enclosure_tassels:
        return

    opening = random.choice(enclosure_tassels)
    print("OPENING: ", opening)

    opening_x, opening_y = opening
    index_opening = enclosure_tassels.index(opening)

    while dim_opening > 0:
        opening_new = Opening(opening)

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


def is_within_bounds(x, y, width, height):
    """
    Check if the given coordinates (x, y) are within the specified bounds.

    This function takes in an x-coordinate, a y-coordinate, as well as a width and
    height representing the size of a rectangular area. It returns True if the point
    (x, y) lies inside or on the boundary of the rectangle, and False otherwise.

    Args:
        x (int): The x-coordinate to check for being within bounds.
        y (int): The y-coordinate to check for being within bounds.
        width (int): The width of the bounding box. Must be greater than zero.
        height (int): The height of the bounding box. Must be greater than zero.

    Returns:
        bool: A boolean indicating whether the point (x, y) is within the bounds of
            the rectangle defined by the width and height parameters. Specifically,
            this will be True if both of the following conditions hold:
                0 <= x < width
                AND
                0 <= y < height

            Otherwise, it will return False.
    """
    # Ensure that the dimensions provided are positive
    assert width > 0, "Invalid width value"
    assert height > 0, "Invalid height value"

    # Return True if both conditions are met, else False
    return 0 <= x < width and 0 <= y < height


def contains_resource(grid, cell, resource):
    cell_contents = grid.get_cell_list_contents((cell[0], cell[1]))

    specific_agent = next(
        (agent for agent in cell_contents if isinstance(agent, resource)), None
    )

    if specific_agent:
        return True
    else:
        return False


def get_circular_neighbors(cell, width, height, dim_tassel):
    """
    Return all valid neighbors of a specific cell considering circular boundary conditions.
    Neighbors are defined as points at most one 'dim_tassel' away along each axis.

    :param tuple[int, int] cell: Current cell coordinate (x, y)
    :param int width: Grid width
    :param int height: Grid height
    :param int dim_tassel: Dimension of tassels
    :return set[tuple[int, int]]: Set of valid neighbor coordinates
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
    enclosure_tassels = []
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if i ** 2 + j ** 2 <= radius ** 2:
                p = (x_start + i, y_start + j)
                if within_bounds(grid, p) and can_blocked_place(grid, p):
                    isolated_area_tassels.append(p)
                    add_resource(grid, CircularIsolation(p, radius), p[0], p[1])
                    resources.append(p)

                    # Check for perimeter tassels
                    if any(
                            nb in enclosure_tassels
                            for nb in get_circular_neighbors(p, *grid.shape)
                    ):
                        enclosure_tassels.append(p)

    if enclosure_tassels:
        opening = random.choice(enclosure_tassels)
        index_opening = enclosure_tassels.index(opening)

        while dim_opening > 0:
            new_resource = Opening(
                opening
            )  # Assuming Opening is a class for grid openings
            add_resource(
                grid, new_resource, opening[0], opening[1]
            )  # Add opening to the grid
            resources.append(new_resource)  # Append the opening to resources list
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
            resources,
            random.randint(0, isolated_width) * dim_tassel % grid_width,
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

    Comments:
    This function first generates random dimensions for the blocked area within the specified limits.
    It then calculates the number of possible squared blocks that can fit into this blocked area by dividing it
    by the size of each square block and rounding down to the nearest integer using the `math.floor()` method.
    Next, the function loops through these calculated dimensions and checks whether the potential location of
    each square block is valid (i.e., lies within the bounds of the grid and has not already been occupied).
    If the conditions are met, a new instance of the `SquaredBlockedArea` class is created at the current position,
    printed out, and added to both the grid and the `resources` list.
    """

    # Set local variables equal to input arguments
    x = coord_x
    y = coord_y

    # Generate random width and height values for the blocked area
    columns = random.randint(min_width_blocked, max_width_blocked)
    rows = random.randint(min_height_blocked, max_height_blocked)

    num_columns = math.floor((columns - dim_tassel) / dim_tassel)
    num_rows = math.floor((rows - dim_tassel) / dim_tassel)

    for j in range(num_rows):
        for i in range(num_columns):

            tassel_x = math.floor(x + i * dim_tassel)
            tassel_y = math.floor(y + j * dim_tassel)

            if 0 <= tassel_x < grid.width and 0 <= tassel_y < grid.height:
                if (tassel_x, tassel_y) not in resources:
                    square = SquaredBlockedArea((tassel_x, tassel_y))
                    print("BLOCKED SQUARE: ", (tassel_x, tassel_y))
                    add_resource(grid, square, tassel_x, tassel_y)
                    resources.append((tassel_x, tassel_y))


def populate_blocked_areas(
        resources,
        num_squares,
        num_circles,
        grid,
        min_width_blocked,
        max_width_blocked,
        min_height_blocked,
        max_height_blocked,
        radius,
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
        radius (int): Radius of circular blocked areas.
        dim_tassel (int): Dimension of tassels.

    No explicit return statement since values get modified directly through passed arguments.
    """

    # Loop 'num_squares' times
    for _ in range(num_squares):
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
        )

    # Loop 'num_circles' times
    for _ in range(num_circles):
        # Get valid agent positions
        (x, y) = generate_valid_agent_position(grid)
        # Fill circular blocked area at the obtained position
        fill_circular_blocked_area(x, y, radius, dim_tassel, grid, resources)


class DefaultRandomGrid:
    """
    Generate a default random grid according to user input parameters.

    This class generates a random grid based on various inputs such as the desired
    dimension sizes, shapes, obstacles, etc. Once instantiated, you can call its `begin` method
    which initializes the internal state of the object and produces the final grid layout.

    Attributes:
        _width (int): The width of the generated grid.
        _length (int): The length of the generated grid.
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
        _grid (List[List[Any]]): Final grid representation after generation.

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
            resources,
            grid,
            isolated_width,
            isolated_length,
    ):
        """
        Initialize attributes needed to create a new instance of the DefaultRandomGrid class.

        Args:
            width (int): Grid width.
            length (int): Grid length.
            isolated_shape (tuple[int, int]): Shape of isolated region.
            min_height_blocked (int): Minimum height of blocked regions.
            max_height_blocked (int): Maximum height of blocked regions.
            min_width_blocked (int): Minimum width of blocked regions.
            max_width_blocked (int): Maximum width of blocked regions.
            radius (int): Radius used when generating circular blockages.
            dim_tassel (float): Size of each individual tassel.
            isolated_area_tassels (list[Tuple[int, int]]): Tuple list of cell indices.
            num_blocked_squares (int): Number of squared blockages.
            num_blocked_circles (int): Number of circular blockages.
            resources (list): Additional resources dictionary.
            grid (List[List[Any]]): Empty grid structure.
        """
        super().__init__()

        self._width = width
        self._length = length
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
        self._grid = grid
        self._isolated_width = isolated_width
        self._isolated_length = isolated_length

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
            self._radius,
            self._dim_tassel,
        )

        return self._grid, self._resources, random_corner
