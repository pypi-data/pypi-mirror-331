from openai import OpenAI

class LlmClient():
    """Client for interacting with OpenAI language models.
    
    Provides methods for sending prompts and completing conversations using
    OpenRouter's chat completion API.
    """
    def __init__(self, api_key: str, model: str = "openai/gpt-4o", base_url: str = "https://openrouter.ai/api/v1"):
        """Initialize LLM client with API credentials and model settings.
        
        Args:
            api_key: OpenRouter API key for authentication
            model: Name of the model to use for completions
            base_url: Base URL for the LLM API endpoint
        """
        self.llm: OpenAI = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model
    
    def prompt(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send a single prompt to the LLM with optional system context.
        
        Args:
            prompt: The user prompt to send
            system_prompt: Optional system context message
            
        Returns:
            The model's response text
        """
        messages = []
        if system_prompt is not None:
            messages.append({
                "role": "system", 
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })
        return self.llm.chat.completions.create(
            model=self.model,
            messages=messages
        ).choices[0].message.content
    
    def complete(self, messages) -> str:
        """Complete a conversation given a list of message objects.
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            The model's response text
        """
        return self.llm.chat.completions.create(
            model=self.model,
            messages=messages
        ).choices[0].message.content