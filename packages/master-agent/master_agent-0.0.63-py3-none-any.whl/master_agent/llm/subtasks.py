import json
import re
from .client import LlmClient
from .utils import strip_code_fences

class SubtasksValidationError(Exception):
    """Custom exception for validation errors in subtask paths.
    
    Attributes:
        errors (list[str]): List of validation error messages
    """
    def __init__(self, errors: list[str]):
        self.errors = errors

class SubtasksGenerator:
    """Generates and validates sequences of subtasks for navigation in a grid environment.
    
    Uses LLM to generate valid paths from start to goal states, with proper validation
    of state transitions and object interactions.
    """
    def __init__(self, llm_client: LlmClient, custom_prompt_func=None):
        """Initialize generator with LLM client for path generation.
        
        Args:
            llm_client: Client for making LLM API calls
            custom_prompt_func: 
            Optional function to generate custom prompts (reference self.create_gen_subtasks_prompt)
            def create_gen_subtasks_prompt(self, objects: list[str]) -> str
        """
        self.llm_client = llm_client
        self.create_gen_subtasks_prompt = custom_prompt_func or self.create_gen_subtasks_prompt

    def gen_subtask_paths(self, objects: list[str], custom_prompt: str | None = None) -> list[list[str]]:
        """Generate valid paths from start to goal using provided objects.
        
        Args:
            objects: List of object names available in the environment
            custom_prompt: Optional custom prompt for LLM
        Returns:
            List of valid paths, where each path is a list of state strings
            
        Raises:
            Exception: If LLM returns empty response or no paths
        """
        content =  self.llm_client.complete([
            {
            "role": "system",
            "content": "You are a reasoning agent that generates paths from initial states to goal states in a grid-based environment. Each path is a sequence of symbolic states. Output JSON only."
            },
            {
            "role": "user",
            "content": f'{self.create_gen_subtasks_prompt(objects)}'
            },
        ])

        if not content.strip():
            raise Exception("No response from LLM")

        stripped_content = strip_code_fences(content)

        data = json.loads(stripped_content)
        paths = data.get("paths")
        
        if not paths or len(paths) == 0:
            raise Exception("No paths generated")
        
        # self.validate_subtask_paths(paths, objects)
        
        return paths
    
    def validate_subtask_paths(self, paths: list[list[str]], objects: list[str]) -> None:
        """Validate generated paths against domain rules and constraints.
        
        Checks:
        - Non-empty paths
        - Valid start/goal states
        - Valid state predicates
        - Logical key/door relationships
        
        Args:
            paths: List of paths to validate
            objects: List of valid object names
            
        Raises:
            SubtasksValidationError: If any validation checks fail
        """
        errors = []
        start_state = "At(OutsideRoom)"
        goal_state = "At(Green_Goal)"
        
        # Create patterns based on allowed predicates and objects
        valid_patterns = [
            re.compile(r"At\(({}|OutsideRoom|Green_Goal|Wall)\)".format("|".join(objects))),
            re.compile(r"Holding\(({})\)".format("|".join(objects))),
            re.compile(r"Unlocked\(({})\)".format("|".join(objects)))
        ]

        for idx, path in enumerate(paths):
            if not path:
                errors.append(f"Path {idx + 1} is empty.")
                continue
                
            if path[0] != start_state:
                errors.append(f"Path {idx + 1} does not start with {start_state}.")
                
            if path[-1] != goal_state:
                errors.append(f"Path {idx + 1} does not end with {goal_state}.")
                
            # Validate each state matches allowed patterns
            for state in path:
                if not any(pattern.fullmatch(state) for pattern in valid_patterns):
                    errors.append(f"Path {idx + 1} contains invalid state: {state}")
                    
            # Count keys and doors
            keys = sum(1 for state in path if "Holding" in state)
            doors = sum(1 for state in path if "Unlocked" in state)
            if doors > keys:
                errors.append(f"Path {idx + 1}: More doors unlocked than keys picked up.")

        if errors:
            raise SubtasksValidationError(errors)
    
    def create_gen_subtasks_prompt(self, objects: list[str]) -> str:
        """Create prompt for LLM to generate valid paths.
        
        Args:
            objects: List of object names to include in prompt
            
        Returns:
            Formatted prompt string for LLM
        """
        example_json = '''{"paths": [[
      "At(OutsideRoom)",
      "Holding(Key1)", 
      "Unlocked(Door)",
      "At(Green_Goal)"
    ],[
      "At(OutsideRoom)",
      "Holding(Key2)",
      "Unlocked(Door)", 
      "At(Green_Goal)"
    ],[
      "At(OutsideRoom)",
      "Holding(Key3)",
      "Unlocked(Door)",
      "At(Green_Goal)"
    ],[
      "At(OutsideRoom)",
      "At(Wall)",
      "At(Green_Goal)"
    ]]}'''

        return f'''Generate a handful of unique DAGs showing multiple paths from the start to the goal. A "state" is any conjunction of these ground predicates:

Start: OutsideRoom, Goal: Green_Goal
Objects: {", ".join(objects)}
Predicates: At(?), Holding(?), Unlocked(?)
Include intermediate states logically required to move from start to goal, respecting object interactions and valid environment constraints. 

Output the DAGs in JSON as members of a 2D array named "paths", with no extra text. For example:
{example_json}'''