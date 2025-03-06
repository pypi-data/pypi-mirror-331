from envs import grid_world_object_mapping
from master_agent.rl.utils.string_parser import extract_pred_obj

class DagNode:
    def __init__(self, predicate, worldObj=None, coord=None):
        self.predicate = predicate  # Store the predicate as a string
        self.worldObj = worldObj    # Reference to a MiniGrid world object
        self.coord = coord          # Tuple of coordinates (x, y)

class DAG:
    def __init__(self, input_text_arr):
        """
        Initialize the DAG using an input array of arrays of strings.
        """
        self.adj_list, self.nodes = self._create_dag(input_text_arr)

    def _fill_adj_list(self, pred_obj_dict, input_dict, input_text_arr):
        """
        Populate the adjacency list (input_dict) by processing the input_text_arr.
        """
        for i in range(len(input_text_arr)):
            for j in range(1, len(input_text_arr[i])):
                prev_key = extract_pred_obj(input_text_arr[i][j - 1])
                key = extract_pred_obj(input_text_arr[i][j])
                
                prev_node_num = pred_obj_dict[prev_key]
                connecting_node = pred_obj_dict[key]
                if connecting_node not in input_dict[prev_node_num]:
                    input_dict[prev_node_num].append(connecting_node)

    def _create_dag(self, input_text_arr) -> tuple[dict[int, list[int]], dict[int, DagNode]]:
        """
        Build the DAG from the input text array.
        
        Returns:
            adj_list: A dictionary mapping each node id to a list of connected node ids.
            nodes: A dictionary mapping node id to its corresponding DagNode.
        """
        pred_obj_dict = {}
        node_count = 0
        adj_list = {}
        int_to_node_dict = {}

        # Create node representations based on the input text.
        for i in range(len(input_text_arr)):
            for j in range(len(input_text_arr[i])):
                pred, obj = extract_pred_obj(input_text_arr[i][j])
                if (pred, obj) not in pred_obj_dict:
                    # First interaction with this node; create a new DagNode.
                    worldObj, coord = grid_world_object_mapping[obj]
                    int_to_node_dict[node_count] = DagNode(pred, worldObj, coord)
                    pred_obj_dict[(pred, obj)] = node_count
                    node_count += 1

        # Initialize the adjacency list for each node.
        for i in range(node_count):
            adj_list[i] = []

        # Populate the adjacency list based on the order of elements in the input.
        self._fill_adj_list(pred_obj_dict, adj_list, input_text_arr)

        return adj_list, int_to_node_dict
