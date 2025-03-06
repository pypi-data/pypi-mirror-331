import os
from dotenv import load_dotenv
from llm.client import LlmClient
from llm.subtasks import SubtasksGenerator

def test_subtasks_gen_subtasks_prompt():
    load_dotenv()

    llm_api_key = os.getenv('LLM_API_KEY')
    assert llm_api_key != None
    llm_base_url = os.getenv('LLM_BASE_URL')
    assert llm_base_url != None
    llm_model = os.getenv('LLM_MODEL')
    assert llm_model != None

    llm_client = LlmClient(llm_api_key, llm_model, llm_base_url)

    subtasks_gen = SubtasksGenerator(llm_client)

    prompt = subtasks_gen.create_gen_subtasks_prompt(["Key1", "Key2", "Key3"])

    assert prompt != None
    assert prompt != ""

    print(prompt)

def test_subtasks_custom_gen_subtasks_prompt():
    load_dotenv()

    llm_api_key = os.getenv('LLM_API_KEY')
    assert llm_api_key != None
    llm_base_url = os.getenv('LLM_BASE_URL')
    assert llm_base_url != None
    llm_model = os.getenv('LLM_MODEL')
    assert llm_model != None

    llm_client = LlmClient(llm_api_key, llm_model, llm_base_url)
    
    def custom_prompt_func(objects):
        return f"Generate paths for {objects}"

    subtasks_gen = SubtasksGenerator(llm_client, custom_prompt_func=custom_prompt_func)

    prompt = subtasks_gen.create_gen_subtasks_prompt(["Key1", "Key2", "Key3"])

    assert prompt != None
    assert prompt == custom_prompt_func(["Key1", "Key2", "Key3"])

    print(prompt)

def test_subtasks_gen_subtasks():
    load_dotenv()

    llm_api_key = os.getenv('LLM_API_KEY')
    assert llm_api_key != None
    llm_base_url = os.getenv('LLM_BASE_URL')
    assert llm_base_url != None
    llm_model = os.getenv('LLM_MODEL')
    assert llm_model != None

    llm_client = LlmClient(llm_api_key, llm_model, llm_base_url)

    subtasks_gen = SubtasksGenerator(llm_client)

    objects = ["Key1", "Key2", "Key3", "Door1", "Door2"]

    subtask_paths = subtasks_gen.gen_subtask_paths(objects)
    assert subtask_paths != None
    print(subtask_paths)