import itertools
import json
import os
import random

from mesa.space import SingleGrid, MultiGrid
from agents import GuideLine
from Model.model import Simulator
from Utils.utils import (
    initialize_isolated_area,
    populate_blocked_areas,
    populate_perimeter_guidelines,
    add_base_station,
    generate_pair,
    find_largest_blocked_area,
    add_resource,
)


def create_random_grid(environment_data, tassel_dim, isolated_area_tassels, plugins):

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
    grid = MultiGrid(int(width), int(length), torus=False)

    # Apply all provided plugins to the grid
    for plugin in plugins:
        grid = apply_plugin(plugin, grid)

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

    return grid, resources, position


def run_model_with_parameters(
        robot_data, grid, resources, repetitions, cycles, dim_tassel
):
    """
    Run the simulation with the specified parameters.

    Args:
        robot_data (dict): Robot information.
        grid (MultiGrid): Grid to perform the simulation on.
        resources (list): Resources present in the grid.
        repetitions (int): Number of times the experiment should repeat.
        cycles (int): Length of each experiment.
        dim_tassel (float): Dimension of the tassel

    Returns:
        None
    """
    for _ in range(repetitions):
        for _ in range(cycles):
            # Start the simulation
            simulation = Simulator(grid, robot_data, resources, dim_tassel)
            simulation.step()


def set_cell(x, y, grid, resources):
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


def draw_line(x1, y1, x2, y2, grid, resources):
    """
    Draw a straight line connecting two points using Bresenham's algorithm.

    Args:
        x1 (int): Starting point X coordinate.
        y1 (int): Starting point Y coordinate.
        x2 (int): Ending point X coordinate.
        y2 (int): Ending point Y coordinate.
        grid (SingleGrid or MultiGrid): Mesa Space object where the agents reside.
        resources (list): Resources available during initialization.

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
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    set_cell(x1, y1, grid, resources)


def begin_simulation(plugins):
    """
    Initiate the simulation by setting up required objects and running it.

    Returns:
        None
        :param plugins:
    """
    # Load data from external JSON files
    robot_data = None
    environment_data = None
    simulator_data = None
    isolated_area_tassels = []

    if os.path.exists("../SetUp/robot_file.json"):
        with open("../SetUp/robot_file.json") as f:
            robot_data = json.load(f)
    if os.path.exists("../SetUp/environment_file.json"):
        with open("../SetUp/environment_file.json") as f:
            environment_data = json.load(f)
    if os.path.exists("../SetUp/simulator_file.json"):
        with open("../SetUp/simulator_file.json") as f:
            simulator_data = json.load(f)
    # todo: in setup prende taglio - rimbalzo come plugin

    # Proceed with initialization regardless of existence of JSON files
    tassel_dim = simulator_data.get("tassel_dim", {}) if simulator_data else {}
    grid, resources, position = create_random_grid(
        environment_data, tassel_dim, isolated_area_tassels, plugins
    )

    if isolated_area_tassels is not []:
        random_tassel = random.choice(isolated_area_tassels)
        draw_line(
            position[0],
            position[1],
            random_tassel[0],
            random_tassel[1],
            grid,
            resources,
        )

        run_model_with_parameters(
            robot_data,
            grid,
            resources,
            simulator_data["repetitions"],
            simulator_data["cycles"],
            simulator_data["dim_tassel"],
        )

        # Add base station to the largest blocked area randomly
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
