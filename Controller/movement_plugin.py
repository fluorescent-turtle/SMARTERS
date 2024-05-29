from abc import abstractmethod


class MovementPlugin:
    """A base class for plugins that handle character movement."""

    def __init__(self, grid, resources: list, pos):
        """Initialize the MovementPlugin object.

        Args:
            grid (Grid): The Grid object representing the game board.
            resources (list): A list of Resources objects.
            pos (tuple): The starting position of the character on the grid.
        """
        self.grid = grid
        self.resources = resources
        self.pos = pos
        # Define possible directions of movement
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        # Initialize the current direction index
        self.current_direction_index = 0
        # Initialize the number of steps taken in the same direction
        self.steps_in_same_direction = 0
        # Calculate the width and height of the grid
        self.grid_width = grid.width - 1
        self.grid_height = grid.height - 1

    @abstractmethod
    def move(self, agent):
        """Move the character according to the rules defined by the specific subclass.

        Args:
            agent (Agent): The Agent object representing the character being moved.
        """
        pass

    @abstractmethod
    def boing(self):
        """Make the character "boing" (bounce back) according to the rules defined by the specific subclass."""
        pass
