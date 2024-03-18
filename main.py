"""
This script simulates lawnmowers using the LawnmowersSimulator class.

Args:
    None

Returns:
    None

Usage:
    This script should be run from the command line. It takes no arguments.
    Example usage:
        python script_name.py
"""

import sys  # Importing the sys module to access command-line arguments

from Model.LawnmowersSimulator import LawnmowersSimulator  # Importing the LawnmowersSimulator class

args = sys.argv  # Getting command-line arguments

if __name__ == "__main__":
    # Determining if command-line arguments were provided and passing them to the simulator, otherwise None
    plugin_args = args if args else None
    last_arg = args.pop()
    simulator = LawnmowersSimulator(plugin_args.remove(last_arg), last_arg)
    simulator.run()  # Running the simulation
