import os
from dotenv import load_dotenv
from .identify import TileIdentifier
from .client import LlmClient
from envs.complexEnv import ComplexEnv

def test_tile_identifier():
    load_dotenv()

    llm_api_key = os.getenv('LLM_API_KEY')
    assert llm_api_key != None
    llm_base_url = os.getenv('LLM_BASE_URL')
    assert llm_base_url != None
    llm_model = os.getenv('LLM_MODEL')
    assert llm_model != None

    llm_client = LlmClient(llm_api_key, llm_model, llm_base_url)

    identifier = TileIdentifier(llm_client)

    env = ComplexEnv(render_mode='rgb_array', highlight=False) # Removing highlight for accurate tileset representation
    env.reset()

    unidentified_tileset = identifier.parse_tileset(env.render())
    
    identifier.validate_unidentified_tileset(unidentified_tileset, env)