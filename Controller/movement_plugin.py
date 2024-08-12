from abc import abstractmethod


class MovementPlugin:
    def __init__(self, grid, pos, grid_width, grid_height):
        """
        Initialize the MovementPlugin with the grid and initial position.

        :param grid: The grid on which the movement will take place.
        :type grid: Any
        :param pos: The initial position of the agent on the grid.
        :type pos: tuple or list
        :param grid_width: The width of the grid.
        :type grid_width: int
        :param grid_height: The height of the grid.
        :type grid_height: int
        """
        self.grid = grid
        self.pos = pos

        # Calculate the width and height of the grid
        self.grid_width = grid_width
        self.grid_height = grid_height

    @abstractmethod
    def move(self, agent):
        """
        Move the character according to the rules defined by the specific subclass.

        :param agent: The Agent object representing the character being moved.
        :type agent: Agent
        """
        pass

    @abstractmethod
    def boing(self):
        """
        Make the character "boing" (bounce back) according to the rules defined by the specific subclass.
        """
        pass
