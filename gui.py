import json
import random
import tkinter as tk
from tkinter import Tk, ttk

from model import Simulator


def begin_simulation(tassel_dim, repetitions, cycle):
    # read data from json file
    with open("../SetUp/robot_file", "r") as robot_file:
        robot_data = json.load(robot_file)
    with open("../SetUp/environment_file", "r") as environment_file:
        environment_data = json.load(environment_file)

    simulation = Simulator(
        robot_data=robot_data,
        environment_data=environment_data,
        tassel_dim=tassel_dim,
        repetitions=repetitions,
        cycle=cycle,
        position=(
            random.randint(1, int(environment_data["width"])),
            random.randint(1, int(environment_data["length"])),
        ),
        center=False,
    )
    # test_agent = TestAgent(1, simulation, [],"High")
    # simulation.schedule.add(test_agent)
    simulation.run_model()
    """for i in [1, 2]:  # needed for isolated area
        for j in [1, 2]:  # needed for isolated area

            # case: base station on the perimeter
            # begin simulation
            Simulator(
                robot_data=robot_data,
                environment_data=environment_data,
                tassel_dim=tassel_dim,
                repetitions=repetitions,
                cycle=cycle,
                position=(
                    random.randint(1, environment_data["width"]),
                    random.randint(1, environment_data["length"]),
                ),
                center=False,
            )

            # case: base station on the biggest blocked area
            # begin simulation
            Simulator(
                robot_data=robot_data,
                environment_data=environment_data,
                tassel_dim=tassel_dim,
                repetitions=repetitions,
                cycle=cycle,
                position=(-1, -1),
                center=False,
            )
            # case: base station on the biggest blocked (center)
            # begin simulation
            Simulator(
                robot_data=robot_data,
                environment_data=environment_data,
                tassel_dim=tassel_dim,
                repetitions=repetitions,
                cycle=cycle,
                position=(-1, -1),
                center=True,
            )"""


class SimulatorWindow(Tk):
    """
    Main window
    """

    def __init__(self):
        super().__init__()

        # window title
        self.title("Smarters")

        window_width = 500
        window_height = 500

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # parameters entry
        frame = ttk.Frame(self)
        frame.place(anchor="center")

        # field options
        options = {"padx": 20, "pady": 20}

        # frame label
        frame_label = ttk.Label(self, text="Simulator features", font=("Arial", 18))
        frame_label.grid(row=1, column=0, columnspan=3, **options)

        # tassel's dimension
        first_label = ttk.Label(frame, text="Dimension of the tassel (m): ")
        first_label.grid(column=0, row=2, sticky="W", **options)

        self.tassel_dim = tk.StringVar()
        self.tassel_dim.set(str(0.5))
        tassel_dim_entry = ttk.Entry(frame, textvariable=self.tassel_dim)
        tassel_dim_entry.grid(column=1, row=2, **options)
        tassel_dim_entry.focus()

        # cutting cycle time
        second_label = ttk.Label(frame, text="Cutting cycle time (h): ")
        second_label.grid(column=0, row=3, sticky="W", **options)

        self.cutting_cycle = tk.IntVar()
        cutting_cycle_entry = ttk.Entry(frame, textvariable=self.cutting_cycle)
        cutting_cycle_entry.grid(column=1, row=3, **options)
        cutting_cycle_entry.focus()

        # repetition's times
        third_label = ttk.Label(frame, text="Repetition times: ")
        third_label.grid(column=0, row=4, sticky="W", **options)

        self.repetitions = tk.IntVar()
        repetitions_entry = ttk.Entry(frame, textvariable=self.repetitions)
        repetitions_entry.grid(column=1, row=4, **options)
        repetitions_entry.focus()

        # Next button
        next_button = tk.Button(self, text="Next", command=self.click_next)
        next_button.place(x=350, y=400)

        # add padding to the frame and show it
        frame.grid(padx=20, pady=20)

    def click_next(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.destroy()

        begin_simulation(
            float(self.tassel_dim.get()),
            self.repetitions.get(),
            self.cutting_cycle.get(),
        )
