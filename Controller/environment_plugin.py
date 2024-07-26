import math
import random

from mesa.space import MultiGrid
from scipy.spatial import KDTree
from Controller.default_grid import RandomGrid
from Model.agents import (
    SquaredBlockedArea,
    CircledBlockedArea,
    IsolatedArea,
    Opening,
    GuideLine,
    BaseStation,
)
from Utils.utils import (
    set_guideline_cell,
    draw_line,
    within_bounds,
    contains_any_resource,
    add_resource,
)


def build_squared_isolated_area(
        x_start,
        y_start,
        isolated_area_width,
        isolated_area_length,
        grid,
        dim_opening,
        grid_width,
        grid_height,
):
    enclosure_tassels = []

    def create_resources(x_range, y_range):
        """Create resources within specified ranges."""
        for x in x_range:
            for y in y_range:
                new_resource = IsolatedArea((x, y))
                res = add_resource(grid, new_resource, x, y, grid_width, grid_height)
                if res:
                    # isolated_area_tassels.append((x, y))
                    # print("isolated area: ", (x, y))

                    # Check if the tassel is on the boundary of the isolated area
                    if (
                        (x == x_start or x == x_start + isolated_area_width - 1)
                        and y_start <= y < y_start + isolated_area_length
                    ) or (
                        (y == y_start or y == y_start + isolated_area_length - 1)
                        and x_start <= x < x_start + isolated_area_width
                    ):
                        enclosure_tassels.append((x, y))
                    else:
                        if (
                            (x == x_start or x == x_start - isolated_area_width + 1)
                            and y >= y_start - isolated_area_length + 1
                        ) or (
                            (y == y_start or y == y_start - isolated_area_length + 1)
                            and x >= x_start - isolated_area_width + 1
                        ):
                            enclosure_tassels.append((x, y))

    if x_start == 0:
        if y_start == 0:
            create_resources(
                range(x_start, x_start + isolated_area_width),
                range(y_start, y_start + isolated_area_length),
            )
        else:
            create_resources(
                range(x_start, x_start + isolated_area_width),
                range(y_start - isolated_area_length, y_start),
            )
    elif y_start == 0:
        create_resources(
            range(x_start - isolated_area_width, x_start),
            range(y_start, y_start + isolated_area_length),
        )
    else:
        create_resources(
            range(x_start - isolated_area_width, x_start),
            range(y_start - isolated_area_length, y_start),
        )

    # Remove points in the corners from enclosure_tassels
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

    opening_index = enclosure_tassels.index(opening)
    aux_opening = []

    while dim_opening > 0:
        opening_new = Opening(opening)
        # print("OPENING: ", opening)
        aux_opening.append(opening)
        result = add_resource(
            grid, opening_new, opening_x, opening_y, grid_width, grid_height
        )

        if result:
            dim_opening -= 1

            opening_index = (opening_index + 1) % len(enclosure_tassels)
            opening = enclosure_tassels[opening_index]

    return random.choice(aux_opening)


def circular_isolation(
        grid,
        radius,
        x_start,
        y_start,
        dim_opening,
        grid_width,
        grid_height,
):
    """
    Create a circular isolated area with an opening.
    """
    enclosure_tassels = []
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if i ** 2 + j ** 2 <= radius ** 2:
                p = (x_start + i, y_start + j)
                if add_resource(grid, IsolatedArea(p), *p, grid_width, grid_height):
                    if any(
                            nb in enclosure_tassels
                            for nb in grid.get_neighborhood(p, grid_width, grid_height, 1)
                    ):
                        enclosure_tassels.append(p)

    if enclosure_tassels:
        current_opening = random.choice(enclosure_tassels)
        while dim_opening > 0:
            index_current_opening = enclosure_tassels.index(current_opening)
            next_openings = [
                (index_current_opening + i) % len(enclosure_tassels) for i in [-1, 0, 1]
            ]
            current_opening = enclosure_tassels[random.choice(next_openings)]
            add_resource(
                grid,
                Opening(current_opening),
                *current_opening,
                grid_width,
                grid_height,
            )
            dim_opening -= 1

    return random.choice(enclosure_tassels)


