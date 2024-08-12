import cProfile
import json
import math
import os
import pstats
import random
from io import StringIO
from typing import Union, Tuple

try:
    from Model.agents import (
        BaseStation,
        GuideLine,
        SquaredBlockedArea,
        GrassTassel,
        CircledBlockedArea,
        Opening,
        Robot,
        IsolatedArea,
    )
except ImportError:
    print(
        "Error: Could not import `Model.agents`. Make sure it is installed and accessible."
    )
    exit()


def validate_and_adjust_base_station(coords, grid_width, grid_height, grid):
    if (
            coords is None
            or not within_bounds(grid_width, grid_height, coords)
            or contains_any_resource(
        grid,
        coords,
        [SquaredBlockedArea, CircledBlockedArea, IsolatedArea],
        grid_width,
        grid_height,
    )
    ):

        def maybe_move_to_adjacent_valid_tile():
            if coords:
                x, y = coords
            else:
                x, y = (0, 0)
            offsets = (
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            )
            for dx, dy in offsets:
                new_x, new_y = x + dx, y + dy
                if within_bounds(
                        grid_width, grid_height, (new_x, new_y)
                ) and not contains_any_resource(
                    grid,
                    coords,
                    [SquaredBlockedArea, CircledBlockedArea, IsolatedArea],
                    grid_width,
                    grid_height,
                ):
                    return new_x, new_y
            return coords

        return maybe_move_to_adjacent_valid_tile()

    return coords


def perimeter_try_generating_base_station(
        grid_width,
        grid_height,
        base_station,
        grid,
) -> Tuple[int, int]:
    def generate_perimeter_pair(width: int, length: int) -> Tuple[int, int]:
        return (
            (0, random.randint(0, width))
            if random.choice([0, 1]) == 0
            else (random.randint(0, length), 0)
        )

    while base_station is None:
        try:
            tmp_bs = generate_perimeter_pair(grid_width, grid_height)
            base_station = validate_and_adjust_base_station(
                tmp_bs, grid_width, grid_height, grid
            )
        except ValueError:
            base_station = None
    return base_station


def big_center_try_generating_base_station(
        center_tassel,
        grid_width,
        grid_height,
        base_station,
        biggest_blocked_area,
        grid,
):
    if biggest_blocked_area:
        while base_station is None:
            try:
                tmp_bs = generate_biggest_center_pair(
                    center_tassel, biggest_blocked_area
                )
                base_station = validate_and_adjust_base_station(
                    tmp_bs, grid_width, grid_height, grid
                )
            except ValueError:
                base_station = None
        return base_station
    else:
        return None


class StationGuidelinesStrategy:
    def locate_base_station(
            self,
            grid,
            center_tassel,
            biggest_blocked_area,
            grid_width,
            grid_height,
    ):
        pass


class PerimeterPairStrategy(StationGuidelinesStrategy):
    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, grid_width, grid_height
    ):
        base_station = None
        attempt_limit = 35

        for _ in range(attempt_limit):
            base_station = perimeter_try_generating_base_station(
                grid_width, grid_height, base_station, grid
            )
            if base_station is not None and add_base_station(
                    grid, base_station, grid_width, grid_height
            ):
                return base_station
        return None


class BiggestRandomPairStrategy(StationGuidelinesStrategy):
    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, grid_width, grid_height
    ) -> Union[Tuple[int, int], None]:

        base_station = None
        attempt_limit = 35

        def generate_biggest_pair(bba):
            random_choice = random.choice(bba) if bba else None
            print(f"RANDOM CHOICE {random_choice}")
            return random_choice

        def big_random_try_generating_base_station(bs):
            while bs is None:
                try:
                    tmp_bs = generate_biggest_pair(biggest_blocked_area)
                    bs = validate_and_adjust_base_station(
                        tmp_bs, grid_width, grid_height, grid
                    )
                except ValueError:
                    bs = None
            return bs

        if biggest_blocked_area:
            for _ in range(attempt_limit):
                base_station = big_random_try_generating_base_station(base_station)
                if base_station is not None and add_base_station(
                        grid, base_station, grid_width, grid_height
                ):
                    return base_station
            return None
        else:
            return None


