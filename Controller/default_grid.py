""" Copyright 2024 Sara Grecu

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License."""

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
