import os
from datetime import datetime

import mesa
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from Model.agents import GrassTassel, Robot, SquaredBlockedArea, CircledBlockedArea


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
        Initialize the simulator for the grass-cutting simulation.

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
        self.grid = grid
        self.cycles = cycles
        self.base_station_pos = base_station_pos
        self.speed = speed
        self.dim_tassel = dim_tassel
        self.i = i
        self.j = j
        self.cycle_data = cycle_data
        self.filename = filename
        self.schedule = mesa.time.StagedActivation(self)

        self.grass_tassels = []
        self.initialize_grass_tassels()  # Place grass tassels on the grid

        self.robot = self.initialize_robot(robot_plugin, autonomy)  # Initialize the robot
        self.running = True

    def initialize_grass_tassels(self):
        """Initialize and place grass tassels in the grid."""
        for contents, (x, y) in self.grid.coord_iter():
            # Check if the current cell is not blocked or occupied
            if not any(isinstance(agent, (GrassTassel, SquaredBlockedArea, CircledBlockedArea)) for agent in contents):
                new_grass = GrassTassel((x, y))
                self.grass_tassels.append(new_grass)
                self.grid.place_agent(new_grass, (x, y))

    def initialize_robot(self, robot_plugin, autonomy):
        """
        Initialize and place the robot at the base station.

        :param robot_plugin: The robot plugin for movement and other functions.
        :param autonomy: The autonomy of the robot in terms of steps it can take before recharging.
        :return: The initialized robot instance.
        """
        robot = Robot(
            len(self.grass_tassels) + 1,
            self,
            robot_plugin,
            self.grass_tassels,
            autonomy,
            self.speed,
            2,
            self.base_station_pos,
        )
        self.grid.place_agent(robot, self.base_station_pos)
        self.schedule.add(robot)
        return robot

    def step(self):
        """Perform a single step of the simulation."""
        self.schedule.step()  # Progress the simulation schedule by one step

        cycle = 0
        while self.cycles > 0:
            while self.robot.get_autonomy() > 0:
                self.robot.step()  # Move the robot until it runs out of autonomy
            self.robot.reset_autonomy()  # Reset the robot's autonomy for the next cycle

            cycle += 1
            self.cycles -= self.robot.get_autonomy()  # Decrease the remaining cycles

            self._process_cycle_data(cycle)  # Process and save the data for the current cycle

        self.running = False  # Mark the simulation as not running

    def _process_cycle_data(self, cycle):
        """
        Process and save data collected during each cycle.

        :param cycle: The current cycle number.
        """
        # Initialize a 2D list to store grass tassel counts
        counts = [[0 for _ in range(self.grid.height)] for _ in range(self.grid.width)]

        for grass_tassel in self.grass_tassels:
            x, y = grass_tassel.get()  # Get the position of the grass tassel
            counts[x][y] = grass_tassel.get_counts()  # Store the count at the respective position

        df = self._create_cycle_dataframe(counts, cycle)  # Create a DataFrame for the cycle data
        self._save_cycle_results(df, counts, cycle)  # Save the cycle results as CSV and heatmap

    def _create_cycle_dataframe(self, counts, cycle):
        """
        Create a DataFrame with the cycle data.

        :param counts: A 2D list with the grass tassel counts.
        :param cycle: The current cycle number.
        :return: A pandas DataFrame containing the cycle data.
        """
        df = pd.DataFrame(counts).rename(
            columns={j: j * self.dim_tassel for j in range(self.grid.height)}
        )
        df.insert(0, "num_mappa", self.i)
        df.insert(1, "ripetizione", self.j)
        df.insert(2, "cycle", cycle)
        df.insert(3, "x", [i * self.dim_tassel for i in range(self.grid.width)])

        return df

    def _save_cycle_results(self, df, counts, cycle):
        """
        Save the results of the cycle as CSV and heatmap.

        :param df: The DataFrame containing the cycle data.
        :param counts: A 2D list with the grass tassel counts.
        :param cycle: The current cycle number.
        """
        output_dir = os.path.abspath("./View/")  # Define the output directory
        os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Save the DataFrame as a CSV file
        df.to_csv(os.path.join(output_dir, f"{self.filename}_cycle_{cycle}.csv"), index=False)

        # Create and save a heatmap of the counts
        self._create_and_save_heatmap(counts, cycle, output_dir)

    def _create_and_save_heatmap(self, counts, cycle, output_dir):
        """
        Create and save a heatmap for the cycle.

        :param counts: A 2D list with the grass tassel counts.
        :param cycle: The current cycle number.
        :param output_dir: The directory where the heatmap will be saved.
        """
        fig, ax = plt.subplots()
        ax.xaxis.tick_top()  # Place x-axis ticks at the top of the plot

        sns.heatmap(
            data=counts,
            annot=False,
            cmap="BuGn",
            cbar_kws={"label": "Counts"},
            robust=True,
            vmin=0,
            vmax=max(map(max, counts)),  # Determine the maximum count value for heatmap scaling
            ax=ax,
            xticklabels=self._reduce_ticks(self.grid.height, self.dim_tassel),
            yticklabels=self._reduce_ticks(self.grid.width, self.dim_tassel),
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")  # Generate a timestamp for the filename
        plt.savefig(
            os.path.join(output_dir, f"heatmap_{timestamp}_cycle_{cycle}.png"))  # Save the heatmap as a PNG file
        plt.close(fig)  # Close the figure to free memory

    @staticmethod
    def _reduce_ticks(dim, step, tick_step=10):
        """
        Reduce the number of ticks for better readability.

        :param dim: The dimension (width or height) of the grid.
        :param step: The step size for ticks.
        :param tick_step: The interval at which ticks should be shown.
        :return: A list of tick labels with reduced frequency.
        """
        ticks = [i * step for i in range(dim)]
        return [tick if i % tick_step == 0 else "" for i, tick in enumerate(ticks)]