def initialize_isolated_area(
        grid,
        isolated_shape,
        isolated_length,
        isolated_width,
        grid_width,
        grid_height,
        radius,
):
    """
    Initialize the isolated area based on the specified shape.
    """

    def choose_random_corner(width, height):
        return random.choice([(0, 0), (0, height), (width, 0), (width, height)])

    x_corner, y_corner = choose_random_corner(grid_width, grid_height)
    if isolated_width != 0:
        dim_opening = random.randint(1, isolated_width) % grid_width

        if isolated_shape == "Square":
            return build_squared_isolated_area(
                x_corner,
                y_corner,
                isolated_length,
                isolated_width,
                grid,
                dim_opening,
                grid_width,
                grid_height,
            )
        else:
            return circular_isolation(
                grid,
                radius,
                x_corner,
                y_corner,
                dim_opening,
                grid_width,
                grid_height,
            )


def calculate_variance(value1, value2):
    """
    Calculate the variance between two values.
    """
    mean = (value1 + value2) / 2
    sum_of_squares = abs((value1 - mean) ** 2 + (value2 - mean) ** 2)
    return int(sum_of_squares / 2)


def find_and_draw_lines(grid, neighbors, grid_width, grid_height, dim_tassel):
    """
    Find and draw lines connecting neighboring cells to the perimeter.
    """

    def find_perimeter_cells(width, height):
        return [
            (x, y)
            for x in range(width)
            for y in range(height)
            if x in {0, width - 1} or y in {0, height - 1}
        ]

    def neighbor_on_the_perimeter(n, perimeter_cells):
        perimeter_set = perimeter_cells
        return any(neighbor in perimeter_set for neighbor in n)

    perimeter_guidelines = find_perimeter_cells(grid_width, grid_height)

    if neighbors and not neighbor_on_the_perimeter(neighbors, perimeter_guidelines):
        tree = KDTree(neighbors)
        closest_neighbor, nearest_perimeter, min_distance = None, None, float("inf")
        for pg_cell in perimeter_guidelines:
            distance, index = tree.query(pg_cell)
            if distance < min_distance:
                closest_neighbor = neighbors[index]
                min_distance = distance
                nearest_perimeter = pg_cell

        if closest_neighbor:
            draw_line(
                closest_neighbor[0],
                closest_neighbor[1],
                nearest_perimeter[0],
                nearest_perimeter[1],
                grid,
                grid_height,
                dim_tassel,
            )


def fill_circular_blocked_area(
        start_x,
        start_y,
        rad,
        grid,
        grid_width,
        grid_height,
        dim_tassel,
):
    def can_place(pos):
        blocked_areas = [
            GuideLine,
            IsolatedArea,
            SquaredBlockedArea,
            CircledBlockedArea,
            BaseStation,
        ]
        try:
            return (
                    0 < pos[0] < grid_width
                    and 0 < pos[1] < grid_height
                    and not contains_any_resource(
                grid,
                pos,
                blocked_areas,
                grid_width,
                grid_height,
            )
            )
        except IndexError:
            print(f"Invalid position: {pos}")
            return False

    squared_circle_count = int((math.pi * rad * rad) / 2)
    angle_delta = math.pi * 2 / squared_circle_count

    blocked_tassels = []

    for idx in range(squared_circle_count):  # Iterating over the squared circle count.
        angle = angle_delta * idx  # Calculating the angle for current iteration.
        center = (  # Calculating the center of the current circle.
            round(start_x + rad * math.cos(angle)),  # X coordinate of the center.
            round(start_y + rad * math.sin(angle)),  # Y coordinate of the center.
        )
        next_center = (  # Calculating the center of the next circle.
            round(
                center[0] + math.cos(angle + angle_delta) * 1 * 0.5
            ),  # X coordinate of the next center.
            round(
                center[1] + math.sin(angle + angle_delta) * 1 * 0.5
            ),  # Y coordinate of the next center.
        )
        midpoint = (  # Calculating the midpoint between current and next centers.
            round((next_center[0] + center[0]) / 2),  # X coordinate of the midpoint.
            round((next_center[1] + center[1]) / 2),  # Y coordinate of the midpoint.
        )

        dist = math.sqrt(  # Calculating the distance between midpoint and center.
            (midpoint[0] - center[0]) ** 2 + (midpoint[1] - center[1]) ** 2
        )
        """if (
            dist < 1 * 0.5
        ):  # , f"Distance {dist} exceeded allowed limit."  # Assertion to check distance limit.
            continue"""
        for i in range(-rad, rad + 1):  # Looping through x-coordinate range.
            for j in range(-rad, rad + 1):  # Looping through y-coordinate range.
                if (
                        i ** 2 + j ** 2 <= rad ** 2
                ):  # Checking if the point lies within the circle.
                    point = (
                        midpoint[0] + i,
                        midpoint[1] + j,
                    )  # Calculating the point within the circle.
                    if can_place(point) and not is_near_opening(
                            grid, point, grid_width, grid_height
                    ):
                        new_resource = CircledBlockedArea(
                            point
                        )  # Creating a new blocked area resource.

                        add_resource(
                            grid,
                            new_resource,
                            point[0],
                            point[1],
                            grid_width,
                            grid_height,
                        )
                        blocked_tassels.append(point)

    neighbors = []
    for tassel in blocked_tassels:
        for nb in grid.get_neighborhood(tassel, moore=True, include_center=False):
            if nb not in blocked_tassels and not is_near_opening(
                    grid, tassel, grid_width, grid_height
            ):
                neighbors.append((nb[0], nb[1]))

    for neighbor in neighbors:
        set_guideline_cell(
            neighbor[0], neighbor[1], grid, grid_width, grid_height, dim_tassel
        )

    find_and_draw_lines(grid, neighbors, grid_width, grid_height, dim_tassel)


