from .utils.common import *
from rl import DAG
from envs.subtask import modify_env_reward
from envs.complexEnv import ComplexEnv
from gymnasium.wrappers import RecordVideo
from minigrid.wrappers import ImgObsWrapper  
from stable_baselines3 import PPO               
import os

def find_path_to_goal(adj_list: dict, int_to_node_dict: dict) -> list:
    """
    Performs a depth-first search (DFS) starting from node 0 until a goal node is reached.
    A goal node is one that has a worldObj of type Goal.

    Args:
        adj_list (dict): A dictionary mapping node indices to a list of neighbor indices.
        int_to_node_dict (dict): A dictionary mapping node indices to Node objects.

    Returns:
        list: A list of node indices representing the path from node 0 to the goal node.
              Returns None if no such path is found.
    """
    # Print node information for debugging
    for node_idx, node in int_to_node_dict.items():
        print(f"Node {node_idx}: Predicate={node.predicate}, Type={type(node.worldObj).__name__ if node.worldObj else 'None'}")
    
    # Stack-based iterative DFS implementation
    start_node = 0
    visited = set()
    stack = [(start_node, [start_node])]  # (current_node, path_so_far)
    
    while stack:
        current, path = stack.pop()
        
        if current in visited:
            continue
            
        visited.add(current)
        
        # Check if current node is a goal node
        node = int_to_node_dict[current]
        
        # Method 1: Check predicate string
        if "Green_Goal" in node.predicate:
            print(f"Found goal node at index {current} with predicate: {node.predicate}")
            return path
            
        # Method 2: Check worldObj type (if worldObj exists)
        if node.worldObj and hasattr(node.worldObj, '__class__') and node.worldObj.__class__.__name__ == 'Goal':
            print(f"Found goal object at index {current}")
            return path
            
        # Add neighbors to stack in reverse order (to maintain DFS behavior)
        neighbors = adj_list.get(current, [])
        for neighbor in reversed(neighbors):
            if neighbor not in visited:
                new_path = path + [neighbor]
                stack.append((neighbor, new_path))
    
    # If we get here, no path was found
    print("No path to goal found")
    return None

def path_to_edges(path: list) -> list:
    """
    Converts a path (list of node indices) into a list of edges.

    Args:
        path (list): A list of node indices.
        
    Returns:
        list: A list of tuples representing the edges (subtasks) along the path.
    """
    if path is None or len(path) < 2:
        return []
    return [(path[i], path[i+1]) for i in range(len(path)-1)]

def save_demo_video(final_path_edges, int_to_node_dict):
    """
    Save demonstration video of the learned path.
    
    Args:
        final_path_edges: List of edges to demonstrate.
        int_to_node_dict: Dictionary mapping node indices to Node objects.
    """
    if not final_path_edges:
        print("No path to demonstrate!")
        return
    
    # Create demos directory if it doesn't exist
    demo_folder = "./master_agent/rl/demos"
    os.makedirs(demo_folder, exist_ok=True)
    
    # Create base environment with rgb_array rendering
    base_env = ComplexEnv(render_mode="rgb_array")
    
    # Wrap with video recording
    video_env = RecordVideo(
        base_env,
        video_folder=demo_folder,
        episode_trigger=lambda _: True,  # Record every episode
        name_prefix="full_path_demo"
    )
    
    # Wrap for image observations
    wrapped_env = ImgObsWrapper(video_env)
    
    # Pre-load all policies to avoid loading during execution
    policies = {}
    for src_idx, dest_idx in final_path_edges:
        policy_path = f"./master_agent/rl/models/PPO_{src_idx}_{dest_idx}_.pth"
        try:
            policy = PPO.load(policy_path)
            policies[(src_idx, dest_idx)] = policy
        except Exception as e:
            print(f"Error loading policy {src_idx}-{dest_idx}: {e}")
            return
    
    # Initial reset with first subtask configuration
    current_subtask = 0
    src_idx, dest_idx = final_path_edges[current_subtask]
    src_node = int_to_node_dict[src_idx]
    dest_node = int_to_node_dict[dest_idx]
    
    # Configure first subtask - Important: terminate_on_success=False
    modify_env_reward(
        base_env,
        src_node,
        dest_node,
        terminate_on_success=False  # This prevents environment reset
    )
    
    # Initial reset only for first subtask
    obs, _ = wrapped_env.reset()
    
    print("\n===== RECORDING DEMO VIDEO =====")
    print(f"Saving to: {demo_folder}")
    
    # Main execution loop
    while current_subtask < len(final_path_edges):
        # Get current subtask details and policy
        src_idx, dest_idx = final_path_edges[current_subtask]
        src_node = int_to_node_dict[src_idx]
        dest_node = int_to_node_dict[dest_idx]
        policy = policies[(src_idx, dest_idx)]
        
        print(f"\nExecuting subtask {current_subtask+1}: {src_node.predicate} → {dest_node.predicate}")
        
        # Execute policy until subtask completion or failure
        subtask_complete = False
        max_steps = 500  # Safety limit to prevent infinite loops
        step_count = 0
        
        while not subtask_complete and step_count < max_steps:
            # Get action from policy
            action, _ = policy.predict(obs)
            
            # Take step in environment
            obs, reward, terminated, truncated, info = wrapped_env.step(action)
            step_count += 1
            
            # Check for subtask completion
            if info.get("is_success", False):
                subtask_complete = True
                print(f"Subtask {current_subtask+1} completed in {step_count} steps!")
                
                # Move to next subtask
                current_subtask += 1
                
                # Reconfigure environment for next subtask if there is one
                if current_subtask < len(final_path_edges):
                    next_src_idx, next_dest_idx = final_path_edges[current_subtask]
                    next_src_node = int_to_node_dict[next_src_idx]
                    next_dest_node = int_to_node_dict[next_dest_idx]
                    
                    # Last subtask can terminate on success
                    is_last = current_subtask == len(final_path_edges) - 1
                    
                    # Modify environment for next subtask without resetting
                    modify_env_reward(
                        base_env,
                        next_src_node,
                        next_dest_node,
                        terminate_on_success=is_last
                    )
                break
            
            # Handle environment termination (failure case)
            if terminated or truncated:
                print(f"Subtask {current_subtask+1} failed after {step_count} steps")
                return
    
    if current_subtask == len(final_path_edges):
        print("\n🎉 Full path completed successfully!")
        print(f"Demo video saved to {demo_folder}")
        
    # Close the environment to ensure video is saved
    wrapped_env.close()

def test_human_mode():
    """
    Test the human mode by loading a learned DAG and finding a path to the goal.
    """
    input_data = [
        ["At(OutsideRoom)", "Holding(Key1)", "Unlocked(Door)", "At(Green_Goal)"],
        ["At(OutsideRoom)", "Holding(Key2)", "Unlocked(Door)", "At(Green_Goal)"],
        ["At(OutsideRoom)", "Unlocked(Door)", "At(Green_Goal)"],
        ["At(OutsideRoom)", "Holding(Key2)", "At(Green_Goal)"]
    ]

    dag = DAG(input_data)

    adj_list = {
        0 : [1, 4],
        1 : [],
        2 : [3],
        3 : [],
        4 : [2]
    }

    # Get a learned path for the learned tasks that reach the end goal
    path = find_path_to_goal(adj_list, dag.nodes)
    final_path_edges = path_to_edges(path)

    save_demo_video(final_path_edges, dag.nodes)
