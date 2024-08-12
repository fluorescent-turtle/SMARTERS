from abc import abstractmethod

class RandomGrid:
    def __init__(
            self,
            width,
            length,
    ):
        """
        Initialize the RandomGrid with specified width and length.

        :param width: The width of the grid.
        :type width: int
        :param length: The length of the grid.
        :type length: int
        """
        self._width = width
        self._length = length

    @abstractmethod
    def begin(self):
        """
        Abstract method to begin the process on the grid.

        Subclasses must implement this method to define the specific
        behavior when starting the grid-related operations.
        """
        pass
