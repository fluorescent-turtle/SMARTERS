import mesa

from simulation.agent_tassel import GrassTassel


# todo: siamo sicuri che il from vada bene e non ci devva essere solamente .agent?
class ForestFire(mesa.Model):
    """
    Simple Forest Fire model.
    """

    def __init__(self, width=100, height=100, density=0.65):
        """
        Create a new environment model.

        Args:
            width, height: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        """
        super().__init__()
        # Set up model objects
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(width, height, torus=False)

        self.datacollector = mesa.DataCollector(
            {
                "High": lambda m: self.count_type(m, "High"),
                "Cut": lambda m: self.count_type(m, "Cut"),
            }
        )

        # Place a tree in each cell with Prob = density
        for contents, (x, y) in self.grid.coord_iter():
            if self.random.random() < density:
                # Create a tree
                new_tassel = GrassTassel((x, y), self)
                # Set all trees in the first column on fire.
                if x == 0:
                    new_tassel.condition = "High"
                self.grid.place_agent(new_tassel, (x, y))
                self.schedule.add(new_tassel)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # Halt if no more fire
        if self.count_type(self, "High") == 0:
            self.running = False

    @staticmethod
    def count_type(model, tree_condition):
        """
        Helper method to count trees in a given condition in a given model.
        """
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count
