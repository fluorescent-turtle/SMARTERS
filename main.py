import sys

from Model.starter import Starter


def parse_cli(argv):
    """Parses the command line arguments for the main script.

    Args:
      argv: The list of command line arguments.

    Returns:
      A dictionary of parsed arguments.
    """
    args = argv[1:]  # Skip the script name
    r_plugins = []
    e_plugins = []
    filen = None

    current_flag = None

    for arg in args:
        if arg.startswith("--"):
            # Set current flag if we encounter a new flag
            if arg == "--r":
                current_flag = 'r_plugins'
            elif arg == "--e":
                current_flag = 'e_plugins'
            elif arg == "--d":
                current_flag = 'data_file'
            else:
                raise ValueError(f"Unknown argument: {arg}")
        else:
            # Add value to the current flag
            if current_flag == 'r_plugins':
                r_plugins.append(arg)
            elif current_flag == 'e_plugins':
                e_plugins.append(arg)
            elif current_flag == 'data_file':
                if filen is not None:
                    raise ValueError(f"Multiple data files specified: {filen} and {arg}")
                filen = arg
            else:
                raise ValueError(f"Unexpected value without a flag: {arg}")

    return e_plugins, r_plugins, filen


if __name__ == "__main__":
    env_plugins, robot_plugins, filename = parse_cli(sys.argv)

    # Use command-line arguments as plugin names
    simulator = Starter(env_plugins, robot_plugins, filename)
    simulator.run()
