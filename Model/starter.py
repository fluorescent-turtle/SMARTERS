import importlib

from Model.environment import begins_simulation


class Starter:
    def __init__(self, env_plugins, r_plugins):
        self.env_plugins = []
        self.robot_plugins = []

        # Loop over the environment plugins and initialize them
        if env_plugins:
            for plugin_name in env_plugins:
                try:
                    # Import the plugin module dynamically
                    plugin_module = importlib.import_module(
                        plugin_name, "../Controller"
                    )

                    # Get the plugin class from the imported module
                    plugin_class = getattr(plugin_module, plugin_name)

                    # Instantiate the plugin class and append it to the list of plugins
                    self.env_plugins.append(plugin_class())
                except ImportError as e:
                    print(f"Error importing plugin '{plugin_name}': {e}")

        # Loop over the robot plugins and initialize them
        if r_plugins:
            for plugin_name in r_plugins:
                try:
                    # Import the plugin module dynamically
                    plugin_module = importlib.import_module(
                        plugin_name, "../Controller"
                    )

                    # Get the plugin class from the imported module
                    plugin_class = getattr(plugin_module, plugin_name)

                    # Instantiate the plugin class and append it to the list of plugins
                    self.robot_plugins.append(plugin_class())
                except ImportError as e:
                    print(f"Error importing plugin '{plugin_name}': {e}")

    def run(self):
        """
        Runs the lawnmowers simulation using the provided plugins.

        Returns:
            None
        """
        begins_simulation(
            self.env_plugins, self.robot_plugins
        )  # Begin the simulation with the list of plugins
