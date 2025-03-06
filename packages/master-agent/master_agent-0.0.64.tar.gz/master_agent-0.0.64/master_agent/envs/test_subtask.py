from minigrid.envs import EmptyEnv
from minigrid.core.world_object import Box, Key, Door, Goal
from minigrid.core.grid import Grid
from envs import modify_env_reward
from PIL import Image
from minigrid.minigrid_env import MiniGridEnv
from minigrid.core.world_object import WorldObj, Door
from rl.dag import DagNode

def test_modify_env_at_reward():
    # Initialize the environment
    env = EmptyEnv(size=5, render_mode="rgb_array")

    # Define target objs positions
    target_obj_pos_1 = (2, 1)
    target_obj_pos_2 = (1, 2)

    # Set predefined grid for testing
    def custom_gen_grid(width, height):
        # Create grid
        custom_grid = Grid(width, height)

        # Define walls
        custom_grid.horz_wall(0, 0)
        custom_grid.horz_wall(0, height - 1)
        custom_grid.vert_wall(0, 0)
        custom_grid.vert_wall(width - 1, 0)

        # Set target objs
        custom_grid.set(target_obj_pos_1[0], target_obj_pos_1[1], Goal())
        custom_grid.set(target_obj_pos_2[0], target_obj_pos_2[1], Goal())

        env.grid = custom_grid
        env.agent_pos = (1, 1)
        env.agent_dir = 0
    env._gen_grid = custom_gen_grid
    env.reset()

    # Modify reward func for target_obj_1
    env = modify_env_reward(env, predicate="at", target_obj=Goal(), target_coords=target_obj_pos_1)

    # Move agent to target_obj_1
    obs, reward, terminated, truncated, info = env.step(env.actions.forward)
    assert reward > 0

    # Modify reward func for target_obj_2
    env = modify_env_reward(env, predicate="at", target_obj=Goal(), target_coords=target_obj_pos_2)

    # Move agent to target_obj_2
    env.step(env.actions.right)
    env.step(env.actions.forward)
    env.step(env.actions.right)
    obs, reward, terminated, truncated, info = env.step(env.actions.forward)
    assert reward > 0

    env.reset()

    screenshot = env.render()
    Image.fromarray(screenshot).save("screenshot.png")

    # Modify reward func for target_obj_1
    env = modify_env_reward(env, predicate="at", target_obj=Goal())

    # Move agent to target_obj_1
    obs, reward, terminated, truncated, info = env.step(env.actions.forward)
    assert reward > 0

    # Modify reward func for target_obj_2
    env = modify_env_reward(env, predicate="at", target_obj=Goal())

    # Move agent to target_obj_2
    env.step(env.actions.right)
    env.step(env.actions.forward)
    env.step(env.actions.right)
    obs, reward, terminated, truncated, info = env.step(env.actions.forward)
    assert reward > 0

def test_modify_env_holding_reward():
    # Initialize the environment
    env = EmptyEnv(size=5, render_mode="rgb_array")

    # Define target objs
    target_obj_1, target_obj_pos_1 = Key("blue"), (2, 1)
    target_obj_2, target_obj_pos_2 = Box("grey"), (1, 2)

    # Set predefined grid for testing
    def custom_gen_grid(width, height):
        # Create grid
        custom_grid = Grid(width, height)

        # Define walls
        custom_grid.horz_wall(0, 0)
        custom_grid.horz_wall(0, height - 1)
        custom_grid.vert_wall(0, 0)
        custom_grid.vert_wall(width - 1, 0)

        # Set target objs
        custom_grid.set(target_obj_pos_1[0], target_obj_pos_1[1], target_obj_1)
        custom_grid.set(target_obj_pos_2[0], target_obj_pos_2[1], target_obj_2)

        env.grid = custom_grid
        env.agent_pos = (1, 1)
        env.agent_dir = 0
    env._gen_grid = custom_gen_grid
    env.reset()

    # Modify reward func for target_obj_1
    env = modify_env_reward(env, predicate="holding", target_obj=target_obj_1, target_coords=target_obj_pos_1)

    # Move agent to target_obj_1
    obs, reward, terminated, truncated, info = env.step(env.actions.pickup)
    assert reward > 0

    # Modify reward func for target_obj_2
    env = modify_env_reward(env, predicate="holding", target_obj=target_obj_2, target_coords=target_obj_pos_2)

    # Move agent to target_obj_2
    env.step(env.actions.drop)
    env.step(env.actions.right)
    obs, reward, terminated, truncated, info = env.step(env.actions.pickup)
    assert reward > 0

    env.reset()

    # Modify reward func for target_obj_1
    env = modify_env_reward(env, predicate="holding", target_obj=target_obj_1)

    # Move agent to target_obj_1
    obs, reward, terminated, truncated, info = env.step(env.actions.pickup)
    assert reward > 0

    # Modify reward func for target_obj_2
    env = modify_env_reward(env, predicate="holding", target_obj=target_obj_2)

    # Move agent to target_obj_2
    env.step(env.actions.drop)
    env.step(env.actions.right)
    obs, reward, terminated, truncated, info = env.step(env.actions.pickup)
    assert reward > 0

