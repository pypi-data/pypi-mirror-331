from __future__ import annotations

from minigrid.core.constants import COLOR_NAMES
from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Door, Goal, Key, Wall
from minigrid.manual_control import ManualControl
from minigrid.minigrid_env import MiniGridEnv


class NoLavaKeyOneEnv(MiniGridEnv):
    def __init__(
        self,
        size=13,
        agent_start_pos=(2, 11),
        agent_start_dir=0,
        max_steps: int | None = None,
        **kwargs,
    ):
        self.agent_start_pos = agent_start_pos
        self.agent_start_dir = agent_start_dir

        mission_space = MissionSpace(mission_func=self._gen_mission)

        if max_steps is None:
            max_steps = 4 * size**2

        super().__init__(
            mission_space=mission_space,
            grid_size=size,
            # Set this to True for maximum speed
            see_through_walls=True,
            max_steps=max_steps,
            **kwargs,
        )

    @staticmethod
    def _gen_mission():
        return "grand mission"

    def _gen_grid(self, width, height):
        # Create an empty grid
        self.grid = Grid(width, height)

        # Generate the surrounding walls
        self.grid.wall_rect(0, 0, width, height)

        # Generate horizonral separation walls
        for i in range(0, width):
            if (i != 2):
                self.grid.set(i, 4, Wall())
                self.grid.set(i, 8, Wall())
             
        for i in range(1, height):
            if (i <= 2 or i == 11 or i == 9):
                self.grid.set(4, i, Wall())
            if ((i <= 3 and i >= 2) or i >= 10):
                self.grid.set(8, i, Wall())
             
        # implement lava:
        #for i in range(2, 10):
            #self.grid.set(i, 6, Lava())
        
        # Place the door and keys
        self.grid.set(4, 3, Door(COLOR_NAMES[5], is_locked=True))
        self.grid.set(10, 10, Key(COLOR_NAMES[5]))
        #self.grid.set(1, 2, Key(COLOR_NAMES[5]))

        # Place a goal square
        self.put_obj(Goal(), 9, 2)

        # Place the agent
        if self.agent_start_pos is not None:
            self.agent_pos = self.agent_start_pos
            self.agent_dir = self.agent_start_dir
        else:
            self.place_agent()

        self.mission = "grand mission"


