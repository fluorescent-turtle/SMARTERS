"""
This script defines functionalities for simulating a scenario using tkinter.
"""

import json
import random
import tkinter as tk
from tkinter import Tk, ttk

from model import Simulator


def begin_simulation(tassel_dim, repetitions, cycle):
    """
    Begin the simulation with the specified parameters.

    Parameters:
        tassel_dim (float): The dimension of the tassel in meters.
        repetitions (int): The number of repetitions.
        cycle (int): The cutting cycle time in hours.
    """
    # Read data from JSON files
    with open("../SetUp/robot_file", "r") as robot_file:
        robot_data = json.load(robot_file)
    with open("../SetUp/environment_file", "r") as environment_file:
        environment_data = json.load(environment_file)

    # Start the simulation
    simulation = Simulator(
        robot_data=robot_data,
        environment_data=environment_data,
        tassel_dim=tassel_dim,
        repetitions=repetitions,
        cycle=cycle,
    )
    simulation.run_model()


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
