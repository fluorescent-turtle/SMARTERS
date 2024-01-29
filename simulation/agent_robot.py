import mesa


class Robot(mesa.Agent):

    def __init__(self, pos, model):
        """
        Create a new robot.
        Args:
            pos: The robot's coordinates on the grid.
            model: Standard model reference for agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.condition = "High"

    def step(self):
        if self.condition == "Cutting":
            """for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.condition == "Fine":
                    neighbor.condition = "On Fire"""
            self.condition = "Cut"
