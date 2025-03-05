from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='master_agent',
    version='0.0.62',
    author='Stevo Huncho',
    author_email='stevo@stevohuncho.com',
    description='A library providing the tools to solve complex environments in Minigrid using LgTS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="reinforcement learning, actor-critic, a2c, ppo, multi-processes, gpu, teacher student, ts",
    packages=["master_agent", "master_agent.llm", "master_agent.envs"],
    install_requires=[
        'torch',
        'minigrid',
        'numpy',
    ],
)