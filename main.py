import sys

from Model.starter import Starter


def parse_cli(argv):
    """Parses the command line arguments for the main script.

    Args:
      argv: The list of command line arguments.

    Returns:
      A dictionary of parsed arguments.
    """

    # Get the arguments following the script name.
    args = argv[1:]

    # Parse the arguments.
    parsed_args = {}
    e_plugins = {}
    r_plugins = {}

    for arg in args:
        if arg.startswith("--"):
            key, value = arg.split("--")
            parsed_args[key] = value

            if key == "e":
                e_plugins[value] = True
            elif key == "r":
                r_plugins[value] = True

    # Return the parsed arguments.
    return e_plugins, r_plugins


if __name__ == "__main__":
    env_plugins, robot_plugins = parse_cli(sys.argv)

    # Use command-line arguments as plugin names
    simulator = Starter(env_plugins, robot_plugins)
    simulator.run()