def add_squared_area(
        coord_x,
        coord_y,
        min_width_blocked,
        max_height_blocked,
        max_width_blocked,
        min_height_blocked,
        grid,
        grid_width,
        grid_height,
        dim_tassel
):
    columns = calculate_variance(min_width_blocked, max_width_blocked)
    rows = calculate_variance(min_height_blocked, max_height_blocked)
    num_columns = math.ceil(columns + min_width_blocked)
    num_rows = math.ceil(rows + min_height_blocked)
    blocked_area = []
    resources = set()

    for j in range(num_rows):
        tassel_y = coord_y + j
        if 0 <= tassel_y < grid_height:
            for i in range(num_columns):
                tassel_x = coord_x + i
                if (
                        0 <= tassel_x < grid_width
                        and not is_near_opening(
                    grid, (tassel_x, tassel_y), grid_width, grid_height
                )
                        and (tassel_x, tassel_y) not in resources
                ):
                    add_resource(
                        grid,
                        SquaredBlockedArea((tassel_x, tassel_y)),
                        tassel_x,
                        tassel_y,
                        grid_width,
                        grid_height,
                    )
                    resources.add((tassel_x, tassel_y))
                    blocked_area.append((tassel_x, tassel_y))

    neighbors = []
    for tassel in blocked_area:
        for nb in grid.get_neighborhood(tassel, moore=True, include_center=False):
            if nb not in blocked_area and not is_near_opening(
                    grid, tassel, grid_width, grid_height
            ):
                neighbors.append((nb[0], nb[1]))

    for neighbor in neighbors:
        set_guideline_cell(
            neighbor[0], neighbor[1], grid, grid_width, grid_height, dim_tassel
        )

    find_and_draw_lines(grid, neighbors, grid_width, grid_height, dim_tassel)

    return blocked_area


def aux_lines(blocked_area, grid, grid_width, grid_height, dim_tassel):
    def get_circular_neighbors(cell):
        # Helper function to validate a single coordinate value
        def _valid_coordinate(h, max_val):
            """Check if a coordinate value is inside grid bounds"""
            return -1 < h < max_val

        n = set()  # Initialize empty set to store unique neighbor coordinates
        x, y = cell

        # Loop through possible relative offsets (-1, 0, 1) along both axes
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy

                # Check if the potential neighbor is within grid boundaries and has no common tassel
                if (
                        _valid_coordinate(nx, grid_width)
                        and _valid_coordinate(ny, grid_height)
                ) and ((abs(dx) + abs(dy)) == 1):
                    n.add((nx, ny))
                else:
                    print(f"Invalid position: ({nx}, {ny})")

        return n

    neighbors = get_circular_neighbors(blocked_area)

    for neighbor in neighbors:
        set_guideline_cell(
            neighbor[0], neighbor[1], grid, grid_width, grid_height, dim_tassel
        )

    find_and_draw_lines(grid, neighbors, grid_width, grid_height, dim_tassel)


