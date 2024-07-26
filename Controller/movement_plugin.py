from abc import abstractmethod


class MovementPlugin:
    def __init__(self, grid, pos, grid_width, grid_height):
        self.grid = grid
        self.pos = pos

        # Calculate the width and height of the grid
        self.grid_width = grid_width
        self.grid_height = grid_height

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
