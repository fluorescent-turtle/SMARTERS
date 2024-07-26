import copy
import importlib
import logging
import math
import os
from datetime import datetime

import pandas as pd
from mesa.space import MultiGrid

from Controller.environment_plugin import DefaultRandomGrid, DefaultCreatedGrid
from Controller.robot_plugin import DefaultMovementPlugin
from Model.model import Simulator
from Utils.utils import (
    put_station_guidelines,
    load_data_from_file,
    find_central_tassel,
    BiggestCenterPairStrategy,
    BiggestRandomPairStrategy,
    PerimeterPairStrategy,
    populate_perimeter_guidelines,
)


def _initialize_plugins(plugins):
    """
    Import and instantiate plugins.

    Args:
        plugins (list): List of plugin names.

    Returns:
        list: List of initialized plugin instances.
    """
    plugin_cache = {}
    initialized_plugins = []

    for plugin_name in plugins:
        if plugin_name not in plugin_cache:
            try:
                # Dynamically import the plugin module and class
                plugin_module = importlib.import_module(f"Controller.{plugin_name}")
                plugin_class = getattr(plugin_module, plugin_name)
                plugin_cache[plugin_name] = plugin_class
            except ImportError as e:
                logging.error(f"Error importing plugin '{plugin_name}': {e}")
                continue
        initialized_plugins.append(plugin_cache[plugin_name]())

    return initialized_plugins


class Starter:
    def __init__(self, env_plugins, r_plugins):
        self.env_plugins = _initialize_plugins(env_plugins)
        self.r_plugins = _initialize_plugins(r_plugins)

    def run(self):
        """
        Run the model with initialized plugins.
        """
        run_model_with_parameters(
            self.env_plugins, self.r_plugins[0] if self.r_plugins else None
        )


def execute_plugins(env_plugins, grid_width, grid_height):
    """
    Execute environment plugins on the grid.

    Args:
        env_plugins (list): Environment plugins to execute.
        grid_width (int): Width of the grid.
        grid_height (int): Height of the grid.

    Returns:
        tuple: Grid, resources, and corner after plugin execution.
    """
    corner = None, None
    grid = None
    for plugin in env_plugins:
        try:
            # Execute the plugin on the grid
            grid, corner = plugin(grid_width, grid_height).begin()
        except Exception as e:
            logging.error(f"Error in environment plugin: {e}")
    return grid, corner


def create_grid(grid_type, data_e, grid_width, grid_height, dim_tassel, env_plugins):
    """
    Create a grid using the provided parameters.

    Args:
        grid_type (str): Type of grid to create ('default' or 'random').
        data_e (dict): Data for environment setup.
        grid_width (int): Width of the grid.
        grid_height (int): Height of the grid.
        dim_tassel (int): Dimension of the tassel.
        env_plugins

    Returns:
        MultiGrid: The created grid or None if an error occurs.
    """
    if grid_type == "default":
        raw_shapes = data_e["circles"] + data_e["squares"] + data_e["isolated_area"]
        return DefaultCreatedGrid(
            grid_width=grid_width,
            grid_height=grid_height,
            data_e=data_e,
            raw_shapes=raw_shapes,
            dim_tassel=dim_tassel,
        ).begin()

    elif grid_type == "random":
        required_keys = [
            "min_width_square",
            "max_width_square",
            "min_height_square",
            "max_height_square",
            "min_ray",
            "max_ray",
            "isolated_area_min_length",
            "isolated_area_max_length",
            "min_radius",
            "max_radius",
            "isolated_area_min_width",
            "isolated_area_max_width",
            "num_blocked_squares",
            "num_blocked_circles",
        ]

        params = {key: int(data_e[key]) for key in required_keys if key in data_e}

        params.update(
            {
                "isolated_shape": data_e.get("isolated_area_shape"),
                "dim_tassel": dim_tassel,
            }
        )

        return DefaultRandomGrid(grid_width, grid_height, **params).begin()

    else:
        if env_plugins:
            return execute_plugins(env_plugins, grid_width, grid_height)


def split_at_first_hyphen(string):
    """
    Split a string at the first hyphen.

    Args:
        string (str): The input string to split.

    Returns:
        tuple: A tuple containing the part before the first hyphen and the part after the hyphen.
    """
    first_hyphen_index = string.find("-")
    if first_hyphen_index == -1:
        return string, ""
    return string[:first_hyphen_index].strip(), string[first_hyphen_index + 1:].strip()


def process_grid_data(grid_height, grid_width, i, j, filename, dim_tassel, grid):
    """
    Process the grid data and save it to a CSV file.

    Args:
        grid_height (int): Height of the grid.
        grid_width (int): Width of the grid.
        i (int): Index of the current map.
        j (int): Index of the current repetition.
        filename (str): Filename for saving the grid data.
        dim_tassel (int): Dimension of the tassel.
        grid (MultiGrid): The grid to process.

    """
    external_data = [["Empty" for i in range(grid_width)] for j in range(grid_height)]
    for x in range(grid_height):
        for y in range(grid_width):
            external_data[x][y] = grid.get_cell_list_contents([(x, y)])

    output_dir = os.path.abspath("./View/")
    path = os.path.join(output_dir, filename)
    df = pd.DataFrame(external_data)
    df = df.rename(columns={j: j * dim_tassel for j in range(grid_width)})
    df.insert(loc=0, column="num_mappa", value=i)
    df.insert(loc=1, column="ripetizione", value=j)
    df.insert(loc=2, column="x", value=[dim_tassel * i for i in range(grid_height)])

    df.to_csv(path, index=False)