def is_near_opening(grid, point, grid_width, grid_height):
    """
    Check if a point is near an opening.
    """
    neighbors = grid.get_neighborhood(point, moore=True, include_center=False)
    return any(
        contains_any_resource(grid, nb, [Opening], grid_width, grid_height)
        for nb in neighbors
    )


def generate_valid_agent_position(grid, grid_width, grid_height, max_attempts=35):
    """
    Generate a valid agent position that is not near any blocked area or opening.
    """
    blocked_types = [
        IsolatedArea,
        SquaredBlockedArea,
        CircledBlockedArea,
        Opening,
        GuideLine,
    ]
    for _ in range(max_attempts):
        x, y = random.randrange(0, grid_width), random.randrange(0, grid_height)
        if (
                within_bounds(grid_width, grid_height, (x, y))
                and not contains_any_resource(
            grid,
            (x, y),
            blocked_types,
            grid_width,
            grid_height,
        )
                and not is_near_opening(grid, (x, y), grid_width, grid_height)
        ):
            return x, y
    return None


def populate_blocked_areas(
        num_squares,
        num_circles,
        min_width_blocked,
        max_width_blocked,
        min_height_blocked,
        max_height_blocked,
        ray,
        grid,
        grid_width,
        grid_height,
        dim_tassel,
):
    """
    Populate the grid with blocked areas.
    """
    blocked_tassels = []
    max_size = 0

    for _ in range(num_squares):
        pos = generate_valid_agent_position(grid, grid_width, grid_height)
        if pos:
            blocked_tassels = add_squared_area(pos[0], pos[1], min_width_blocked, max_height_blocked, max_width_blocked,
                                               min_height_blocked, grid, grid_width, grid_height, dim_tassel)
            if len(blocked_tassels) > max_size:
                max_size = blocked_tassels

    for _ in range(num_circles):
        pos = generate_valid_agent_position(grid, grid_width, grid_height)
        if pos:
            fill_circular_blocked_area(
                pos[0],
                pos[1],
                ray,
                grid,
                grid_width,
                grid_height,
                dim_tassel,
            )

    if len(blocked_tassels) > 0:
        return blocked_tassels


class DefaultRandomGrid(RandomGrid):
    """
    Default grid with random initialization for isolated areas and blocked areas.
    """

    def __init__(
            self,
            width,
            length,
            isolated_shape,
            num_blocked_squares,
            min_width_square,
            max_width_square,
            min_height_square,
            max_height_square,
            num_blocked_circles,
            min_ray,
            max_ray,
            isolated_area_min_length,
            isolated_area_max_length,
            min_radius,
            max_radius,
            isolated_area_min_width,
            isolated_area_max_width,
            dim_tassel,
    ):
        super().__init__(width, length)
        self._isolated_width = isolated_area_min_width + random.randint(
            0, calculate_variance(isolated_area_min_width, isolated_area_max_width)
        )
        self._isolated_length = isolated_area_min_length + random.randint(
            0, calculate_variance(isolated_area_min_length, isolated_area_max_length)
        )
        self._ray = min_ray + random.randint(0, calculate_variance(min_ray, max_ray))

        self._isolated_shape = isolated_shape
        self._min_height_blocked = min_height_square
        self._max_height_blocked = max_height_square

        self._min_width_blocked = min_width_square
        self._max_width_blocked = max_width_square
        self._radius = min_radius + random.randint(
            0, calculate_variance(min_radius, max_radius)
        )

        self._num_blocked_squares = num_blocked_squares
        self._num_blocked_circles = num_blocked_circles
        self._dim_tassel = dim_tassel

        self._grid = MultiGrid(length, width, torus=False)

    # @profile
    def begin(self):
        random_corner = initialize_isolated_area(
            self._grid,
            self._isolated_shape,
            self._isolated_length,
            self._isolated_width,
            self._width,
            self._length,
            self._radius,
        )

        blocked_tassels = populate_blocked_areas(
            self._num_blocked_squares,
            self._num_blocked_circles,
            self._grid,
            self._min_width_blocked,
            self._max_width_blocked,
            self._min_height_blocked,
            self._max_height_blocked,
            self._ray,
            self._width,
            self._length,
            self._dim_tassel,
        )

        return self._grid, random_corner, blocked_tassels


