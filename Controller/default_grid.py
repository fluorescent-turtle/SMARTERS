from abc import abstractmethod


class RandomGrid:
    """
    Generate a default random grid according to user input parameters.

    This class generates a random grid based on various inputs such as the desired
    dimension sizes, shapes, obstacles, etc. Once instantiated, you can call its `begin` method
    which initializes the internal state of the object and produces the final grid layout.

    Attributes:
        _width (int): The width of the generated grid.
        _length (int): The length of the generated grid.
        _grid (List[List[Any]]): Final grid representation after generation.

    Methods:
        begin(): Initializes the grid generation process and returns relevant details.
    """

    def __init__(
            self,
            width,
            length,
            grid,
    ):
        """
        Initialize attributes needed to create a new instance of the DefaultRandomGrid class.

        Args:
            width (int): Grid width.
            length (int): Grid length.
            grid (List[List[Any]]): Empty grid structure.
        """
        self._width = width
        self._length = length

        self._grid = grid

    @abstractmethod
    def begin(self):
        pass
