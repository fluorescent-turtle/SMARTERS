import json
import os
import random

from mesa.space import MultiGrid

from Controller.environment_plugin import DefaultRandomGrid
# Import necessary modules

from Controller.robot_plugin import DefaultRobot
from Utils.utils import (
    put_station_guidelines,
    PerimeterPairStrategy,
    BiggestRandomPairStrategy,
    BiggestCenterPairStrategy,
)


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


def creates_robot(robot_plugins):
    """
    Create a new instance of the default robot class with given plugins.

    Parameters:
        robot_plugins (list): List of plugin objects to add to the robot.

    Returns:
        Robot: An initialized robot object.
    """
    robot = DefaultRobot.begin()

    # Add plugins to the robot
    for module in robot_plugins:
        module(robot).begin()

    return robot


def creates_environment(data_e, tassel_dim, env_plugins, isolated_area_tassels):
    width = data_e.get("width")
    length = data_e.get("length")
    isolated_shape = data_e.get("isolated_area_shape")
    min_height_blocked = data_e.get("min_height_square")
    max_height_blocked = data_e.get("max_height_square")
    min_width_blocked = data_e.get("min_width_square")
    max_width_blocked = data_e.get("max_width_square")
    num_blocked_squares = data_e.get("num_blocked_squares")
    num_blocked_circles = data_e.get("num_blocked_circles")
    radius = data_e.get("radius")
    isolated_width = data_e.get("isolated_area_width")
    isolated_length = data_e.get("isolated_area_length")

    grid = MultiGrid(width, length, torus=False)

    resources = []

    DefaultRandomGrid(
        width,
        length,
        isolated_shape,
        min_height_blocked,
        max_height_blocked,
        min_width_blocked,
        max_width_blocked,
        radius,
        tassel_dim,
        isolated_area_tassels,
        num_blocked_squares,
        num_blocked_circles,
        resources,
        grid,
        isolated_width,
        isolated_length,
    ).begin()

    for module in env_plugins:
        module(
            grid,
            width,
            length,
            isolated_shape,
            min_height_blocked,
            max_height_blocked,
            min_width_blocked,
            max_width_blocked,
            radius,
            tassel_dim,
            isolated_area_tassels,
            num_blocked_squares,
            num_blocked_circles,
            resources,
        ).begin()

    return resources, grid


def generate_random_corner(width, length):
    return random.choice(
        [(0, 0), (0, length - 1), (width - 1, 0), (width - 1, length - 1)]
    )


def begins_simulation(env_plugins, robot_plugins):
    """
    Initialize and start the simulation process.

    Parameters:
        env_plugins (list): List of plugin objects for the environment.
        robot_plugins (list): List of plugin objects for the robot.

    Returns:
        None
    """
    # Load data from file
    data_r, data_e, data_s = load_data_from_file("../SetUp/data_file")

    # Extract relevant simulation parameters
    repetitions = data_s["repetitions"]
    cycle = data_s["cycle"]
    tassel_dim = data_s["dim_tassel"]

    # Initialize the environment with plugins
    resources, grid = creates_environment(data_e, tassel_dim, env_plugins, isolated_area_tassels)

    # Create the robot with plugins
    current_robot = creates_robot(robot_plugins)

    # Random corner
    random_corner = generate_random_corner(data_e["width"], data_e["length"])
    # Add base station and guidelines
    put_station_guidelines(
        strategy=PerimeterPairStrategy,
        grid=grid,
        width=data_e["width"],
        length=data_e["length"],
        resources=resources,
        random_corner_perimeter=random_corner,
        central_tassel=None,
        biggest_area_blocked=[],
    )
    # Start the simulation with given parameters
    run_model_with_parameters(
        grid,
        resources,
        repetitions,
        cycle,
        tassel_dim,
        current_robot,
    )

    """# Random corner
    random_corner = generate_random_corner(data_e["width"], data_e["length"])
    # Add base station and guidelines
    put_station_guidelines(
        BiggestRandomPairStrategy,
        grid,
        data_e["width"],
        data_e["length"],
        resources,
        random_corner,
        None,
        [],
    )
    # Start the simulation with given parameters
    run_model_with_parameters(
        grid,
        resources,
        repetitions,
        cycle,
        tassel_dim,
        current_robot,
    )

    # Random corner
    random_corner = generate_random_corner(data_e["width"], data_e["length"])
    # Add base station and guidelines
    put_station_guidelines(
        BiggestCenterPairStrategy,
        grid,
        data_e["width"],
        data_e["length"],
        resources,
        random_corner,
        None,
        [],
    )
    # Start the simulation with given parameters
    run_model_with_parameters(
        grid,
        resources,
        repetitions,
        cycle,
        tassel_dim,
        current_robot,
    )"""


def run_model_with_parameters(grid, resources, repetitions, cycles, dim_tassel, robot):
    """
    Run the model with provided parameters.

    Args:
        grid: Grid object.
        resources: List of resources on the grid.
        repetitions: Number of repetitions.
        cycles: Number of cycles.
        dim_tassel: Tassel dimension.
        robot: Robot

    Returns:
        None
    """
    for _ in range(repetitions):  # todo: non ha senso che ho lo stesso ambiente
        for _ in range(cycles):
            """simulation = Simulator(
                grid, robot_data, resources, dim_tassel, robot
            )
            simulation.step()"""
