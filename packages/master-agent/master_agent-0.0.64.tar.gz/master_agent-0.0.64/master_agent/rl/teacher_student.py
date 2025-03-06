from .utils.common import *
from envs.subtask import modify_env_reward
from envs.complexEnv import ComplexEnv
from rl import DAG, MinigridFeaturesExtractor, LEARNING_RATE, NUM_STEPS, ETA, EPSILON, EPISODES, MU
from gymnasium.wrappers import RecordVideo
import os
import time


class TeacherStudent:
    def __init__(self, input_data, render_mode="rgb_array"):
        """
        Initialize the TeacherStudent framework.
        
        Args:
            input_data (list): List of state predicates for graph creation
            render_mode (str): Rendering mode for environments
        """
        self.render_mode = render_mode
        
        # Create models directory if it doesn't exist
        os.makedirs('./master_agent/rl/models', exist_ok=True)
        
        # Environment setup to pass to the CNN
        self.policy_kwargs = dict(
            features_extractor_class=MinigridFeaturesExtractor,
            features_extractor_kwargs=dict(features_dim=128),
        )
        
        # Convert to a graph
        # adjacency list mapping of integers
        # int_to_node_dict is a dictionary letting us know what each integer represents as a node
        self.dag = DAG(input_data)
        
        # Initialize collections
        self.active_tasks = []      # active tasks containing tuples (q,p)
        self.learned_tasks = []     # learned tasks containing tuples (q,p)
        self.discarded_tasks = []   # discarded tasks containing tuples (q,p)
        
        # Initialize policies and Q-values
        self.edge_policy = {}
        self.teacher_Q_values = {}
        
        # Initialize all policies and Q-values
        for q in self.dag.adj_list:
            for p in self.dag.adj_list[q]:
                self.edge_policy[(q, p)] = self._create_ppo_policy((q, p))
                self.teacher_Q_values[(q, p)] = float("-inf")

    def _create_env(self, src_node, dest_node, edge):
        """
        Create an environment for a specific subtask.
        
        Args:
            src_node: Source node object
            dest_node: Destination node object
            edge: Tuple of (source_idx, dest_idx)
            
        Returns:
            Environment instance
        """
        # Initialize the base environment
        base_env = ComplexEnv(render_mode=self.render_mode)
        
        # Change the environment based on the src and dest node
        task_env = modify_env_reward(base_env, src_node, dest_node, terminate_on_success=True)
        
        # Wrap the environment for image-based observations
        task_env = ImgObsWrapper(task_env)
        
        # Set up video recording
        folder = "./master_agent/rl/training_videos"
        extension = f"/policy{edge[0]}{edge[1]}"
        folder += extension
        
        os.makedirs(folder, exist_ok=True)
        # Record videos every n episodes
        task_env = RecordVideo(
            task_env,
            video_folder=folder,
            step_trigger=lambda step_count: step_count % 100_000 == 0
        )
        
        return task_env

    @staticmethod
    def _linear_schedule(initial_value):
        """
        Linear learning rate schedule.
        
        Args:
            initial_value: Initial learning rate.
            
        Returns:
            Function that computes the learning rate based on remaining progress.
        """
        def func(progress_remaining):
            # progress_remaining goes from 1 (start) to 0 (end)
            return progress_remaining * initial_value
        return func

    def _create_ppo_policy(self, edge):
        """
        Create a PPO policy for a specific edge.
        
        Args:
            edge: Tuple of (source_idx, dest_idx)
            
        Returns:
            PPO model
        """
        src, dest = edge
        
        # Reference to the Node class that contains (predicate, worldObj, coord)
        src_node = self.dag.nodes[src]
        dest_node = self.dag.nodes[dest]
        
        # Creating a unique environment based on a edge src and dest
        task_env = self._create_env(src_node, dest_node, edge)
        
        tensor_board = "./master_agent/rl/logs/tensor_board"
        os.makedirs(tensor_board, exist_ok=True)
        
        model = PPO(
            policy="MlpPolicy",
            env=task_env,
            learning_rate=self._linear_schedule(0.0003),  # Use a linear schedule for learning rate annealing
            n_steps=5000,            # Update after 5000 steps
            batch_size=64,           # You can adjust this based on your needs
            n_epochs=60,             # Number of epochs for each update
            gamma=0.99,
            clip_range=0.2,
            target_kl=0.04,  # Higher value to reduce frequent updates
            ent_coef=0.125,
            verbose=1,
            tensorboard_log=tensor_board
        )
        
        return model

    def _student_learn(self, policy, edge):
        """
        Trains the policy and evaluates its performance.
        
        Args:
            policy: PPO policy
            edge: Tuple of (source_idx, dest_idx)
            
        Returns:
            tuple: (average_return, average_success_rate)
        """
        returns = []
        success_count = 0
        
        # Retrieve the environment from the policy and train the agent
        task_env = policy.get_env()
        log_name = f"policy{edge[0]}{edge[1]}"
        policy.learn(total_timesteps=NUM_STEPS, tb_log_name=log_name, reset_num_timesteps=False)
        
        task_env = policy.get_env()
        obs = task_env.reset()
        
        for _ in range(EPISODES):
            sum_reward = 0
            done = False
            episode_success = False
            # Run one full episode.
            while not done:
                action, _ = policy.predict(obs)
                obs, reward, done, info = task_env.step(action)
                sum_reward += reward
            # After the episode ends, check if the success flag was set.
            for info_dict in info:
                if info_dict.get("is_success", False):
                    success_count += 1
            returns.append(sum_reward)
            obs = task_env.reset()
        
        avg_return = np.mean(returns)
        avg_success_rate = success_count / EPISODES
        return avg_return, avg_success_rate

    def _epsilon_action(self, eps=0.1):
        """
        Select an action using epsilon-greedy strategy.
        
        Args:
            eps: Epsilon value for exploration
            
        Returns:
            tuple: Selected (source_idx, dest_idx) edge
        """
        # p is a probability (0,1)
        p = np.random.random()
        
        # Find the key with the largest Q-value
        # only gets a list of highest q values that are in the active list
        filtered_q_values = {k: v for k, v in self.teacher_Q_values.items() if k in self.active_tasks}
        if not filtered_q_values:
            random_index = np.random.choice(len(self.active_tasks))
            return self.active_tasks[random_index]
            
        max_key = max(filtered_q_values, key=lambda k: filtered_q_values[k])
        
        if p < 1 - eps:
            return max_key
        else:
            random_index = np.random.choice(len(self.active_tasks))
            return self.active_tasks[random_index]

    def find_path_to_goal(self):
        """
        Find a path from start node to goal node using DFS.
        
        Returns:
            list: Path of node indices from start to goal, or None if no path exists
        """
        # Print node information for debugging
        for node_idx, node in self.dag.nodes.items():
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
            node = self.dag.nodes[current]
                
            # Check worldObj type (if worldObj exists)
            if node.worldObj and hasattr(node.worldObj, '__class__') and node.worldObj.__class__.__name__ == 'Goal':
                print(f"Found goal object at index {current}")
                return path
                
            # Add neighbors to stack in reverse order 
            neighbors = self.dag.adj_list.get(current, [])
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    stack.append((neighbor, new_path))
        
        # If we get here, no path was found
        print("No path to goal found")
        return None

    @staticmethod
    def path_to_edges(path):
        """
        Convert a path of nodes to a list of edges.
        
        Args:
            path: List of node indices
            
        Returns:
            list: List of edge tuples (src, dest)
        """
        if path is None or len(path) < 2:
            return []
        return [(path[i], path[i+1]) for i in range(len(path)-1)]

    def human_mode_demo_path(self, final_path_edges):
        """
        Demonstrate the learned path while recording a video.
        
        Args:
            final_path_edges: List of edges to demonstrate.
        """
        if not final_path_edges:
            print("No path to demonstrate!")
            return

        # Create demos directory if it doesn't exist
        demo_folder = "./master_agent/rl/demos"
        os.makedirs(demo_folder, exist_ok=True)

        # Create base environment with rgb_array rendering (needed for video recording)
        base_env = ComplexEnv(render_mode="rgb_array")
        video_env = RecordVideo(
            base_env,
            video_folder=demo_folder,
            episode_trigger=lambda _: True,
            name_prefix="full_path_demo"
        )
        wrapped_env = ImgObsWrapper(video_env)

        # Pre-load all policies from saved models
        policies = {}
        for src_idx, dest_idx in final_path_edges:
            policy_path = f"./master_agent/rl/models/PPO_{src_idx}_{dest_idx}_.pth"
            try:
                policy = PPO.load(policy_path)
                policies[(src_idx, dest_idx)] = policy
            except Exception as e:
                print(f"Error loading policy {src_idx}-{dest_idx}: {e}")
                return

        # Configure the first subtask
        current_subtask = 0
        src_idx, dest_idx = final_path_edges[current_subtask]
        src_node = self.dag.nodes[src_idx]
        dest_node = self.dag.nodes[dest_idx]
        modify_env_reward(
            base_env,
            src_node,
            dest_node,
            terminate_on_success=False
        )

        obs, _ = wrapped_env.reset()
        print("\n===== RECORDING DEMO VIDEO =====")
        print(f"Saving to: {demo_folder}")

        # Execute each subtask sequentially
        while current_subtask < len(final_path_edges):
            src_idx, dest_idx = final_path_edges[current_subtask]
            src_node = self.dag.nodes[src_idx]
            dest_node = self.dag.nodes[dest_idx]
            policy = policies[(src_idx, dest_idx)]
            
            print(f"\nExecuting subtask {current_subtask+1}: {src_node.predicate} → {dest_node.predicate}")
            subtask_complete = False
            max_steps = 500
            step_count = 0
            
            while not subtask_complete and step_count < max_steps:
                action, _ = policy.predict(obs)
                obs, reward, terminated, truncated, info = wrapped_env.step(action)
                step_count += 1
                
                if info.get("is_success", False):
                    subtask_complete = True
                    print(f"Subtask {current_subtask+1} completed in {step_count} steps!")
                    current_subtask += 1
                    
                    if current_subtask < len(final_path_edges):
                        next_src_idx, next_dest_idx = final_path_edges[current_subtask]
                        next_src_node = self.dag.nodes[next_src_idx]
                        next_dest_node = self.dag.nodes[next_dest_idx]
                        is_last = current_subtask == len(final_path_edges) - 1
                        modify_env_reward(
                            base_env,
                            next_src_node,
                            next_dest_node,
                            terminate_on_success=is_last
                        )
                    break
                
                if terminated or truncated:
                    print(f"Subtask {current_subtask+1} failed after {step_count} steps")
                    return

        if current_subtask == len(final_path_edges):
            print("\n🎉 Full path completed successfully!")
            print(f"Demo video saved to {demo_folder}")

        wrapped_env.close()

    def train(self):
        """
        Train the Teacher-Student framework.
        """
        # Record the start time
        start_time = time.time()

        # Start of algorithm
        # Since we always start at node 0.
        # Add the connecting edges from node 0.
        for connecting_node in self.dag.adj_list[0]:
            self.active_tasks.append((0, connecting_node))
            # Set the now active_tasks teacher q values to 0
            self.teacher_Q_values[(0, connecting_node)] = 0
        
        while self.active_tasks:
            # Sample a task using epsilon greedy
            task = self._epsilon_action(EPSILON)
            print("Task selected" + " " + str(task))
            
            # the policy the agent is going to train on (q,p)
            policy = self.edge_policy[task]
            avg_returns, avg_success_rate = self._student_learn(policy, task)
            
            # Calculate Q-value delta
            old_Q = self.teacher_Q_values[task]
            new_Q = (LEARNING_RATE * avg_returns) + ((1 - LEARNING_RATE) * old_Q)
            delta = abs(new_Q - old_Q)
            self.teacher_Q_values[task] = new_Q  # Update Q-value
            
            print(f"Task {task} - Success: {avg_success_rate:.2f}, Return: {avg_returns:.2f}, Q-value: {self.teacher_Q_values[task]:.2f}")
            
            # check for convergence 
            if avg_success_rate >= ETA and delta < MU:
                src = task[0]
                dest = task[1]
                print("Task converged" + " " + str(task))
                model_path = f"./master_agent/rl/models/PPO_{src}_{dest}_.pth"
                policy.save(model_path)
                print(f"Saved converged policy to {model_path}")
                
                # a task has converged
                # append the task to the set of learned task
                self.learned_tasks.append(task)
                
                # remove from the set of active task
                self.active_tasks.remove(task)
                
                # reset the q values of all the active task, to have equal
                # chance as earlier task have been training for more time
                for (q, p) in self.active_tasks:
                    self.teacher_Q_values[(q, p)] = 0
                
                dest = task[1]
                # add all connecting node from the destination node to the active task
                for connecting_node in self.dag.adj_list[dest]:
                    self.active_tasks.append((dest, connecting_node))
                    # set the now active_tasks teacher q values to 0
                    self.teacher_Q_values[(dest, connecting_node)] = 0
                
                # set the converged task to no longer train
                self.teacher_Q_values[task] = float("-inf")
                
                # find the sub-tasks that can be discarded
                # logic is to remove tasks that training to reach the same destination p 
                # when a more efficient path is found
                for (q, p) in self.active_tasks.copy():
                    if p == dest:
                        self.active_tasks.remove((q, p))
                        self.teacher_Q_values[(q, p)] = float("-inf")
                        self.dag.adj_list[q].remove(p)
                        self.discarded_tasks.append((q, p))
                # after removal
                print("After removal this is the active_tasks list: ")
                print(self.active_tasks)
        
        # Calculate and record total training time
        end_time = time.time()
        total_training_time = end_time - start_time
        
        print("Completed training")
        print(f"Total Training Time: {total_training_time:.2f} seconds")
        self._print_summary()
        
    def _print_summary(self):
        """Print a summary of the learning results."""
        print("\n===== LEARNING SUMMARY =====")
        print("\nAdjacency List (Learned Graph):")
        for vertex, neighbors in self.dag.adj_list.items():
            print(f"{vertex} : {neighbors}")
        
        print("\nLearned Tasks:")
        print(self.learned_tasks)
        
        print("\nDiscarded Tasks:")
        print(self.discarded_tasks)
    
    def demo_learned_path(self):
        """Find and demonstrate the learned path to the goal."""
        # Get a learned path for the learned tasks that reach the end goal
        path = self.find_path_to_goal()
        final_path_edges = self.path_to_edges(path)
        
        print("\nPath to Goal:", path)
        print("Path Edges:", final_path_edges)
        
        # --- Run Human Mode Demonstration ---
        # This demonstration will chain the learned policies in a single continuous episode.
        self.human_mode_demo_path(final_path_edges)