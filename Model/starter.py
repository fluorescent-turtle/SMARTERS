import importlib
from Model.environment import begin_simulation


class Starter:
    def __init__(self, plugins):
        """
        Initializes the Starter instance.

        Args:
            plugins (list): A list of plugin names.
        """
        if plugins:
            # If plugins are provided, create a list of plugin instances
            self._plugins = []
            for plugin_name in plugins:
                # Import the plugin module dynamically
                plugin_module = importlib.import_module(plugin_name, "../Controller")
                # Get the plugin class from the imported module
                plugin_class = getattr(plugin_module, plugin_name)
                # Instantiate the plugin class and append it to the list of plugins
                self._plugins.append(plugin_class())
        else:
            # todo: raise an error
            pass

    def run(self):
        """
        Runs the lawnmowers simulation using the provided plugins.

        Returns:
            None
        """
        begin_simulation(self._plugins)  # Begin the simulation with the list of plugins
