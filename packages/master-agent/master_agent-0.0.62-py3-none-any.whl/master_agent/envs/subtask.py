from typing import Literal
from minigrid.minigrid_env import MiniGridEnv
from minigrid.core.world_object import WorldObj, Door
import numpy as np

def modify_env_reward(env: MiniGridEnv, predicate: Literal["at", "holding", "unlocked"], target_obj: WorldObj | None = None, target_coords: tuple[int, int] | None = None) -> MiniGridEnv:
    if predicate == "at":
        if target_coords is None and target_obj is None:
            raise ValueError("When using 'at' predicate, target_coords or target_obj must be provided")
    elif predicate == "holding":
        if target_obj is None:
            raise ValueError("When using 'holding' predicate, target_obj must be provided")
    elif predicate == "unlocked":
        if target_coords is None and target_obj is None:
            raise ValueError("When using 'unlocked' predicate, target_coords or target_obj must be provided")
    else:
        raise ValueError("Predicate must be one of 'at', 'holding', 'unlocked'")

    original_step = MiniGridEnv.step

    def modified_step(action):
        obs, reward, terminated, truncated, info = original_step(env, action)
        reward = 0

        if predicate == "at":
            ax, ay = env.agent_pos

            if target_coords is not None:
                tx, ty = target_coords
                
                if (ax == tx and ay == ty):
                    if target_obj is None or env.grid.get(tx, ty).encode()[0] == target_obj.encode()[0] and env.grid.get(tx, ty).encode()[1] == target_obj.encode()[1]:
                        reward = env._reward()
                        terminated = True
                        return obs, reward, terminated, truncated, info
            elif target_obj is not None:
                grid_enc = env.grid.encode()
                target_obj_enc = target_obj.encode()

                for i in range(env.grid.width):
                    for j in range(env.grid.height):
                        if grid_enc[i][j][0] == target_obj_enc[0] and grid_enc[i][j][1] == target_obj_enc[1]:
                            reward = env._reward()
                            terminated = True
                            return obs, reward, terminated, truncated, info
                            
        elif predicate == "holding":
            if env.carrying is not None:
                if env.carrying.color == target_obj.color and env.carrying.type == target_obj.type:
                    if target_coords is not None:
                        ax, ay = env.agent_pos
                        tx, ty = target_coords

                        dx = [1, 0, -1, 0]
                        dy = [0, 1, 0, -1]

                        for i in range(4):
                            if (ax + dx[i] == tx and ay + dy[i] == ty):
                                reward = env._reward()
                                terminated = True
                                return obs, reward, terminated, truncated, info
                    else:
                        reward = env._reward()
                        terminated = True
                        return obs, reward, terminated, truncated, info
        elif predicate == "unlocked":
            if target_coords is not None:
                tx, ty = target_coords
                door = env.grid.get(tx, ty)

                if door is not None and isinstance(door, Door) and door.is_open and (target_obj is None or door.color == target_obj.color):
                    reward = env._reward()
                    terminated = True
                    return obs, reward, terminated, truncated, info
            elif target_obj is not None:
                grid_enc = env.grid.encode()
                target_obj_enc = target_obj.encode()

                for i in range(env.grid.width):
                    for j in range(env.grid.height):
                        door = env.grid.get(i, j)
                        if door is not None and isinstance(door, Door) and door.is_open and door.color == target_obj.color:
                            reward = env._reward()
                            terminated = True
                            return obs, reward, terminated, truncated, info
        
        return obs, reward, terminated, truncated, info
    
    env.step = modified_step
    return env
