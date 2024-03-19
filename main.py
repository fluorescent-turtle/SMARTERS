import sys

from Model.starter import Starter

if __name__ == "__main__":

    if len(sys.argv) > 1:
        # Use command-line arguments as plugin names
        simulator = Starter(sys.argv)
        simulator.run()
