import math
import random
from abc import ABC
from typing import List, Tuple

from Controller.movement_plugin import MovementPlugin
from Model.agents import (
    SquaredBlockedArea,
    CircledBlockedArea,
    GrassTassel,
    GuideLine,
    Opening,
)
from Utils.utils import (
    get_grass_tassel,
    mowing_time,
    contains_any_resource,
    within_bounds,
)


def ping_pong_boing(agent, pos: Tuple[int, int]) -> Tuple[int, int]:
    """Implements ping pong movement logic."""
    if pos[1] == 0:
        return pos[0], pos[1] + 1
    elif pos[1] == agent.grid_width:
        return pos[0], pos[1] - 1
    else:
        return pos[0], pos[1] + 1


def check_right_for_guide_line(
        pos: Tuple[int, int],
        direction: Tuple[int, int],
        grid,
        grid_width: int,
        grid_height: int,
) -> bool:
    """Checks if there's a guide line to the right of the current position."""
    right_pos = (pos[0] + direction[1] * 1, pos[1] - direction[0] * 1)
    return within_bounds(grid_width, grid_height, right_pos) and contains_any_resource(
        grid, right_pos, [GuideLine], grid_width, grid_height
    )


def move_backward(
        pos: Tuple[int, int], direction: Tuple[int, int], grid_width, grid_height
) -> Tuple[int, int]:
    new_x = pos[0] + direction[0]
    new_y = pos[1] + direction[1]
    print(f"PREV POS: {pos} -- NEW POS: {new_x, new_y}")

    while not within_bounds(grid_width, grid_height, (new_x, new_y)):  # todo
        new_x = pos[0] + direction[0]
        new_y = pos[1] + direction[1]
        print(f"PREV POS: {pos} -- NEW POS: {new_x, new_y}")

    return new_x, new_y


