import importlib

from mesa.space import MultiGrid

from Controller.environment_plugin import DefaultRandomGrid
from Controller.robot_plugin import DefaultMovementPlugin
from Model.agents import BaseStation, GuideLine
from Model.model import Simulator
from Utils.utils import (
    put_station_guidelines,
    PerimeterPairStrategy,
    get_most_frequent_elements,
    load_data_from_file,
    generate_random_corner,
    contains_resource,
    BiggestCenterPairStrategy,
    BiggestRandomPairStrategy,
    find_central_tassel,
    create_csv,
)


class Starter:
    """
    Initialize the Starter class by setting empty lists for environment and robot plugins,
    then attempt to import and instantiate each plugin passed in the constructor arguments.
    """

    def __init__(self, env_plugins, r_plugins):
        """
        Initialize the Starter class. Set empty lists for environment and robot plugins,
        then attempt to import and instantiate each plugin passed in the constructor arguments.

        Args:
            env_plugins (List[str]): Names of the environment plugins to import and instantiate.
            r_plugins (List[str]): Names of the robot plugins to import and instantiate.
        """
        self.env_plugins = []
        self.r_plugins = []

        # Loop over the environment plugins and initialize them
        if env_plugins:
            for plugin_name in env_plugins:
                try:
                    # Import the plugin module dynamically
                    plugin_module = importlib.import_module(
                        f"{plugin_name}", "../Controller"
                    )

                    # Get the plugin class from the imported module
                    plugin_class = getattr(plugin_module, plugin_name)

                    # Instantiate the plugin class and append it to the list of plugins
                    self.env_plugins.append(plugin_class())
                except ImportError as e:
                    print(f"Error importing plugin '{plugin_name}': {e}")

        # Loop over the robot plugins and initialize them
        if r_plugins:
            for plugin_name in r_plugins:
                try:
                    # Import the plugin module dynamically
                    plugin_module = importlib.import_module(
                        f"{plugin_name}", "../Controller"
                    )

                    # Get the plugin class from the imported module
                    plugin_class = getattr(plugin_module, plugin_name)

                    # Instantiate the plugin class and append it to the list of plugins
                    self.r_plugins.append(plugin_class())
                except ImportError as e:
                    print(f"Error importing plugin '{plugin_name}': {e}")

    def run(self):
        """
        Runs the lawnmowers simulation using the provided plugins.

        Returns:
            None
        """
        try:
            run_model_with_parameters(
                self.env_plugins, self.r_plugins
            )  # Begin the simulation with the list of plugins
        except Exception as e:
            print(f"Unexpected error occurred while running the simulation: {e}")


def create_environment(data_e, tassel_dim, env_plugins, isolated_area_tassels):
    """
    Creates a simulation environment with a grid, resources, and blocked cells.

    This function initializes the main grid for the simulation and sets up various
    aspects like resource placement, obstructed areas, etc. The function iterates
    through any provided environment plugins to further populate and configure the
    simulation environment.

    Args:
        data_e (dict): A dictionary holding initialization data for the environment.
        tassel_dim (int): Dimension of a single tassel.
        env_plugins (list): A list of environment plugin instances.
        isolated_area_tassels (list): A list of tuples indicating where isolated
            tassels are located in the environment.

    Returns:
        tuple: Two items are returned as a tuple: a list of resources and the
            MultiGrid instance for the environment.
    """
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

    ray = data_e.get("ray")

    # Initialize the grid
    grid = MultiGrid(width, length, torus=False)

    # Create empty lists of resources
    resources = []

    if not env_plugins:
        # Instantiate and call begin method on default grid plugin
        try:
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
                ray,
                resources,
                grid,
                isolated_width,
                isolated_length,
            ).begin()
        except Exception as e:
            print(
                "Error in creating the default environment: ", e)

    else:
        # Iterate through additional environment plugins and execute their begin methods
        for module in env_plugins:
            try:
                module(
                    grid,
                    width,
                    length,
                ).begin()
            except Exception as e:
                print(f"Error in beginning a custom environment plugin: {e}")

    return resources, grid


def env_initializer(env_plugins, data_e, data_s):
    """
    Creates a simulation environment with provided plugins.

    Args:
        env_plugins (list): List of environment plugin instances.
        data_e (dict): Initialization data for the environment.
        data_s (dict): Initialization data for the simulation.

    Returns:
        tuple: Two items are returned as a tuple: a list of resources and the
            MultiGrid instance for the environment.
    """
    # Extract relevant simulation parameters
    tassel_dim = data_s["dim_tassel"]

    isolated_area_tassels = []

    # Initialize the environment with plugins
    resources, grid = create_environment(
        data_e, tassel_dim, env_plugins, isolated_area_tassels
    )

    return resources, grid


def clear_non_perimeter_objects(grid):
    """
    Clear non-perimeter objects on the grid by calling their `clear` method.

    This function iterates over each cell in the grid that is not on its edge and checks
    if it contains either a `BaseStation` or a `GuideLine`. If it does, the object's
    `clear` method is called to remove it from the grid.

    Args:
        grid (Grid): The grid containing the objects to be cleared.
    """
    try:
        # Iterate over all cells except those on the perimeter
        for x in range(grid.width - 1):
            for y in range(grid.height - 1):

                # Check if the current cell contains a BaseStation
                if contains_resource(grid, (x, y), BaseStation):
                    BaseStation((x, y)).clear()

                # Check if the current cell contains a GuideLine
                elif contains_resource(grid, (x, y), GuideLine):
                    GuideLine((x, y)).clear()
    except Exception as e:
        print("Error clearing non-perimeter objects:", str(e))


