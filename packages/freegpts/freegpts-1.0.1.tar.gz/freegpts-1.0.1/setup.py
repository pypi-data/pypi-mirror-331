from setuptools import setup, find_packages

setup(
    name="freegpts",
    version="1.0.1",
    description='The project provides free access to ChatGPT-4, GPT-4o-mini, and SearchGPT models for integration into Python applications.',
    packages=find_packages(),
    install_requires=['requests'],
    project_urls={
    'GitHub': 'https://github.com/xevvv/free-chat-gpt'
    },
)