class BiggestCenterPairStrategy(StationGuidelinesStrategy):
    def locate_base_station(
            self, grid, center_tassel, biggest_blocked_area, grid_width, grid_height
    ) -> Union[Tuple[int, int], None]:
        base_station = None
        attempt_limit = 35

        for _ in range(attempt_limit):
            base_station = big_center_try_generating_base_station(
                center_tassel,
                grid_width,
                grid_height,
                base_station,
                biggest_blocked_area,
                grid,
            )
            if base_station is not None and add_base_station(
                    grid, base_station, grid_width, grid_height
            ):
                return base_station
        return None


def mowing_time(speed_robot, autonomy_robot_seconds, cutting_diameter, total_area):
    # Calculate the area covered per pass
    # cutting_area = math.pi * (cutting_diameter / 2) ** 2

    # Calculate the number of passes required to cover the total area
    # passes_needed = math.ceil(total_area / cutting_area)

    # Calculate the total distance covered (assuming an optimized path)
    # total_distance = passes_needed * cutting_area / (math.pi * cutting_diameter)

    # Calculate the total time required
    total_time_minutes = total_area / speed_robot
    # total_distance / speed_robot

    # Convert total time from minutes to seconds
    total_time_seconds = total_time_minutes * 60
    # print(f"AUTONOMY: {autonomy_robot_seconds} ======== TOTAL TIME: {total_time_seconds}")
    # Check if the autonomy is sufficient to complete the job
    if total_time_seconds > autonomy_robot_seconds:
        print(f"Warning: The robot's autonomy might not be sufficient.")
        pass

    return total_time_seconds


def euclidean_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def generate_biggest_center_pair(center_tassel, biggest_blocked_area):
    if not biggest_blocked_area:
        return None

    nearest_tuple = min(
        biggest_blocked_area, key=lambda pos: euclidean_distance(pos, center_tassel)
    )

    return nearest_tuple


"""def dfs(grid, x, y, resource, visited, grid_width, grid_height):
    stack = [(x, y)]
    count = 0

    while stack:
        cx, cy = stack.pop()

        if (cx, cy) in visited:
            continue

        visited.add((cx, cy))
        count += 1

        for nx, ny in [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]:
            if (
                0 <= nx < grid_width
                and 0 <= ny < grid_height
                and (nx, ny) not in visited
            ):
                if grid[ny][nx] == resource:
                    stack.append((nx, ny))

    return count"""

"""def get_largest_successive_cells(
    grid, grid_width: int, grid_height: int, resources: Set[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    visited = set()
    max_size = 0
    max_resource = None

    for x, y in resources:
        if (x, y) not in visited:
            resource = grid[x][y]
            if contains_resource(
                grid, (x, y), SquaredBlockedArea, grid_width, grid_height
            ):  # Assuming contains_resource correctly identifies the resource
                size = dfs(grid, x, y, resource, visited, grid_width, grid_height)
                if size >= max_size:
                    max_size = size
                    max_resource = resource

    if max_resource is None:
        return []

    # Re-run DFS to get all positions of the largest group
    visited.clear()

    for x, y in resources:
        if (x, y) not in visited and grid[y][x] == max_resource:
            dfs(grid, x, y, max_resource, visited, grid_width, grid_height)

    result = list(visited)
    return result"""


def load_data_from_file(file_path: str) -> Union[Tuple[dict, dict, dict], None]:
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    return data.get("robot", {}), data.get("env", {}), data.get("simulator", {})


def put_station_guidelines(
        strategy,
        grid,
        grid_width: int,
        grid_height: int,
        random_corner_perimeter,
        central_tassel,
        biggest_area_blocked,
):
    base_station_pos = strategy.locate_base_station(
        strategy, grid, central_tassel, biggest_area_blocked, grid_width, grid_height
    )

    if base_station_pos:
        if random_corner_perimeter:
            draw_line(
                base_station_pos[0],
                base_station_pos[1],
                random_corner_perimeter[0],
                random_corner_perimeter[1],
                grid,
                grid_width,
                grid_height,
            )

        # Find the farthest point from base station
        farthest_point = find_farthest_point(
            grid_width, grid_height, base_station_pos[0], base_station_pos[1]
        )

        # If farthest point is found, draw line from base station to it
        if farthest_point is not None:
            draw_line(
                base_station_pos[0],
                base_station_pos[1],
                farthest_point[0],
                farthest_point[1],
                grid,
                grid_width,
                grid_height,
            )

    return base_station_pos


