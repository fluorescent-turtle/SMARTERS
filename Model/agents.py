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

from mesa import Agent


class Robot(Agent):
    """
    A Robot agent that interacts with the environment.

    :param unique_id: Unique identifier for the agent.
    :type unique_id: int
    :param model: The model object that the agent belongs to.
    :type model: Model
    :param robot_plugin: The robot plugin used for movement.
    :type robot_plugin: MovementPlugin
    :param autonomy: Autonomy level of the robot.
    :type autonomy: int
    :param speed: Speed of the robot.
    :type speed: float
    :param shear_load: The shear load capacity of the robot.
    :type shear_load: float
    :param base_station: The base station object where the robot can recharge.
    :type base_station: BaseStation
    """

    def __init__(
            self,
            unique_id,
            model,
            robot_plugin,
            grass_tassels,
            autonomy,
            speed,
            shear_load,
            base_station,
    ):
        super().__init__(unique_id, model)

        self.robot_plugin = robot_plugin  # Plugin used for movement
        self.grass_tassels = grass_tassels  # Number of grass tassels to collect
        self.autonomy = autonomy  # Autonomy level of the robot

        self.base_station = base_station
        self.speed = speed  # Speed of the robot
        self.shear_load = shear_load

        self.visited_positions = []
        self.aux_autonomy = autonomy

        self.first = True
        self.dir = None
        self.dx = None

        self.end = False
        self.path_taken = set()

    def step(self):
        """
        Move the robot using the robot plugin.
        """
        self.robot_plugin.move(self)

    def get_gt(self):
        """
        Get the number of grass tassels to collect.

        :return: Number of grass tassels.
        :rtype: int
        """
        return self.grass_tassels

    def decrease_autonomy(self, param):
        """
        Decrease the autonomy level of the robot.

        :param param: Amount to decrease the autonomy.
        :type param: int
        """
        self.aux_autonomy -= param

    def get_autonomy(self):
        """
        Get the current autonomy level of the robot.

        :return: Current autonomy level.
        :rtype: int
        """
        return self.aux_autonomy

    def reset_autonomy(self):
        """
        Reset the autonomy level of the robot to its initial value.
        """
        self.aux_autonomy = self.autonomy

    def not_first(self):
        """
        Indicate that this is not the first step.
        """
        self.first = False

    def get_first(self):
        """
        Check if this is the first step.

        :return: True if it is the first step, False otherwise.
        :rtype: bool
        """
        return self.first


class GrassTassel:
    """
    A GrassTassel agent that represents a single grass tassel.

    :param pos: Position of the grass tassel.
    """

    def __init__(self, pos):
        self.cut = -1  # Number of times the grass tassel has been cut
        self.pos = pos  # Position of the grass tassel

    def increment(self):
        """
        Increment the cut count.
        """
        if self.cut == -1:
            self.cut = 1
        else:
            self.cut += 1

    def get_counts(self):
        """
        Get the number of times the grass tassel has been cut.

        :return: Cut count.
        :rtype: int
        """
        return self.cut

    def get(self):
        """
        Get the position of the grass tassel.

        :return: Position of the grass tassel.
        :rtype: tuple or list
        """
        return self.pos

    def clear(self):
        """
        Clear the position of the grass tassel.
        """
        self.pos = None


class IsolatedArea:
    """
    Represents an isolated area.

    :param pos: Position of the isolated area.
    :type pos: tuple or list
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the isolated area.

        :return: Position of the isolated area.
        :rtype: tuple or list
        """
        return self.pos


class Opening:
    """
    Represents an opening in the environment.

    :param pos: Position of the opening.
    :type pos: tuple or list
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the opening.

        :return: Position of the opening.
        :rtype: tuple or list
        """
        return self.pos


class BaseStation:
    """
    Represents a base station where robots can recharge.

    :param pos: Position of the base station.
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the base station.

        :return: Position of the base station.
        :rtype: tuple or list
        """
        return self.pos

    def clear(self):
        """
        Clear the position of the base station.
        """
        self.pos = None


class SquaredBlockedArea:
    """
    Represents a squared blocked area.

    :param pos: Position of the blocked area.
    :type pos: tuple or list
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the blocked area.

        :return: Position of the blocked area.
        :rtype: tuple or list
        """
        return self.pos


class CircledBlockedArea:
    """
    Represents a circular blocked area.

    :param pos: Center position of the circle.
    :type pos: tuple or list
    """

    def __init__(self, pos):
        self.pos = pos


class GuideLine:
    """
    Represents a guideline for robots to follow.

    :param pos: Position of the guideline.
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the guideline.

        :return: Position of the guideline.
        :rtype: tuple or list
        """
        return self.pos

    def clear(self):
        """
        Clear the position of the guideline.
        """
        self.pos = None
