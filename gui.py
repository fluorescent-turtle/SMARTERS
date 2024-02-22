import itertools
import json
import tkinter as tk
from tkinter import ttk, Tk
from mesa.space import SingleGrid
from model import Simulator
from utils import (
    initialize_isolated_area,
    populate_blocked_areas,
    populate_perimeter_guidelines,
    add_base_station,
    generate_pair,
    find_largest_blocked_area,
)


def create_random_grid(environment_data, tassel_dim):
    """
    Create a random grid based on environment data and tassel dimensions.

    Args:
        environment_data (dict): Data related to the environment.
        tassel_dim (float): The dimension of the tassel in meters.

    Returns:
        SingleGrid: The generated grid.
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
    isolated_area_tassels = []

    # Initialize model components
    grid = SingleGrid(int(width), int(length), torus=False)
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
    populate_blocked_areas(resources, num_blocked_squares, num_blocked_circles, grid, min_width_blocked,
                           max_width_blocked, min_height_blocked, max_height_blocked)

    populate_perimeter_guidelines(int(width), int(length), grid, resources)

    return grid, resources


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


def begin_simulation(tassel_dim, repetitions, cycle):
    """
    Begin the simulation with the specified parameters.

    Args:
        tassel_dim (float): The dimension of the tassel in meters.
        repetitions (int): The number of repetitions.
        cycle (int): The cutting cycle time in hours.
    """
    # Read data from JSON files
    with open("../SetUp/robot_file", "r") as robot_file:
        robot_data = json.load(robot_file)
    with open("../SetUp/environment_file", "r") as environment_file:
        environment_data = json.load(environment_file)

    grid, resources = create_random_grid(environment_data, tassel_dim)
    base_station = generate_pair(environment_data["width"], environment_data["length"])

    # Add base station to the perimeter
    add_base_station(
        grid,
        base_station,
        resources,
    )

    # Add guidelines on the grid

    run_model_with_parameters(robot_data, grid, resources, repetitions, cycle)

    # Add base station to the biggest blocked area randomly
    biggest_area, coords = find_largest_blocked_area(grid)
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


class SimulatorWindow(Tk):
    """
    Main window for the simulator application.
    """

    def __init__(self):
        """
        Initialize the main window.
        """
        super().__init__()

        # Set window title
        self.title("Smarters")

        window_width = 500
        window_height = 500

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate center position
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # Set window position to the center of the screen
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # Create parameters entry frame
        frame = ttk.Frame(self)
        frame.place(anchor="center")

        # Define options for fields
        options = {"padx": 20, "pady": 20}

        # Add frame label
        frame_label = ttk.Label(self, text="Simulator features", font=("Arial", 18))
        frame_label.grid(row=1, column=0, columnspan=3, **options)

        # Add tassel's dimension entry
        first_label = ttk.Label(frame, text="Dimension of the tassel (m): ")
        first_label.grid(column=0, row=2, sticky="W", **options)

        self.tassel_dim = tk.StringVar()
        self.tassel_dim.set(str(0.5))
        tassel_dim_entry = ttk.Entry(frame, textvariable=self.tassel_dim)
        tassel_dim_entry.grid(column=1, row=2, **options)
        tassel_dim_entry.focus()

        # Add cutting cycle time entry
        second_label = ttk.Label(frame, text="Cutting cycle time (h): ")
        second_label.grid(column=0, row=3, sticky="W", **options)

        self.cutting_cycle = tk.IntVar()
        cutting_cycle_entry = ttk.Entry(frame, textvariable=self.cutting_cycle)
        cutting_cycle_entry.grid(column=1, row=3, **options)
        cutting_cycle_entry.focus()

        # Add repetition's times entry
        third_label = ttk.Label(frame, text="Repetition times: ")
        third_label.grid(column=0, row=4, sticky="W", **options)

        self.repetitions = tk.IntVar()
        repetitions_entry = ttk.Entry(frame, textvariable=self.repetitions)
        repetitions_entry.grid(column=1, row=4, **options)
        repetitions_entry.focus()

        # Add Next button
        next_button = tk.Button(self, text="Next", command=self.click_next)
        next_button.place(x=350, y=400)

        # Add padding to the frame and show it
        frame.grid(padx=20, pady=20)

    def click_next(self):
        """
        Proceed to the next step in the simulation.
        """
        for widget in self.winfo_children():
            widget.destroy()
        self.destroy()

        begin_simulation(
            float(self.tassel_dim.get()),
            self.repetitions.get(),
            self.cutting_cycle.get(),
        )
