from typing import Literal
from minigrid.minigrid_env import MiniGridEnv
from minigrid.core.world_object import WorldObj, Door
import numpy as np
from rl.dag import DagNode

def modify_env_reward(env: MiniGridEnv, src: DagNode, dest: DagNode) -> MiniGridEnv:

    # Validate src node predicates
    if src.predicate not in ["holding", "at", "unlocked"]:
        raise ValueError("Invalid predicate for src node. Must be 'holding', 'at', or 'unlocked'")

    # Capture the original reset method and define the modified one
    original_reset = env.reset

    def modified_reset(*args, **kwargs):
        obs, info = original_reset(*args, **kwargs)
        # Set up the environment based on src predicate
        if src.predicate == "holding":
            if src.worldObj is None:
                raise ValueError("Src node with 'holding' predicate must have a worldObj")
            obj_x, obj_y = src.coord
            # Remove the object from the grid at its location
            env.grid.set(obj_x, obj_y, None)
            env.carrying = src.worldObj
        elif src.predicate == "at":
            if src.coord is None:
                raise ValueError("Src node with 'at' predicate must have coord")
        elif src.predicate == "unlocked":
            if src.coord is None:
                raise ValueError("Src node 'unlocked' requires coord or worldObj")
            obj_x, obj_y = src.coord
            world_item = env.grid.get(obj_x, obj_y)
            world_item.is_open = True
            world_item.is_locked = False

        agent_x, agent_y = src.coord
        env.agent_pos = (agent_x, agent_y)
        env.agent_dir = 0

        obs = env.gen_obs()
        return obs, info 

    env.reset = modified_reset

    # Validate dest node logic (for reaching the girl)
    if dest.predicate == "at":
        if dest.coord is None and dest.worldObj is None:
            raise ValueError("For 'at' predicate, target_coords or target_obj must be provided")
    elif dest.predicate == "holding":
        if dest.worldObj is None:
            raise ValueError("For 'holding' predicate, target_obj must be provided")
    elif dest.predicate == "unlocked":
        if dest.coord is None and dest.worldObj is None:
            raise ValueError("For 'unlocked' predicate, target_coords or target_obj must be provided")
    else:
        raise ValueError("Predicate must be one of 'at', 'holding', 'unlocked'")

    original_step = MiniGridEnv.step

    def modified_step(action):


        # used to calculate to speed up the agent to reach the goal, by comparing the last previous step to the next step
        if dest.coord is not None:
            prev_distance = abs(env.agent_pos[0] - dest.coord[0]) + abs(env.agent_pos[1] - dest.coord[1])
        else:
            prev_distance = None

        # Execute the original step action
        obs, original_reward, terminated, truncated, info = original_step(env, action)

        # --- Check for Lava ---
        # Before applying any further rewards, check if the new cell is lava.
        current_tile = env.grid.get(env.agent_pos[0], env.agent_pos[1])
        # Assuming the lava tile's type is "lava". You could also check via isinstance if you have a Lava class.
        if current_tile is not None and getattr(current_tile, "type", None) == "lava":
            # Agent hit lava; assign 0 reward and do not add shaping reward.
            return obs, 0, terminated, truncated, info

        if dest.predicate == "at":
            ax, ay = env.agent_pos
            if dest.coord is not None:
                tx, ty = dest.coord
                if ax == tx and ay == ty:
                    if dest.worldObj is None or (env.grid.get(tx, ty).encode()[0] == dest.worldObj.encode()[0] 
                                                 and env.grid.get(tx, ty).encode()[1] == dest.worldObj.encode()[1]):
                        reward = env._reward()
                        terminated = True
                        return obs, reward, terminated, truncated, info
            elif dest.worldObj is not None:
                grid_enc = env.grid.encode()
                target_obj_enc = dest.worldObj.encode()
                for i in range(env.grid.width):
                    for j in range(env.grid.height):
                        if grid_enc[i][j][0] == target_obj_enc[0] and grid_enc[i][j][1] == target_obj_enc[1]:
                            reward = env._reward()
                            terminated = True
                            return obs, reward, terminated, truncated, info

        elif dest.predicate == "holding":
            if env.carrying is not None:
                if env.carrying.color == dest.worldObj.color and env.carrying.type == dest.worldObj.type:
                    if dest.coord is not None:
                        ax, ay = env.agent_pos
                        tx, ty = dest.coord
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

        elif dest.predicate == "unlocked":
            if dest.coord is not None:
                tx, ty = dest.coord
                door = env.grid.get(tx, ty)
                if door is not None and isinstance(door, Door) and door.is_open and (dest.worldObj is None or door.color == dest.worldObj.color):
                    reward = env._reward()
                    terminated = True
                    return obs, reward, terminated, truncated, info
            elif dest.worldObj is not None:
                grid_enc = env.grid.encode()
                target_obj_enc = dest.worldObj.encode()
                for i in range(env.grid.width):
                    for j in range(env.grid.height):
                        door = env.grid.get(i, j)
                        if door is not None and isinstance(door, Door) and door.is_open and door.color == dest.worldObj.color:
                            reward = env._reward()
                            terminated = True
                            return obs, reward, terminated, truncated, info

        # Only add shaping reward if not on lava and if we have a destination coordinate.
        reward = 0
        if dest.coord is not None and prev_distance is not None:
            curr_distance = abs(env.agent_pos[0] - dest.coord[0]) + abs(env.agent_pos[1] - dest.coord[1])
            # Coefficient that scales the shaping reward—adjust as needed.
            coefficient = 0.25
            shaping_reward = coefficient * (prev_distance - curr_distance)
            reward += shaping_reward

        return obs, reward, terminated, truncated, info

    env.step = modified_step
    return env