def get_current_datetime():
    """
    Get the current date and time as a formatted string.

    Returns:
        str: The current date and time in the format "YYYY-MM-DD HH:MM:SS".
    """
    now = datetime.now()
    current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return current_date_time


def runner(
        robot_plugin,
        grid,
        cycles,
        base_station_pos,
        data_r,
        grid_width,
        grid_height,
        i,
        j,
        cycle_data,
        filename,
        created,
        dim_tassel,
):
    movement_type, boing = split_at_first_hyphen(data_r["cutting_mode"])

    plugin = (
        robot_plugin(grid, base_station_pos)
        if robot_plugin
        else DefaultMovementPlugin(
            movement_type=movement_type,
            grid=grid,
            base_station_pos=base_station_pos,
            boing=boing,
            cut_diameter=data_r["cutting_diameter"],
            grid_width=grid_width,
            grid_height=grid_height,
            dim_tassel=dim_tassel,
        )
    )

    # Process the grid data and save it to a CSV file
    process_grid_data(grid_height, grid_width, i, j, filename, dim_tassel, grid)

    current_data = []
    Simulator(grid, cycles, base_station_pos, plugin, data_r["speed"], data_r["autonomy"] - (data_r["autonomy"] / 10),
              i, j, current_data, filename, dim_tassel, created).step()
    cycle_data.append(current_data)


def run_model_with_parameters(env_plugins, robot_plugin):
    """
    Run the model with the given environment and robot plugins.

    Args:
        env_plugins (list): List of environment plugins.
        robot_plugin (callable): Robot plugin to execute.
    """
    # Load setup data from the file
    data_r, data_e, data_s = load_data_from_file("../SetUp/data_file")
    repetitions = data_s["repetitions"]
    num_maps = data_s["num_maps"]

    cycles = data_s["cycle"] * 3600
    dim_tassel = data_s["dim_tassel"]
    created = False
    grid_width = math.ceil(data_e["width"] / dim_tassel) + 1
    grid_height = math.ceil(data_e["length"] / dim_tassel) + 1

    """if data_e["circles"] is None:
    else:
        grid_width = math.ceil(data_e["width"])
        grid_height = math.ceil(data_e["length"])
        print(f"GRID WIDTH {grid_width} -- {grid_height}")
        create = True"""

    for i in range(num_maps):
        cycle_data = []
        if (not data_e["circles"] is None) and not created:
            grid, random_corner, biggest_area_blocked = create_grid(
                "default", data_e, grid_width, grid_height, dim_tassel, env_plugins
            )
            created = True
        else:
            grid, random_corner, biggest_area_blocked = create_grid(
                "random", data_e, grid_width, grid_height, dim_tassel, env_plugins
            )

        # Process the grid data and save it
        process_grid_data(
            grid_height,
            grid_width,
            i,
            0,
            f"grid{get_current_datetime()}.csv",
            dim_tassel,
            grid,
        )

        # Populate perimeter guidelines in the grid
        populate_perimeter_guidelines(grid_width, grid_height, grid, dim_tassel)

        # Create deep copies of the grid for different strategies
        grid1 = copy.deepcopy(grid)
        grid2 = copy.deepcopy(grid)
        grid3 = copy.deepcopy(grid)

        for j in range(repetitions):
            # Place the base station using the perimeter pair strategy
            base_station_pos = put_station_guidelines(
                PerimeterPairStrategy,
                grid1,
                grid_width,
                grid_height,

                random_corner,
                None,
                biggest_area_blocked,
            )

            if base_station_pos is not None:
                runner(
                    robot_plugin=robot_plugin,
                    grid=grid1,
                    cycles=cycles,
                    base_station_pos=base_station_pos,
                    data_r=data_r,
                    grid_width=grid_width,
                    grid_height=grid_height,
                    i=i,
                    j=j,
                    cycle_data=cycle_data,
                    filename=f"perimeter_model{get_current_datetime()}.csv",
                    dim_tassel=dim_tassel,
                    created=created
                )

            if biggest_area_blocked:
                # Place the base station using the biggest random pair strategy
                base_station_pos = put_station_guidelines(
                    BiggestRandomPairStrategy,
                    grid2,
                    grid_width,
                    grid_height,
                    random_corner,
                    None,
                    biggest_area_blocked,
                )

                if base_station_pos is not None:
                    runner(
                        robot_plugin,
                        grid2,
                        cycles,
                        base_station_pos,
                        data_r,
                        grid_width,
                        grid_height,
                        i,
                        j,
                        cycle_data,
                        f"big_model{get_current_datetime()}.csv",
                        created,
                        dim_tassel,
                    )

                # Find the central tassel position
                central_tassel = find_central_tassel(grid_width, grid_height)

                # Place the base station using the biggest center pair strategy
                base_station_pos = put_station_guidelines(
                    BiggestCenterPairStrategy,
                    grid3,
                    grid_width,
                    grid_height,
                    random_corner,
                    central_tassel,
                    biggest_area_blocked,
                )

                if base_station_pos is not None:
                    runner(
                        robot_plugin,
                        grid3,
                        cycles,
                        base_station_pos,
                        data_r,
                        grid_width,
                        grid_height,
                        i,
                        j,
                        cycle_data,
                        f"bigcenter_model{get_current_datetime()}.csv",
                        created,
                        dim_tassel,
                    )
