from abc import abstractmethod


class RandomGrid:
    def __init__(
            self,
            width,
            length,
    ):
        self._width = width
        self._length = length

    @abstractmethod
    def begin(self):
        pass