def split_at_first_hyphen(string):
    """
    Split a string into two parts at the first occurrence of a hyphen character.

    This function takes a string as input and returns a tuple containing the substring
    before the first hyphen and the substring after it. If the input string does not
    contain any hyphens, the function returns a tuple with the original string as
    both elements.

    Args:
        string (str): The input string to be split.

    Returns:
        A tuple containing the two parts of the input string separated by the first
        hyphen character.
    """
    # Find the index of the first hyphen character in the input string
    first_hyphen_index = string.find("-")

    # Determine which part of the string should go into the first element of the tuple
    if first_hyphen_index == -1:
        # No hyphens found, so use the whole input string as the first element
        first_part = string
    else:
        # Hyphens were found, so use the substring up to the first one as the first element
        first_part = string[:first_hyphen_index].strip()

    # Determine which part of the string should go into the second element of the tuple
    if first_hyphen_index == -1:
        # No hyphens found, so use an empty string as the second element
        second_part = ""
    else:
        # Hyphens were found, so use the substring starting after the first one as the second element
        second_part = string[first_hyphen_index + 1:].strip()

    # Construct and return the resulting tuple
    return first_part, second_part


def runner(robot_plugin, grid, cycles, data_s, base_station_pos, resources, data_r):
    """
    Runs the simulation either with a user-defined robot plugin or the default movement plugin.

    Parameters:
    robot_plugin: Callable or None
        A callable object representing the user-defined robot plugin, which takes
        three arguments (grid, resources, base_station_pos) and returns another
        callable used as a RobotPlugin inside the Simulator. If None, the default
        movement plugin will be used instead.

    grid: np.ndarray
        A two-dimensional numpy array representing the simulation grid.

    cycles: int
        Number of cycles to run the simulation.

    data_s: dict
        Dictionary containing settings related to tassel dimensions and initial positions.

    base_station_pos: list
        List of integers representing the base station position in the grid.

    resources: Resources
        An instance of class 'Resources', providing shared resources between plugins.

    data_r: dict
        Dictionary containing settings related to cutting mode and speed.
    """
    if robot_plugin:
        Simulator(
            grid,
            cycles,
            data_s["dim_tassel"],
            base_station_pos,
            robot_plugin(grid, resources, base_station_pos),
            data_r["speed"],
        ).step()
    else:
        movement, boing = split_at_first_hyphen(data_r["cutting_mode"])
        Simulator(
            grid,
            cycles,
            data_s["dim_tassel"],
            base_station_pos,
            DefaultMovementPlugin(movement, grid, resources, base_station_pos, boing),
            data_r["speed"],
        ).step()


def run_model_with_parameters(env_plugins, robot_plugin):
    """
    Run a simulation model using specified environment plugins and parameters.

    This function loads data from a file, sets up a simulator environment based on the
    loaded data, initializes resources and grids, runs the simulator through multiple
    cycles, and outputs results to CSV files. It repeats this process several times and
    applies different strategies during each iteration.

    Args:
        env_plugins (list): A dictionary mapping plugin names to their respective classes.
        robot_plugin (callable or None): A callable object representing a custom robot plugin,
            or `None` if no such plugin is desired.
    """

    # Load data from file
    data_r, data_e, data_s = load_data_from_file("../SetUp/data_file")

    repetitions = data_s["repetitions"]
    cycles = data_s["cycle"]

    for _ in range(repetitions):
        resources, grid = env_initializer(env_plugins, data_e, data_s)

        biggest_area_blocked = get_most_frequent_elements(resources, grid)

        # Random corner
        random_corner = generate_random_corner(data_e["width"], data_e["length"])

        create_csv(grid, None)

        # Add base station and guidelines
        base_station_pos = put_station_guidelines(
            strategy=PerimeterPairStrategy,
            grid=grid,
            width=data_e["width"],
            length=data_e["length"],
            resources=resources,
            random_corner_perimeter=random_corner,
            central_tassel=None,
            biggest_area_blocked=[],
        )

        runner(robot_plugin, grid, cycles, data_s, base_station_pos, resources, data_r)

        clear_non_perimeter_objects(grid)

        # Random corner
        random_corner = generate_random_corner(data_e["width"], data_e["length"])

        # Add base station and guidelines
        base_station_pos = put_station_guidelines(
            BiggestRandomPairStrategy,
            grid,
            data_e["width"],
            data_e["length"],
            resources,
            random_corner,
            None,
            biggest_area_blocked,
        )

        runner(robot_plugin, grid, cycles, data_s, base_station_pos, resources, data_r)

        clear_non_perimeter_objects(grid)

        # Random corner
        random_corner = generate_random_corner(data_e["width"], data_e["length"])

        # Central tassel
        central_tassel = find_central_tassel(grid, data_s["dim_tassel"])

        # Add base station and guidelines
        base_station_pos = put_station_guidelines(
            BiggestCenterPairStrategy,
            grid,
            data_e["width"],
            data_e["length"],
            resources,
            random_corner,
            central_tassel,
            biggest_area_blocked,
        )

        runner(robot_plugin, grid, cycles, data_s, base_station_pos, resources, data_r)
