from .utils.common import *
from minigrid.core.world_object import Key, Door, Goal
from envs.subtask import modify_env_reward
from envs.complexEnv import ComplexEnv
from rl import DagNode, MinigridFeaturesExtractor

def test_run():
    policy_kwargs = dict(
    features_extractor_class=MinigridFeaturesExtractor,
    features_extractor_kwargs=dict(features_dim=128),
    )
    

    env = ComplexEnv(render_mode="rgb_array")

    src_node = DagNode("holding", Key("yellow"), (1,2))
    dest_node = DagNode("unlocked", Door("yellow"), (4,3))
    env = modify_env_reward(env, src_node, dest_node)

    env = ImgObsWrapper(env)
    model = PPO("CnnPolicy", env, policy_kwargs=policy_kwargs, verbose=1)
    model.learn(25_000)

    # After training, perform rollout with human rendering
    eval_env = ComplexEnv(render_mode="human")
    # Apply the same reward modification as during training
    eval_env = modify_env_reward(eval_env, src_node, dest_node)
    # Apply the same observation wrapper used during training
    eval_env = ImgObsWrapper(eval_env)

    # Reset the environment
    obs, info = eval_env.reset()
    
    while True:
        # Get action from the model
        action, _ = model.predict(obs)
        # Step through the environment
        obs, reward, terminated, truncated, info = eval_env.step(action)
        # Render the current state
        eval_env.render()
        
        # End the episode if done
        if terminated or truncated:
            break