def test_modify_env_unlocked_reward():
    # Initialize the environment
    env = EmptyEnv(size=5, render_mode="rgb_array")

    # Define target and key objs
    key_obj_1, key_obj_pos_1 = Key("blue"), (2, 1)
    target_obj_1, target_obj_pos_1 = Door("blue"), (3, 1)
    key_obj_2, key_obj_pos_2 = Key("grey"), (1, 2)
    target_obj_2, target_obj_pos_2 = Door("grey"), (1, 3)

    # Set predefined grid for testing
    def custom_gen_grid(width, height):
        # Create grid
        custom_grid = Grid(width, height)

        # Define walls
        custom_grid.horz_wall(0, 0)
        custom_grid.horz_wall(0, height - 1)
        custom_grid.vert_wall(0, 0)
        custom_grid.vert_wall(width - 1, 0)

        # Set target and key objs
        target_obj_1.is_open = False
        custom_grid.set(target_obj_pos_1[0], target_obj_pos_1[1], target_obj_1)
        custom_grid.set(key_obj_pos_1[0], key_obj_pos_1[1], key_obj_1)
        target_obj_2.is_open = False
        custom_grid.set(target_obj_pos_2[0], target_obj_pos_2[1], target_obj_2)
        custom_grid.set(key_obj_pos_2[0], key_obj_pos_2[1], key_obj_2)

        env.grid = custom_grid
        env.agent_pos = (1, 1)
        env.agent_dir = 0
    env._gen_grid = custom_gen_grid
    env.reset()

    # Modify reward func for target_obj_1
    env = modify_env_reward(env, predicate="unlocked", target_obj=target_obj_1, target_coords=target_obj_pos_1)

    env.step(env.actions.pickup)
    env.step(env.actions.forward)
    obs, reward, terminated, truncated, info = env.step(env.actions.toggle)
    assert reward > 0
    env.step(env.actions.drop)

    # Modify reward func for target_obj_2
    env = modify_env_reward(env, predicate="unlocked", target_obj=target_obj_2, target_coords=target_obj_pos_2)

    env.step(env.actions.right)
    env.step(env.actions.right)
    env.step(env.actions.forward)
    env.step(env.actions.forward)
    env.step(env.actions.right)
    env.step(env.actions.right)
    env.step(env.actions.drop)
    env.step(env.actions.right)
    env.step(env.actions.pickup)
    env.step(env.actions.forward)

    obs, reward, terminated, truncated, info = env.step(env.actions.toggle)
    assert reward > 0

    env.reset()

    # Modify reward func for target_obj_1
    env = modify_env_reward(env, predicate="unlocked", target_obj=target_obj_1)

    env.step(env.actions.pickup)
    env.step(env.actions.forward)
    obs, reward, terminated, truncated, info = env.step(env.actions.toggle)
    assert reward > 0
    env.step(env.actions.drop)

    # Modify reward func for target_obj_2
    env = modify_env_reward(env, predicate="unlocked", target_obj=target_obj_2)

    env.step(env.actions.right)
    env.step(env.actions.right)
    env.step(env.actions.forward)
    env.step(env.actions.forward)
    env.step(env.actions.right)
    env.step(env.actions.right)
    env.step(env.actions.drop)
    env.step(env.actions.right)
    env.step(env.actions.pickup)
    env.step(env.actions.forward)

    obs, reward, terminated, truncated, info = env.step(env.actions.toggle)
    assert reward > 0

