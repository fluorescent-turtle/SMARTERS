import importlib
from Model.environment import begin_simulation


class LawnmowersSimulator:
    def __init__(self, plugins, module_dir):
        """
        Initializes the LawnmowersSimulator instance.

        Args:
            plugins (list): A list of plugin names.
            module_dir (str): The directory path where the plugin modules are located.
        """
        if plugins:
            # If plugins are provided, create a list of plugin instances
            self._plugins = []
            for plugin_name in plugins:
                # Import the plugin module dynamically
                plugin_module = importlib.import_module(plugin_name, module_dir)
                # Get the plugin class from the imported module
                plugin_class = getattr(plugin_module, plugin_name)
                # Instantiate the plugin class and append it to the list of plugins
                self._plugins.append(plugin_class())
        else:
            # If no plugins were provided, use the default plugin
            default_module = importlib.import_module("default", module_dir)
            default_plugin = getattr(default_module, "Plugin")
            self._plugins = [default_plugin()]

    def run(self):
        """
        Runs the lawnmowers simulation using the provided plugins.

        Returns:
            None
        """
        begin_simulation(self._plugins)  # Begin the simulation with the list of plugins
