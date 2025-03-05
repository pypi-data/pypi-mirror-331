import os
from dotenv import load_dotenv
from llm.client import LlmClient

def test_client_prompt():
    load_dotenv()

    llm_api_key = os.getenv('LLM_API_KEY')
    assert llm_api_key != None
    llm_base_url = os.getenv('LLM_BASE_URL')
    assert llm_base_url != None
    llm_model = os.getenv('LLM_MODEL')
    assert llm_model != None

    client = LlmClient(llm_api_key, llm_model, llm_base_url)

    content = client.prompt("What is the meaning of life?")
    assert content != None
    assert content != ""

    print(content)

def test_client_complete():
    load_dotenv()

    llm_api_key = os.getenv('LLM_API_KEY')
    assert llm_api_key != None
    llm_base_url = os.getenv('LLM_BASE_URL')
    assert llm_base_url != None
    llm_model = os.getenv('LLM_MODEL')
    assert llm_model != None

    client = LlmClient(llm_api_key, llm_model, llm_base_url)

    content = client.complete([{"role":"user","content":"What is the meaning of life?"}])
    assert content != None
    assert content != ""

    print(content)