class DefaultMovementPlugin(MovementPlugin, ABC):
    def __init__(
            self,
            movement_type: str,
            grid,
            base_station_pos,
            boing: str,
            cut_diameter: int,
            grid_width: int,
            grid_height: int,
            dim_tassel,
    ):
        super().__init__(grid, base_station_pos, grid_width, grid_height)
        self.movement_type = movement_type
        self.boing = boing
        self.cut_diameter = cut_diameter
        self.dim_tassel = dim_tassel
        self.directions = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        ]
        self.current_direction_index = 0
        self.path_taken = []  # List to store the path taken

    def move(self, agent):
        """Moves the agent based on the specified movement type."""
        if self.movement_type == "random":
            self.random_move(agent, agent.get_gt())
        elif self.movement_type == "systematic":
            self.systematic_move(agent, agent.get_gt())

    def process_neighbors(
            self, direction: Tuple[int, int], valid_moves, agent, grass_tassels
    ):
        var = math.ceil(self.cut_diameter * self.dim_tassel)
        for dx in range(-var, var + 1):
            for dy in range(-var, var + 1):
                if dx == 0 and dy == 0:
                    continue

                neighbor = (self.pos[0] + dx, self.pos[1] + dy)
                if within_bounds(self.grid_width, self.grid_height, neighbor):
                    while within_bounds(
                            self.grid_width, self.grid_height, neighbor
                    ) and not contains_any_resource(
                        self.grid,
                        neighbor,
                        [SquaredBlockedArea, CircledBlockedArea],
                        self.grid_width,
                        self.grid_height,
                    ):
                        if agent.get_autonomy() > 0:
                            valid_moves.append(neighbor)
                            neighbor = tuple(
                                coord + d for coord, d in zip(neighbor, direction)
                            )

                            grass_tassel = get_grass_tassel(grass_tassels, neighbor)
                            if grass_tassel is not None:
                                grass_tassel.increment()
                                mowing_t = mowing_time(
                                    agent.speed,
                                    agent.get_autonomy(),
                                    self.cut_diameter,
                                    1,
                                )
                                agent.decrease_autonomy(mowing_t)
                        else:
                            break

    def get_neighbors(self) -> List[Tuple[int, int]]:
        """Returns a list of neighboring positions based on the current position."""
        if self.on_top():
            return [
                (self.pos[0], self.pos[1] - 1),
                (self.pos[0], self.pos[1] + 1),
                (self.pos[0] + 1, self.pos[1] - 1),
                (self.pos[0] + 1, self.pos[1] + 1),
                (self.pos[0] + 1, self.pos[1]),
            ]
        elif self.on_bottom():
            return [
                (self.pos[0], self.pos[1] + 1),
                (self.pos[0], self.pos[1] - 1),
                (self.pos[0] - 1, self.pos[1] + 1),
                (self.pos[0] - 1, self.pos[1] - 1),
                (self.pos[0] - 1, self.pos[1]),
            ]
        elif self.on_left():
            return [
                (self.pos[0] + 1, self.pos[1]),
                (self.pos[0] - 1, self.pos[1]),
                (self.pos[0] - 1, self.pos[1] + 1),
                (self.pos[0] + 1, self.pos[1] + 1),
                (self.pos[0], self.pos[1] + 1),
            ]
        else:
            return [
                (self.pos[0] - 1, self.pos[1]),
                (self.pos[0] + 1, self.pos[1]),
                (self.pos[0] - 1, self.pos[1] - 1),
                (self.pos[0] + 1, self.pos[1] - 1),
                (self.pos[0], self.pos[1] - 1),
            ]

    def get_valid_random_moves(self, agent, grass_tassels):
        """Returns a list of valid random moves based on the current position."""
        valid_moves = []
        last_neighbor = None

        neighbors = self.get_neighbors()
        if not agent.get_first():
            print(f"PREVIOUS POS: {self.pos}")
            self.pos = random.choice(neighbors)
            print(f"NEXT POS: {self.pos}")

            grass_tassel = get_grass_tassel(grass_tassels, self.pos)
            if grass_tassel is not None:
                # print(f"VALID MOVE: {neighbor}")
                grass_tassel.increment()

                mowing_t = mowing_time(
                    agent.speed,
                    agent.get_autonomy(),
                    self.cut_diameter,
                    1,
                )
                agent.decrease_autonomy(mowing_t)

            neighbors = self.get_neighbors()
            agent.not_first()

        if (
                within_bounds(self.grid_width, self.grid_height, neighbors[1])
                and agent.get_autonomy() > 0
        ):
            last_neighbor = neighbors[1]
            print(f"NEIGHBORS: {neighbors}")

            for neighbor in neighbors:
                if agent.get_autonomy() > 0:
                    if within_bounds(
                            self.grid_width, self.grid_height, neighbor
                    ) and GrassTassel in self.grid.get_cell_list_contents(neighbor):
                        grass_tassel = get_grass_tassel(grass_tassels, neighbor)
                        if grass_tassel is not None:
                            # print(f"VALID MOVE: {neighbor}")
                            grass_tassel.increment()

                            mowing_t = mowing_time(
                                agent.speed,
                                agent.get_autonomy(),
                                self.cut_diameter,
                                1,
                            )
                            agent.decrease_autonomy(mowing_t)
                        valid_moves.append(neighbor)

                else:
                    break

                for direction in self.directions:
                    self.process_neighbors(direction, valid_moves, agent, grass_tassels)
            neighbors = self.get_neighbors()  # todo

        print(f"LAST NEIGHBOR: {last_neighbor}")

        return valid_moves, last_neighbor

    def random_move(self, agent, grass_tassels):
        """Performs a random move for the agent."""
        valid_moves, final_up_neighbour = self.get_valid_random_moves(
            agent, grass_tassels
        )

        aux_pos = self.pos
        print("INITIAL POSITION: ", self.pos)

        if valid_moves:
            contents = self.grid.get_cell_list_contents(final_up_neighbour)
            if not (CircledBlockedArea in contents) and not (
                    SquaredBlockedArea in contents
            ):
                print("NEL MOVE FORWARD")
                self.move_agent_forward(agent, final_up_neighbour)
            else:
                print("BOUNCE1")
                self.pos = self.bounce(
                    final_up_neighbour, self.boing, agent, grass_tassels
                )
        else:
            # print(f"BOUNCE2 --- GRASStASSELS {grass_tassels}")
            self.pos = self.bounce(aux_pos, self.boing, agent, grass_tassels)

        # self.path_taken.append(self.pos)

    def move_agent_forward(self, agent, up_neighbor: Tuple[int, int]):
        """Moves the agent forward to the specified neighboring position."""
        self.grid.move_agent(agent, up_neighbor)
        self.pos = up_neighbor

    def on_top(self) -> bool:
        """Checks if the current position is at the top boundary."""
        return self.pos[0] == 0

    def on_bottom(self) -> bool:
        """Checks if the current position is at the bottom boundary."""
        return self.pos[0] == self.grid_width

    def on_left(self) -> bool:
        """Checks if the current position is at the left boundary."""
        return self.pos[1] == 0

    def rotate_left(
            self,
            pos: Tuple[int, int],
            direction: Tuple[int, int],
            size: int,
            grid_width: int,
            grid_height: int,
            grass_tassels,
            agent,
    ) -> Tuple[int, int]:
        angle = 25

        while angle < 360 and agent.get_autonomy() > 0:
            angle_rad = math.radians(angle)
            cos_angle = math.cos(angle_rad)
            sin_angle = math.sin(angle_rad)
            new_dx = direction[0] * cos_angle - direction[1] * sin_angle
            new_dy = direction[0] * sin_angle + direction[1] * cos_angle
            new_x = pos[0] + size * new_dx
            new_y = pos[1] + size * new_dy

            new_pos = math.ceil(new_x), math.ceil(new_y)
            if (
                    within_bounds(grid_width, grid_height, new_pos)
                    # and new_pos not in self.path_taken
                    and not contains_any_resource(
                self.grid,
                new_pos,
                [CircledBlockedArea, SquaredBlockedArea],
                grid_width,
                grid_height,
            )
                    and agent.get_autonomy() > 0
            ):
                grass_tassel = get_grass_tassel(grass_tassels, new_pos)

                if grass_tassel is not None:
                    # print(f"VALID MOVE: {neighbor}")
                    grass_tassel.increment()

                    mowing_t = mowing_time(
                        agent.speed,
                        agent.get_autonomy(),
                        self.cut_diameter,
                        1,
                    )
                    agent.decrease_autonomy(mowing_t)
                return new_pos

            angle += random.randint(15, 25)

        """grass_tassel = get_grass_tassel(grass_tassels, pos)

        if grass_tassel is not None:
            # print(f"VALID MOVE: {neighbor}")
            grass_tassel.increment()

            mowing_t = mowing_time(
                agent.speed,
                agent.get_autonomy(),
                self.cut_diameter,
                1,
            )
            agent.decrease_autonomy(mowing_t)"""
        return pos

    def random_boing(
            self,
            pos: Tuple[int, int],
            grid_width: int,
            grid_height: int,
            grass_tassels,
            agent,
    ) -> Tuple[int, int]:
        """Performs a random boing movement."""
        size = 1
        direction = self.get_initial_direction()
        p = None
        # print(f"GRID WIDTH AND HEIGHT {grid_width} {grid_height}")
        new_pos = move_backward(pos, direction, grid_width, grid_height)
        # print(f"BOUNCING: {new_pos} ---- {self.grid.get_cell_list_contents(new_pos)}")
        grass_tassel = get_grass_tassel(grass_tassels, new_pos)

        if grass_tassel is not None:
            # print(f"VALID MOVE: {neighbor}")
            grass_tassel.increment()

            mowing_t = mowing_time(
                agent.speed,
                agent.get_autonomy(),
                self.cut_diameter,
                1,
            )
            agent.decrease_autonomy(mowing_t)

        pos = self.rotate_left(
            new_pos, direction, size, grid_width, grid_height, grass_tassels, agent
        )

        while p is None and agent.get_autonomy() > 0:
            random_direction = random.choice(self.directions)
            random_pos = pos[0] + random_direction[0], pos[1] + random_direction[1]
            print(f"BOUNCING: {random_pos}")

            if within_bounds(
                    grid_width, grid_height, random_pos
            ) and not contains_any_resource(
                self.grid,
                random_pos,
                [CircledBlockedArea, SquaredBlockedArea],
                grid_width,
                grid_height,
            ):
                grass_tassel = get_grass_tassel(grass_tassels, random_pos)

                if grass_tassel is not None:
                    # print(f"VALID MOVE: {neighbor}")
                    grass_tassel.increment()

                    mowing_t = mowing_time(
                        agent.speed,
                        agent.get_autonomy(),
                        self.cut_diameter,
                        1,
                    )
                    agent.decrease_autonomy(mowing_t)
                p = random_pos

                return p

        p = new_pos

        return p

    def get_initial_direction(self) -> Tuple[int, int]:
        """Determines the initial direction based on the current position."""
        if self.on_top():
            return 1, 0
        elif self.on_bottom():
            return -1, 0
        elif self.on_left():
            return 0, 1
        else:
            return 0, -1

    def bounce(self, pos: Tuple[int, int], cutting_type: str, agent, grass_tassels):
        if agent.get_autonomy() > 0:
            if cutting_type == "random":
                return self.random_boing(
                    pos, self.grid_width, self.grid_height, grass_tassels, agent
                )
            elif cutting_type == "ping_pong":
                return ping_pong_boing(self, pos)

    def systematic_move(self, agent, grass_tassels):
        """Performs a systematic move for the agent."""
        dx, dy = self.directions[self.current_direction_index]
        new_pos = (self.pos[0] + dx, self.pos[1] + dy)

        if not within_bounds(
                self.grid_width, self.grid_height, new_pos
        ) or contains_any_resource(
            self.grid,
            new_pos,
            [CircledBlockedArea, SquaredBlockedArea],
            self.grid_width,
            self.grid_height,
        ):
            self.current_direction_index = (self.current_direction_index + 1) % len(
                self.directions
            )
            dx, dy = self.directions[self.current_direction_index]
            new_pos = (self.pos[0] + dx, self.pos[1] + dy)

        while within_bounds(
                self.grid_width, self.grid_height, new_pos
        ) and contains_any_resource(
            self.grid,
            new_pos,
            [CircledBlockedArea, SquaredBlockedArea],
            self.grid_width,
            self.grid_height,
        ):
            new_pos = self.bounce(new_pos, self.boing, agent, grass_tassels)

        self.pos = new_pos
        self.grid.move_agent(agent, self.pos)

        grass_tassel = get_grass_tassel(grass_tassels, self.pos)
        if grass_tassel is not None:
            # print("GRASS TASSEL IS NOT NONE:")
            grass_tassel.increment()

        # self.path_taken.append(self.pos)