def test_modify_env_reward(env: MiniGridEnv, src: DagNode, dest: DagNode, terminate_on_success: bool = False) -> MiniGridEnv:
    """
    Modifies environment to set up a specific subtask and reward function.
    
    Args:
        env: The MiniGrid environment
        src: Source state node
        dest: Destination state node
        terminate_on_success: If True, environment will terminate when goal is reached
                              If False, environment will continue running after goal
    
    Returns:
        Modified environment
    """
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

    # Validate dest node logic (for reaching the goal)
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
        # Compute previous distance if a destination coordinate is provided.
        if dest.coord is not None:
            prev_distance = abs(env.agent_pos[0] - dest.coord[0]) + abs(env.agent_pos[1] - dest.coord[1])
        else:
            prev_distance = None

        # Execute the original step action.
        obs, original_reward, terminated, truncated, info = original_step(env, action)

        # --- Check for Lava ---
        # Before applying any further rewards, check if the new cell is lava.
        current_tile = env.grid.get(env.agent_pos[0], env.agent_pos[1])
        # Assuming the lava tile's type is "lava". You could also check via isinstance if you have a Lava class.
        if current_tile is not None and getattr(current_tile, "type", None) == "lava":
            # Agent hit lava; assign 0 reward, mark failure, and do not add shaping reward.
            info["is_success"] = False
            return obs, 0, terminated, truncated, info

        # Flag to track if goal is reached
        goal_reached = False
        
        # Check for success based on the destination predicate.
        if dest.predicate == "at":
            ax, ay = env.agent_pos
            if dest.coord is not None:
                tx, ty = dest.coord
                if ax == tx and ay == ty:
                    if dest.worldObj is None or (
                        env.grid.get(tx, ty).encode()[0] == dest.worldObj.encode()[0] and
                        env.grid.get(tx, ty).encode()[1] == dest.worldObj.encode()[1]
                    ):
                        reward = env._reward()
                        goal_reached = True

            elif dest.worldObj is not None:
                grid_enc = env.grid.encode()
                target_obj_enc = dest.worldObj.encode()
                for i in range(env.grid.width):
                    for j in range(env.grid.height):
                        if (grid_enc[i][j][0] == target_obj_enc[0] and
                            grid_enc[i][j][1] == target_obj_enc[1]):
                            reward = env._reward()
                            goal_reached = True

        elif dest.predicate == "holding":
            if env.carrying is not None:
                if env.carrying.color == dest.worldObj.color and env.carrying.type == dest.worldObj.type:
                    if dest.coord is not None:
                        ax, ay = env.agent_pos
                        tx, ty = dest.coord
                        # Check if the agent is adjacent to the destination coordinate.
                        dx = [1, 0, -1, 0]
                        dy = [0, 1, 0, -1]
                        for i in range(4):
                            if (ax + dx[i] == tx and ay + dy[i] == ty):
                                reward = env._reward()
                                goal_reached = True

        elif dest.predicate == "unlocked":
            if dest.coord is not None:
                tx, ty = dest.coord
                door = env.grid.get(tx, ty)
                # Check if agent is standing at the door position and the door is unlocked
                ax, ay = env.agent_pos
                if ax == tx and ay == ty and door is not None and isinstance(door, Door) and door.is_open and (
                    dest.worldObj is None or door.color == dest.worldObj.color
                ):
                    reward = env._reward()
                    goal_reached = True
            elif dest.worldObj is not None:
                grid_enc = env.grid.encode()
                target_obj_enc = dest.worldObj.encode()
                for i in range(env.grid.width):
                    for j in range(env.grid.height):
                        door = env.grid.get(i, j)
                        if door is not None and isinstance(door, Door) and door.is_open and door.color == dest.worldObj.color:
                            reward = env._reward()
                            goal_reached = True

        # Set info["is_success"] if goal is reached
        if goal_reached:
            info["is_success"] = True
            # Only terminate if terminate_on_success is True
            if terminate_on_success:
                terminated = True
            else:
                terminated = False  # Ensure we don't terminate
        else:
            # Only add shaping reward if not on lava and if we have a destination coordinate.
            reward = 0
            if dest.coord is not None and prev_distance is not None:
                curr_distance = abs(env.agent_pos[0] - dest.coord[0]) + abs(env.agent_pos[1] - dest.coord[1])
                # Coefficient that scales the shaping reward—adjust as needed.
                coefficient = 0.01
                shaping_reward = coefficient * (prev_distance - curr_distance)
                reward += shaping_reward

            # Ensure the info dictionary always has an "is_success" key.
            if "is_success" not in info:
                info["is_success"] = False

        return obs, reward, terminated, truncated, info

    env.step = modified_step
    return env