import random
from abc import ABC

from Controller.environment_plugin import contains_resource
from Controller.movement_plugin import MovementPlugin
from Model.agents import SquaredBlockedArea, CircledBlockedArea, GuideLine
from Utils.utils import get_grass_tassel


def random_boing(grid, pos):
    """
    Moves the agent randomly to a nearby empty cell.

    Args:
        grid: The simulation grid.
        pos: Current position of the agent.

    Returns:
        A tuple representing the new position of the agent.
    """
    # Get available directions based on Moore neighborhood
    available_directions = grid.get_neighborhood(pos, moore=True, include_center=False)

    # Randomly choose a direction among the available ones
    random_direction = random.choice(available_directions)

    # Compute the new position based on the chosen direction
    new_pos = (pos[0] + random_direction[0], pos[1] + random_direction[1])

    return new_pos


def ping_pong_boing(grid, pos):
    """
    Bounce the agent horizontally between the two ends of the row.

    Args:
        grid: The simulation grid.
        pos: Current position of the agent.

    Returns:
        A tuple representing the new position of the agent.
    """
    # If the agent reaches the left end, move right
    if pos[1] == 0:
        return pos[0], pos[1] + 1

    # If the agent reaches the right end, move left
    elif pos[1] == grid.width - 1:
        return pos[0], pos[1] - 1

    # Otherwise, keep moving forward
    else:
        return pos[0], pos[1] + 1


class DefaultMovementPlugin(MovementPlugin, ABC):
    def __init__(self, movement_type, grid, resources, base_station_pos, boing):
        super().__init__(grid, resources, base_station_pos)
        self.movement_type = movement_type
        self.boing = boing
        self.pos = base_station_pos

    def move(self, agent):
        if self.movement_type == "random":
            self.random_move(agent, agent.grass_tassels)
        elif self.movement_type == "systematic":
            self.systematic_move(agent, agent.grass_tassels)

    def random_move(self, agent, grass_tassels):
        """
        Move the agent to a random neighboring cell if available.
        """
        right_neighbor = (self.pos[0] + 1, self.pos[1])

        try:
            if (
                    0 <= right_neighbor[0] < self.grid.width
                    and 0 <= right_neighbor[1] < self.grid.height
            ):
                print("RIGHT NEIGHBOR: ", right_neighbor)
                # Check if the right neighbor contains a GuideLine
                if not contains_resource(
                        self.grid,
                        (right_neighbor[0], right_neighbor[1]),
                        SquaredBlockedArea or CircledBlockedArea,
                ):
                    contents = self.grid.get_cell_list_contents([right_neighbor])
                    # Move forward until a non-GuideLine cell is found to the right
                    for content in contents:
                        if contains_resource(
                                self.grid, (content.pos[0], content.pos[1]), GuideLine
                        ):
                            self.move_agent_forward(agent, grass_tassels)
            else:
                # Move back if there's no right neighbor or it's out of bounds
                self.move_agent_to_left(agent, grass_tassels)
        except Exception as e:
            print(f"Error occurred during random_move: {e}")
            # Optionally, log the error or take other corrective actions

    def move_agent_to_left(self, agent, grass_tassels):
        """
        Move the agent to the left neighbor if available.
        """
        left_neighbor = (self.pos[0] - 1, self.pos[1])

        if not contains_resource(
                self.grid, left_neighbor, SquaredBlockedArea or CircledBlockedArea
        ):
            print("LEFT NEIGHBOR: ", left_neighbor)
            self.grid.move_agent(agent, left_neighbor)
            self.pos = left_neighbor
        else:
            # If the left neighbor is not empty, move to a random neighbor
            self.move_to_random_neighbor(agent, grass_tassels)

    def move_agent_forward(self, agent, grass_tassels):
        found_guideline = False
        new_position = list(self.pos)

        while not found_guideline:
            new_position[1] += 1

            # Check if new_position is out of bounds
            if not (0 <= new_position[0] < self.grid.width and 0 <= new_position[1] < self.grid.height):
                print("New position is out of grid bounds.")
                break

            # Check if new_position is different from the starting position
            if new_position != self.pos:
                # Check if the new position contains a GuideLine resource
                if contains_resource(self.grid, tuple(new_position), GuideLine):
                    print("NEW POSITION: ", new_position)
                    found_guideline = True
                    break  # Exit the loop once a guideline is found

        if found_guideline:
            self.grid.move_agent(agent, tuple(new_position))
            self.pos = tuple(new_position)

            grass_tassel = get_grass_tassel(self.grid, grass_tassels, self.pos)
            if grass_tassel is not None:
                grass_tassel.increment()
        else:
            print("No guideline found, agent did not move.")

    def move_to_random_neighbor(self, agent, grass_tassels):
        possible_moves = []
        # Find potential moves excluding resource locations
        for move in self.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
        ):
            if move not in self.resources:
                possible_moves.append(move)

        if possible_moves:
            new_position = random.choice(possible_moves)
            self.finds_position_updates_robot(new_position, agent, grass_tassels)

    def finds_position_updates_robot(self, new_position, agent, grass_tassels):
        while contains_resource(
                self.grid, new_position, SquaredBlockedArea
        ) or contains_resource(self.grid, new_position, CircledBlockedArea):
            new_position = self.bounce((new_position[0], new_position[1]), self.boing)

        self.grid.move_agent(agent, new_position)
        self.pos = new_position

        grass_tassel = get_grass_tassel(self.grid, grass_tassels, new_position)
        if grass_tassel is not None:
            grass_tassel.increment()

    def systematic_move(self, agent, grass_tassels):
        """
        Move the agent systematically based on its current direction.
        If the new position is out of bounds, change direction to up or down.
        If there is an obstacle at the new position, try changing direction to avoid it.
        Finally, move the agent to the new position.
        """
        # Get the x and y displacement from the current direction
        dx, dy = self.directions[self.current_direction_index]

        # Calculate the new position
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        # Check if the new position is out of bounds
        if (
                new_x < 0
                or new_x >= self.grid_width
                or new_y < 0
                or new_y >= self.grid_height
        ):
            # Change direction to up or down
            self.current_direction_index = (self.current_direction_index + 2) % len(
                self.directions
            )

            # Recalculate the new position with the updated direction
            dx, dy = self.directions[self.current_direction_index]
            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy

        # Check if there is an obstacle at the new position
        while self.grid[new_x][new_y] is not None and (
                contains_resource(
                    self.grid,
                    (new_x, new_y),
                    CircledBlockedArea,
                )
                or
                contains_resource(
                    self.grid,
                    (new_x, new_y),
                    SquaredBlockedArea,
                )
        ):
            new_x, new_y = self.boing((new_x, new_y), self.boing)

        # Move the agent to the new position
        self.pos = (new_x, new_y)
        self.grid.move_agent(agent, self.pos)

        grass_tassel = get_grass_tassel(self.grid, grass_tassels, self.pos)
        if grass_tassel is not None:
            grass_tassel.increment()

    def bounce(self, pos, cutting_type):
        if cutting_type == "random":
            return random_boing(self.grid, pos)
        elif cutting_type == "ping_pong":
            return ping_pong_boing(self.grid, pos)
        elif cutting_type == "probabilistic":
            return self.probabilistic_boing(self.grid, pos)

    def probabilistic_boing(self, grid, pos):
        # Implementazione del taglio dell'erba con distribuzione di probabilità
        pass
