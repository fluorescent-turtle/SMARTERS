from mesa import Agent


class Robot(Agent):
    def __init__(self, unique_id, model, robot_plugin, grass_tassels):
        """
        Initialize a new Robot agent.

        Args:
            unique_id (int): Unique identifier for the agent.
            model: Reference to the model.
        """
        super().__init__(unique_id, model)

        self.robot_plugin = robot_plugin
        self.grass_tassels = grass_tassels

    def step(self):
        """
        Execute a step in the agent's behavior.
        """

        self.robot_plugin.move(self)


class GrassTassel(Agent):
    """
    An agent representing a tassel of grass.

    Attributes:
        state: State of the grass tassel.
    """

    def __init__(self, unique_id, pos, model):
        """
        Initialize a new GrassTassel agent.

        Args:
            unique_id: Unique identifier for the agent.
            model: Reference to the model.
            state: State of the grass tassel.
        """
        super().__init__(unique_id, model)
        self.cut = 0
        self.pos = pos

    def increment(self):
        self.cut += 1

    def get_counts(self):
        return self.cut

    def get(self):
        return self.pos


class CircularIsolation:
    """
    Represents a circular isolated area.
    """

    def __init__(self, pos, radius):
        """
        Initialize a new CircularIsolation object.

        Args:
            pos (tuple): Position of the center of the isolated area (x, y).
            radius (int): Radius of the isolated area.
        """
        self.pos = pos
        self.radius = radius

    def get(self):
        return None


class IsolatedArea:
    """
    Represents an isolated area.
    """

    def __init__(self, pos):
        """
        Initialize a new IsolatedArea object.

        Args:
            pos (tuple): Position of the isolated area (x, y).
        """
        self.pos = pos

    def get(self):
        return None


class Opening:
    """
    Represents an opening in an enclosure.
    """

    def __init__(self, pos):
        """
        Initialize a new Opening object.

        Args:
            pos (tuple): Position of the opening (x, y).
        """
        self.pos = pos

    def get(self):
        return None


class EnclosureTassel:
    """
    Represents a tassel in an enclosure.
    """

    def __init__(self, unique_id):
        """
        Initialize a new EnclosureTassel object.

        Args:
            unique_id (int): Unique identifier for the tassel.
        """
        self.unique_id = unique_id

    def get(self):
        return None


class BaseStation:
    """
    Represents a base station.
    """

    def __init__(self, pos):
        """
        Initialize a new BaseStation object.

        Args:
            pos (tuple): Position of the base station (x, y).
        """
        self.pos = pos

    def clear(self):
        self.pos = None

    def get(self):
        return None


class SquaredBlockedArea:
    """
    Represents a squared blocked area.
    """

    def __init__(self, pos, label):
        """
        Initialize a new SquaredBlockedArea object.

        Args:
            pos (tuple): Position of the blocked area (x, y).
            label (label): Label
        """
        self.pos = pos
        self.label = label

    def get(self):
        return self.label

    def get_pos(self):
        return self.pos


class CircledBlockedArea:
    """
    Represents a circled blocked area.
    """

    def __init__(self, pos, radius, label):
        """
        Initialize a new CircledBlockedArea object.

        Args:
            pos (tuple): Position of the center of the blocked area (x, y).
            radius (int): Radius of the blocked area.
            label (int): Label of the blocked area
        """
        self.pos = pos
        self.radius = radius
        self.label = label

    def get(self):
        return self.label


class GuideLine:
    """
    Represents a guideline.
    """

    def __init__(self, pos):
        """
        Initialize a new GuideLine object.

        Args:
            pos (tuple): Position of the guideline (x, y).
        """
        self.pos = pos

    def clear(self):
        self.pos = None

    def get(self):
        return None