def contains_any_resource(grid, pos, resource_types, grid_width, grid_height):
    for rtype in resource_types:
        if contains_resource(grid, pos, rtype, grid_width, grid_height):
            return True
    return False


def draw_line(x1, y1, x2, y2, grid, grid_width, grid_height):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    x, y = x1, y1

    cells_to_add = set()
    err = dx - dy

    while (x, y) != (x2, y2):
        if within_bounds(grid_width, grid_height, (x, y)):

            curr_cell = grid[x][y]
            if curr_cell is not None and not contains_any_resource(
                grid,
                (x, y),
                [
                    CircledBlockedArea,
                    SquaredBlockedArea,
                    IsolatedArea,
                    BaseStation,
                    GuideLine,
                ],
                grid_width,
                grid_height,
            ):
                cells_to_add.add((x, y))
                add_resource(grid, GuideLine((x, y)), x, y, grid_width, grid_height)

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        else:
            break

    if within_bounds(grid_width, grid_height, (x2, y2)):
        cells_to_add.add((x2, y2))
        add_resource(grid, GuideLine((x2, y2)), x2, y2, grid_width, grid_height)

    return cells_to_add


def contains_resource(grid, cell, resource, grid_width, grid_height):
    x, y = cell

    # Add these checks to ensure x and y are within bounds
    if 0 <= x < grid_width and 0 <= y < grid_height:

        cell_contents = grid.get_cell_list_contents(cell)

        specific_agent = next(
            (agent for agent in cell_contents if isinstance(agent, resource)), None
        )

        if specific_agent:
            return True
        else:
            return False
    else:
        return False


def add_base_station(grid, position, grid_width, grid_height):
    base_station = BaseStation((position[0], position[1]))

    return add_resource(
        grid, base_station, position[0], position[1], grid_width, grid_height
    )


def set_guideline_cell(x, y, grid, grid_width, grid_height):
    # Check if the cell is within the grid boundaries (after wrapping)
    if not within_bounds(grid_width, grid_height, (x, y)):
        return False

    blocked_areas = [
        CircledBlockedArea,
        SquaredBlockedArea,
        IsolatedArea,
        BaseStation,
        GuideLine,
    ]

    # Check for existing resources at the wrapped cell
    if not contains_any_resource(
            grid,
            (x, y),
            blocked_areas,
            grid_width,
            grid_height,
    ):
        add_resource(grid, GuideLine((x, y)), x, y, grid_width, grid_height)


def add_resource(grid, resource, x, y, grid_width, grid_height):
    if within_bounds(grid_width, grid_height, (x, y)):
        grid.place_agent(resource, (x, y))
        return True
    else:
        return False


def within_bounds(grid_width, grid_height, pos):
    return 0 <= pos[0] < grid_width and 0 <= pos[1] < grid_height


def find_farthest_point(grid_width, grid_height, fx, fy):
    max_dist = 0
    result = (-1, -1)

    eligible_points = [
        (0, grid_height),
        (grid_width, 0),
        (0, 0),
        (grid_width, grid_height),
    ]

    for point in eligible_points:
        dist = euclidean_distance((fx, fy), point)
        if dist > max_dist:
            max_dist = dist
            result = point
            if dist > grid_width or dist > grid_height:  # Early return if very far
                return result

    return result


def populate_perimeter_guidelines(grid_width, grid_height, grid, dim_tassel):
    for x in range(0, grid_height):
        set_guideline_cell(x, 0, grid, grid_width, grid_height)

    for x in range(0, grid_height):
        set_guideline_cell(x, grid_width, grid, grid_width, grid_height)

    for y in range(0, grid_width):
        set_guideline_cell(0, y, grid, grid_width, grid_height)

    for y in range(0, grid_width):
        set_guideline_cell(grid_height, y, grid, grid_width, grid_height)


def get_grass_tassel(grass_tassels, pos):
    # print(f"grass tassels: {grass_tassels}")
    for res in grass_tassels:

        # print(f"RES: {res}")
        if res.get() == pos:
            return res

    return None


def find_central_tassel(rows, cols):
    if rows % 2 == 1 and cols % 2 == 1:
        central_row = rows // 2
        central_col = cols // 2
        return central_row, central_col
    else:
        central_row = rows // 2 if rows % 2 == 1 else rows // 2 - 1
        central_col = cols // 2 if cols % 2 == 1 else cols // 2 - 1
        return central_row, central_col


def profile_code(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return result

    return wrapper
