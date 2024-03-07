import itertools
import json
import random
from mesa.space import SingleGrid, MultiGrid

from agents import GuideLine
from model import Simulator
from utils import (
    initialize_isolated_area,
    populate_blocked_areas,
    populate_perimeter_guidelines,
    add_base_station,
    generate_pair,
    find_largest_blocked_area,
    add_resource,
)


# todo: function that will allow to custom the grid
def custom_environment(extra_data):
    pass


def create_random_grid(
        environment_data,
        tassel_dim,
        isolated_area_tassels,
        extra_data
):
    """
    Create a random grid environment based on the provided parameters.

    Args:
        environment_data (dict): Data related to the environment.
        tassel_dim (float): Dimension of the tassel.
        isolated_area_tassels (list): List to store tassel coordinates for the isolated area.
        extra_data (dict): Additional data from developer

    Returns:
        mesa.space.Grid: The grid environment.
        list: List of resources in the grid.
    """
    # Set environment parameters
    width = environment_data["width"]
    length = environment_data["length"]
    isolated_shape = environment_data["isolated_area_shape"]
    min_height_blocked = environment_data["min_height_square"]
    max_height_blocked = environment_data["max_height_square"]
    min_width_blocked = environment_data["min_width_square"]
    max_width_blocked = environment_data["max_width_square"]
    num_blocked_squares = environment_data["num_blocked_squares"]
    num_blocked_circles = environment_data["num_blocked_circles"]
    radius = environment_data["radius"]
    isolated_area_width = environment_data["isolated_area_width"]
    isolated_area_length = environment_data["isolated_area_length"]
    ray = environment_data["ray"]

    # Initialize model components
    grid = MultiGrid(int(width), int(length), torus=False)  # todo: change to multigrid

    resources = []
    counter = itertools.count

    # Add isolated area to the grid
    initialize_isolated_area(
        grid,
        isolated_shape,
        isolated_area_width,
        isolated_area_length,
        environment_data,
        isolated_area_tassels,
        radius,
        tassel_dim,
        resources,
        counter,
    )

    # Populate the grid with blocked areas
    populate_blocked_areas(
        resources,
        num_blocked_squares,
        num_blocked_circles,
        grid,
        min_width_blocked,
        max_width_blocked,
        min_height_blocked,
        max_height_blocked,
        ray,
        tassel_dim,
    )

    position = None
    while position is None:
        base_station = generate_pair(
            environment_data["width"], environment_data["length"]
        )
        # Add base station to the perimeter
        position = add_base_station(
            grid,
            base_station,
            resources,
        )

    # Populate the grid with perimeter guidelines
    populate_perimeter_guidelines(int(width), int(length), grid, resources)

    # todo: qui si estrapolano le altre caratteristiche
    custom_environment(extra_data)

    return grid, resources, position


def run_model_with_parameters(robot_data, grid, resources, repetitions, cycles):
    """
    Run the simulation with the specified parameters.

    Args:
        robot_data (dict): Data related to the robot.
        grid (Grid): The grid on which the simulation will be run.
        resources (list): List of resources to be used in the simulation.
        repetitions (int): Number of repetitions.
        cycles (int): Number of cycles per repetition.

    Returns:
        None
    """
    for repetition in range(repetitions):
        for cycle in range(cycles):
            # Start the simulation
            simulation = Simulator(grid, robot_data, resources)
            simulation.step()


def set_cell(x, y, grid, resources):
    """
    Set a cell on the grid with a guide line.

    Args:
        x (int): The x-coordinate of the cell.
        y (int): The y-coordinate of the cell.
        grid (mesa.space.Grid): The grid space.
        resources (list): List of resources.

    Returns:
        None
    """
    guide_line = GuideLine((x, y))
    add_resource(grid, guide_line, x, y)
    resources.append((x, y))


def draw_line(x1, y1, x2, y2, grid, resources):
    """
    Draw a line between two points on the grid.

    Args:
        x1 (int): The x-coordinate of the starting point.
        y1 (int): The y-coordinate of the starting point.
        x2 (int): The x-coordinate of the ending point.
        y2 (int): The y-coordinate of the ending point.
        grid (mesa.space.Grid): The grid space.
        resources (list): List of resources.

    Returns:
        None
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while (x1, y1) != (x2, y2):
        set_cell(x1, y1, grid, resources)
        print("SET CELL: ", (x1, y1))
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    set_cell(x1, y1, grid, resources)


def begin_simulation():
    """
    Begin the simulation with the specified parameters.
    """
    # Read data from JSON files in another directory
    with open(
            "../SetUp/robot_file", "r"
    ) as robot_file:  # TODO: modify the directory if your file are somewhere else
        robot_data = json.load(robot_file)
    with open(
            "../SetUp/environment_file", "r"
    ) as environment_file:  # TODO: modify the directory if your file are somewhere else
        environment_data = json.load(environment_file)
    with open(
            "../SetUp/simulator_file", "r"
    ) as simulator_file:  # TODO: modify the directory if your file are somewhere else
        simulator_data = json.load(simulator_file)
    # with open("../SetUp/extra_file", "r") as extra_file:
    #    extra_data = json.load(extra_file)"""

    isolated_area_tassels = []
    grid, resources, position = create_random_grid(
        environment_data,
        simulator_data["dim_tassel"],
        isolated_area_tassels,

    )

    if isolated_area_tassels is not []:
        # Draw a line from the base station to a random tassel in the isolated area
        random_tassel = random.choice(isolated_area_tassels)
        draw_line(
            position[0],
            position[1],
            random_tassel[0],
            random_tassel[1],
            grid,
            resources,
        )

        # Run model
        run_model_with_parameters(
            robot_data,
            grid,
            resources,
            simulator_data["repetitions"],
            simulator_data["cycle"],
        )

        # Add base station to the biggest blocked area randomly
        biggest_area, coords = find_largest_blocked_area(grid)
    else:
        print("Base station position is None")
        """ 
        # Calculate position for the base station
       base_station_position = calculate_position(
            grid, False, coords, environment_data["width"], environment_data["length"]
        )

        add_base_station(grid, base_station_position, resources)
        run_model_with_parameters(robot_data, grid, resources, repetitions, cycle)

        # Add base station to the biggest area nearest to the center
        # Calculate position for the base station
        base_station_position1 = calculate_position(
            grid, True, coords, environment_data["width"], environment_data["length"]
        )

        add_base_station(grid, base_station_position1, resources)
        run_model_with_parameters(robot_data, grid, resources, repetitions, cycle)"""
