from mesa import Agent


class Robot(Agent):
    """
    A Robot agent that interacts with the environment.

    :param unique_id: Unique identifier for the agent.
    :param model: The model object.
    :param robot_plugin: The robot plugin used for movement.
    :param grass_tassels: Number of grass tassels to collect.
    :param autonomy: Autonomy level of the robot.
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
        return self.grass_tassels

    def decrease_autonomy(self, param):
        """
        Decrease the autonomy level of the robot.

        :param param: Amount to decrease the autonomy.
        """

        self.aux_autonomy -= param

    def get_autonomy(self):
        return self.aux_autonomy

    def reset_autonomy(self):
        self.aux_autonomy = self.autonomy

    def not_first(self):
        self.first = False

    def get_first(self):
        return self.first


# todo: grass tassel in plugin
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
        """
        return self.cut

    def get(self):
        """
        Get the position of the grass tassel.

        :return: Position of the grass tassel.
        """
        return self.pos

    def clear(self):
        self.pos = None


class IsolatedArea:
    """
    Represents an isolated area.

    :param pos: Position of the isolated area.
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the isolated area.

        :return: Position of the isolated area.
        """
        return self.pos


class Opening:
    """
    Represents an opening in the environment.

    :param pos: Position of the opening.
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the opening.

        :return: Position of the opening.
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
        """
        return self.pos

    def clear(self):
        self.pos = None


class SquaredBlockedArea:
    """
    Represents a squared blocked area.

    :param pos: Position of the blocked area.
    """

    def __init__(self, pos):
        self.pos = pos

    def get(self):
        """
        Get the position of the blocked area.

        :return: Position of the blocked area.
        """
        return self.pos


class CircledBlockedArea:
    """
    Represents a circular blocked area.

    :param pos: Center position of the circle.
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
        """
        return self.pos

    def clear(self):
        self.pos = None
