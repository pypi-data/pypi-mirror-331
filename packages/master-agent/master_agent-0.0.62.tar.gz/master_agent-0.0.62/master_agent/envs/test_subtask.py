from minigrid.envs import EmptyEnv
from minigrid.core.world_object import Box, Key, Door, Goal
from minigrid.core.grid import Grid
from envs import modify_env_reward
from PIL import Image

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