def add_area(grid, t, tassels, opening_tassels, grid_width, grid_height, dim_tassel):
    if t == "circles":
        for tassel in tassels:
            add_resource(
                grid,
                CircledBlockedArea((tassel[0], tassel[1])),
                tassel[0],
                tassel[1],
                grid_width,
                grid_height,
            )
        neighbors = []
        for tassel in tassels:
            if within_bounds(grid_width, grid_height, tassel):
                for nb in grid.get_neighborhood(tassel, moore=True, include_center=False):
                    if nb not in tassels and not is_near_opening(
                            grid, tassel, grid_width, grid_height
                    ):
                        neighbors.append((nb[0], nb[1]))

        for neighbor in neighbors:
            set_guideline_cell(
                neighbor[0], neighbor[1], grid, grid_width, grid_height, dim_tassel
            )

        find_and_draw_lines(grid, neighbors, grid_width, grid_height, dim_tassel)
    elif t == "squares":
        for tassel in tassels:
            add_resource(
                grid,
                SquaredBlockedArea((tassel[0], tassel[1])),
                tassel[0],
                tassel[1],
                grid_width,
                grid_height,
            )
        neighbors = set()
        for tassel in tassels:
            if within_bounds(grid_width, grid_height, tassel):
                for nb in grid.get_neighborhood(tassel, moore=True, include_center=False):
                    if nb not in tassels and not is_near_opening(
                            grid, tassel, grid_width, grid_height
                    ):
                        neighbors.add((nb[0], nb[1]))

        for neighbor in neighbors:
            set_guideline_cell(
                neighbor[0], neighbor[1], grid, grid_width, grid_height, dim_tassel
            )

        find_and_draw_lines(grid, neighbors, grid_width, grid_height, dim_tassel)
    elif t == "is_area":
        for tassel in tassels:
            add_resource(
                grid,
                IsolatedArea((tassel[0], tassel[1])),
                tassel[0],
                tassel[1],
                grid_width,
                grid_height,
            )
        for tassel in opening_tassels:
            add_resource(
                grid,
                Opening((tassel[0], tassel[1])),
                tassel[0],
                tassel[1],
                grid_width,
                grid_height,
            )


class DefaultCreatedGrid(RandomGrid):
    """
    Default grid created from raw shape data.
    """

    def __init__(self, grid_width, grid_height, data_e, raw_shapes, dim_tassel):
        super().__init__(grid_width, grid_height)
        self.data_e = data_e
        self.grid = MultiGrid(grid_height, grid_width, torus=False)
        self.random_corner = (-1, -1)
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.raw_shapes = raw_shapes
        self.dim_tassel = dim_tassel

    def begin(self):
        """
        Begin populating the grid based on raw shape data.
        """
        print(f"----- GRID WIDTH: {self.grid_width}")
        circles = self.data_e["circles"]
        circles_rounded = set()
        squares_rounded = set()
        t = None

        if circles:
            for t in circles:
                # for t in tassel:

                x, y = (int(t[0]), int(t[1]))
                circles_rounded.add((x, y))
            add_area(self.grid, "circles", circles_rounded, [], self.grid_width, self.grid_height, self.dim_tassel)

        squares = self.data_e["squares"]

        if squares:
            for t in squares:
                # for t in tassel:
                x, y = (
                    int(t[0]),
                    int(t[1]),
                )
                squares_rounded.add((x, y))
            add_area(self.grid, "squares", squares_rounded, [], self.grid_width, self.grid_height, self.dim_tassel)

        opening = self.data_e["opening"]
        isolated_area = self.data_e["isolated_area"]
        if opening and isolated_area:
            opening_rounded = []
            # for tassel in opening:
            x, y = (
                math.ceil(opening[0]),
                math.ceil(opening[1]),
            )
            opening_rounded.append((x, y))

            isolated_area_rounded = set()
            for tassel in isolated_area:
                x, y = (
                    math.ceil(tassel[0]),
                    math.ceil(tassel[1]),
                )
                isolated_area_rounded.add((x, y))
            add_area(self.grid, "is_area", isolated_area_rounded, opening_rounded, self.grid_width, self.grid_height,
                     self.dim_tassel)
            self.random_corner = random.choice(opening)
            t = (
                math.ceil(self.random_corner[0]),
                math.ceil(self.random_corner[1]),
            )

        return self.grid, t, squares_rounded
