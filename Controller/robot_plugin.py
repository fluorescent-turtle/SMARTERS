import math
import random
from abc import ABC

from Controller.movement_plugin import MovementPlugin
from Model.agents import (
    CircledBlockedArea,
    SquaredBlockedArea,
    IsolatedArea,
    Opening,
    GuideLine,
)
from Utils.utils import (
    within_bounds,
    get_grass_tassel,
    mowing_time,
    contains_any_resource,
)


def pass_on_neighbors(pos, grid, diameter, grass_tassels, agent, dim_tassel):
    radius = math.ceil((diameter / dim_tassel) / 2)
    neighbors = grid.get_neighbors(pos, moore=False, include_center=True, radius=radius)

    for neighbor in neighbors:
        pass_on_current_tassel(grass_tassels, neighbor, agent, diameter)


def pass_on_current_tassel(grass_tassels, new_pos, agent, cut_diameter):
    grass_tassel = get_grass_tassel(grass_tassels, new_pos)
    if grass_tassel is not None:
        grass_tassel.increment()

        mowing_t = mowing_time(
            agent.speed,
            agent.get_autonomy(),
            cut_diameter,
            1,
        )
        agent.decrease_autonomy(mowing_t)
        agent.path_taken.add(new_pos)


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
            (0, 1),
            (1, 0),
            (0, -1),
            (1, -1),
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (1, 1),
        ]
        self.dx_tassel = {
            (1, 0): (0, -1),
            (1, -1): (-1, -1),
            (0, -1): (-1, 0),
            (-1, -1): (-1, 1),
            (-1, 0): (0, 1),
            (-1, 1): (1, 1),
            (0, 1): (1, 0),
            (1, 1): (1, -1),
        }
        self.sx_tassel = {
            (1, 0): (0, 1),
            (1, -1): (-1, -1),
            (0, -1): (-1, 0),
            (-1, -1): (0, -1),
            (-1, 0): (-1, -1),
            (-1, 1): (1, 0),
            (0, 1): (1, 0),
            (1, 1): (0, 1),
        }

        self.up_sx_tassel = {
            (1, 0): (1, 1),
            (1, -1): (1, 0),
            (0, -1): (1, -1),
            (-1, -1): (0, -1),
            (-1, 0): (-1, -1),
            (-1, 1): (-1, 0),
            (0, 1): (-1, 1),
            (1, 1): (0, 1),
        }

    def move(self, agent):
        if self.movement_type == "random":
            self.random_move(agent, agent.get_gt())
        elif self.movement_type == "systematic":
            pass
            # self.systematic_move(agent, agent.get_gt())

    def random_move(self, agent, grass_tassels):
        if agent.get_first():
            print(f"INITIAL POS: {self.pos}")
            aux_pos = self.pos
            agent.dir = random.choice(self.directions)
            aux_pos = aux_pos[0] + agent.dir[0], aux_pos[1] + agent.dir[1]

            while (
                    not within_bounds(self.grid_width, self.grid_height, aux_pos)
                    or aux_pos in agent.path_taken
            ):
                aux_pos = self.pos
                agent.dir = random.choice(self.directions)
                aux_pos = aux_pos[0] + agent.dir[0], aux_pos[1] + agent.dir[1]
            self.pos = aux_pos
            agent.path_taken.add(self.pos)
            agent.not_first()

        agent.dx = self.dx_tassel[agent.dir]
        self.pos = self.pos[0] + agent.dir[0], self.pos[1] + agent.dir[1]

        if within_bounds(self.grid_width, self.grid_height, self.pos):
            if within_bounds(
                    self.grid_width,
                    self.grid_height,
                    (self.pos[0] + agent.dir[0], self.pos[1] + agent.dir[1]),
            ) and not contains_any_resource(
                self.grid,
                (self.pos[0] + agent.dir[0], self.pos[1] + agent.dir[1]),
                [CircledBlockedArea, SquaredBlockedArea],
                self.grid_width,
                self.grid_height,
            ):
                if (
                        Opening not in self.grid.get_cell_list_contents(self.pos)
                        and IsolatedArea not in self.grid.get_cell_list_contents(self.pos)
                        or GuideLine in self.grid.get_cell_list_contents(agent.dx)
                        and CircledBlockedArea
                        not in self.grid.get_cell_list_contents(self.pos)
                        and SquaredBlockedArea
                        not in self.grid.get_cell_list_contents(self.pos)
                ):
                    if self.pos not in agent.path_taken:
                        self.grid.move_agent(agent, self.pos)

                        pass_on_current_tassel(
                            grass_tassels, self.pos, agent, self.cut_diameter
                        )
                        pass_on_neighbors(
                            self.pos,
                            self.grid,
                            self.cut_diameter,
                            grass_tassels,
                            agent,
                            self.dim_tassel,
                        )
                    else:
                        aux_pos = self.pos
                        agent.dir = random.choice(self.directions)
                        aux_pos = aux_pos[0] + agent.dir[0], aux_pos[1] + agent.dir[1]

                        while not within_bounds(
                                self.grid_width, self.grid_height, aux_pos
                        ) or contains_any_resource(
                            self.grid,
                            aux_pos,
                            [CircledBlockedArea, SquaredBlockedArea],
                            self.grid_width,
                            self.grid_height,
                        ):
                            aux_pos = self.pos
                            agent.dir = random.choice(self.directions)
                            aux_pos = (
                                aux_pos[0] + agent.dir[0],
                                aux_pos[1] + agent.dir[1],
                            )
                        self.pos = aux_pos

                        self.grid.move_agent(agent, self.pos)
                        pass_on_current_tassel(
                            grass_tassels, self.pos, agent, self.cut_diameter
                        )
                        pass_on_neighbors(
                            self.pos,
                            self.grid,
                            self.cut_diameter,
                            grass_tassels,
                            agent,
                            self.dim_tassel,
                        )

                else:
                    if within_bounds(self.grid_width, self.grid_height, self.pos) and (
                            CircledBlockedArea in self.grid.get_cell_list_contents(self.pos)
                            or SquaredBlockedArea
                            in self.grid.get_cell_list_contents(self.pos)
                    ):
                        print(f"primo if else: {self.pos}")
                    self.bounce(agent, grass_tassels)
            else:
                if within_bounds(self.grid_width, self.grid_height, self.pos) and (
                        CircledBlockedArea in self.grid.get_cell_list_contents(self.pos)
                        or SquaredBlockedArea in self.grid.get_cell_list_contents(self.pos)
                ):
                    print(f"secondo if else: {self.pos}")
                self.bounce(agent, grass_tassels)
        else:
            if within_bounds(self.grid_width, self.grid_height, self.pos) and (
                    CircledBlockedArea in self.grid.get_cell_list_contents(self.pos)
                    or SquaredBlockedArea in self.grid.get_cell_list_contents(self.pos)
            ):
                print(f"terzo if else: {self.pos}")
            self.bounce(agent, grass_tassels)

    def move_back(self, agent, grass_tassels):
        num_tass_back = math.ceil(self.cut_diameter / self.dim_tassel)
        for _ in range(num_tass_back):
            aux_pos = (self.pos[0] - agent.dir[0]), (self.pos[1] - agent.dir[1])
            if (
                    within_bounds(self.grid_width, self.grid_height, aux_pos)
                    and SquaredBlockedArea not in self.grid.get_cell_list_contents(aux_pos)
                    and CircledBlockedArea not in self.grid.get_cell_list_contents(aux_pos)
            ):
                # print("NEL FOR MOVE BACK")
                self.pos = aux_pos
                pass_on_current_tassel(
                    grass_tassels, self.pos, agent, self.cut_diameter
                )
                pass_on_neighbors(
                    self.pos,
                    self.grid,
                    self.cut_diameter,
                    grass_tassels,
                    agent,
                    self.dim_tassel,
                )
            else:
                break

    def bounce(self, agent, grass_tassels):
        self.move_back(agent, grass_tassels)
        agent.dir = self.up_sx_tassel[agent.dir]
