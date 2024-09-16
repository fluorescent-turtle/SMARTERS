""" Copyright 2024 Sara Grecu

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License."""

import os
from datetime import datetime

import mesa
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from Model.agents import (
    GrassTassel,
    Robot,
    SquaredBlockedArea,
    CircledBlockedArea,
)


class Simulator(mesa.Model):
    def __init__(
            self,
            grid,
            cycles,
            base_station_pos,
            robot_plugin,
            speed,
            autonomy,
            i,
            j,
            cycle_data,
            filename,
            dim_tassel,
    ):
        """
        Initialize the simulator for the grass cutting simulation.

        :param grid: The simulation grid.
        :param cycles: Number of cycles to run the simulation.
        :param base_station_pos: The position of the base station.
        :param robot_plugin: The robot plugin used for the simulation.
        :param speed: The speed of the robot.
        :param autonomy: The autonomy of the robot in terms of cycles it can run.
        :param i: The map number (identifier).
        :param j: The repetition number of the simulation run.
        :param cycle_data: Data collected during the simulation cycles.
        :param filename: The filename for saving the data.
        :param dim_tassel: The dimension of the grass tassel.
        """
        super().__init__()
        self.schedule = mesa.time.StagedActivation(self)
        self.grid = grid
        self.cycles = cycles
        self.speed = speed
        self.base_station_pos = base_station_pos
        self.grass_tassels = []
        self.robot = None
        self.dim_tassel = dim_tassel
        self.initialize_grass_tassels()
        self.initialize_robot(robot_plugin, autonomy, base_station_pos)
        self.i = i
        self.j = j

        self.running = True
        self.cycle_data = cycle_data
        self.filename = filename

    def initialize_grass_tassels(self):
        """Initialize the grass tassels and place them in the grid."""
        cord_iter = self.grid.coord_iter()
        for contents, (x, y) in cord_iter:
            if (
                    GrassTassel not in contents
                    and SquaredBlockedArea not in contents
                    and CircledBlockedArea not in contents
            ):
                # Place a new grass tassel if the cell is not blocked or already occupied by another grass tassel
                pos = (x, y)
                new_grass = GrassTassel(pos)
                self.grass_tassels.append(new_grass)
                self.grid.place_agent(new_grass, pos)

    def initialize_robot(self, robot_plugin, autonomy, base_station_pos):
        """
        Initialize the robot and place it at the base station.

        :param robot_plugin: The robot plugin for movement and other functions.
        :param autonomy: The autonomy of the robot in terms of steps it can take before recharging.
        :param base_station_pos: The position of the base station where the robot starts.
        """
        if self.cycles < autonomy:
            # Create the robot with all necessary attributes
            self.robot = Robot(
                len(self.grass_tassels) + 1,
                self,
                robot_plugin,
                self.grass_tassels,
                self.cycles,
                self.speed,
                2,
                base_station_pos,
            )
        else:
            # Create the robot with all necessary attributes
            self.robot = Robot(
                len(self.grass_tassels) + 1,
                self,
                robot_plugin,
                self.grass_tassels,
                autonomy,
                self.speed,
                2,
                base_station_pos,
            )
        print(f"self.cycles {self.cycles} -- autonomy: {autonomy}")
        # Place the robot at the base station and add it to the schedule
        self.grid.place_agent(self.robot, self.base_station_pos)
        self.schedule.add(self.robot)

    def step(self):
        """Perform a single step of the simulation."""
        self.schedule.step()  # Progress the simulation schedule by one step
        cycle = 0

        # Main simulation loop
        while self.cycles > 0:
            while self.robot.get_autonomy() > 0:
                self.robot.step()  # Move the robot until it runs out of autonomy
            self.robot.reset_autonomy()  # Reset the robot's autonomy for the next cycle
            self.cycles -= self.robot.autonomy  # Decrease the remaining cycles
            cycle += 1
            self._process_cycle_data(cycle)  # Process the data for the current cycle

        self.running = False  # Mark the simulation as not running

    def _process_cycle_data(self, cycle):
        """
        Process the data collected during each cycle and save it.

        :param cycle: The current cycle number.
        """
        counts = [[0 for _ in range(self.grid.height)] for _ in range(self.grid.width)]

        for grass_tassel in self.grass_tassels:
            x, y = grass_tassel.get()
            if grass_tassel.get_counts() > 0:
                counts[x][y] = grass_tassel.get_counts()

        # Create a DataFrame to store the counts
        df = pd.DataFrame(counts)
        df = df.rename(
            columns={j: j * self.dim_tassel for j in range(self.grid.height)}
        )
        df.insert(loc=0, column="num_mappa", value=self.i)
        df.insert(loc=1, column="ripetizione", value=self.j)
        df.insert(loc=2, column="cycle", value=cycle)
        df.insert(
            loc=3,
            column="x",
            value=[i * self.dim_tassel for i in range(self.grid.width)],
        )

        output_dir = os.path.abspath("./View/")  # Define the output directory

        def reduce_ticks(ticks, step):
            return [tick if i % step == 0 else "" for i, tick in enumerate(ticks)]

        # Generate ticks for x and y axes
        xtick = [int(j * self.dim_tassel) for j in range(self.grid.height)]
        ytick = [int(i * self.dim_tassel) for i in range(self.grid.width)]

        tick_step = 35  # Define the step for tick reduction
        reduced_xtick = reduce_ticks(xtick, tick_step)
        reduced_ytick = reduce_ticks(ytick, tick_step)

        # Create a heatmap of the counts
        fig, ax = plt.subplots()
        ax.xaxis.tick_top()  # Place x-axis ticks at the top
        maximum = max(max(sublist) for sublist in counts)

        sns.heatmap(
            data=counts,
            annot=False,
            cmap="BuGn",
            cbar_kws={"label": "Counts"},
            robust=True,
            vmin=0,
            vmax=maximum,
            ax=ax,
            xticklabels=reduced_xtick,
            yticklabels=reduced_ytick,
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H:%M:%S"
        )  # Generate a timestamp for the filename
        file_path = os.path.join(
            output_dir, f"heatmap_{timestamp}_cycle_{cycle}.png"
        )  # Define the file path

        plt.savefig(file_path)  # Save the heatmap as a PNG file
        plt.close(fig)  # Close the figure

        fig, ax = plt.subplots()

        flattened_counts = np.array(counts).flatten()

        # Create histogram plot directly from the flattened array
        bins = np.linspace(min(flattened_counts), max(flattened_counts), 20)
        sns.histplot(flattened_counts, bins=bins, discrete=True, edgecolor='black')

        plt.xscale('linear')
        plt.yscale('symlog')

        # Set x-axis label
        plt.xlabel("Tassel Value")

        # Set y-axis label
        plt.ylabel("Frequency")

        # Adjust layout to prevent overlapping labels
        plt.tight_layout()

        # Save plot as PNG file
        plt.savefig(os.path.join(output_dir, f"hist_{timestamp}_cycle_{cycle}.png"))

        # Close figure
        plt.close(fig)

        # Save the DataFrame as a CSV file
        df.to_csv(
            os.path.join(output_dir, f"{self.filename}_cycle_{cycle}.csv"), index=False
        )
