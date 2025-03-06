import re

def strip_code_fences(text: str) -> str:
    # Remove trailing ``` common for our JSON LLM-guided DAG list
    pattern = r"^```(?:json)?\s*|\s*```$"
    return re.sub(pattern, "", text.strip())