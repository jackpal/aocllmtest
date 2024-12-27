# Advent of Code LLM Tester

A project to see how well common coding LLMs can solve Advent of Code
puzzles.

## One Time Setup

### Create project Python Virtual Environment

1. Open aocllmtest directory in Visual Studio Code
2. Command-shift-P to open command palette
3. Python: Create Environment...
4. Choose Venv
5. Choose Python 3.13.1
6. Choose requirements.txt
7. Tap OK
8. Wait for the environment to be created.

### Set up your Advent of Code Data credentials

Follow instructions at <https://github.com/wimglenn/advent-of-code-data>

### Install your AI Studio key in Apple Keychain

1. Visit <https://aistudio.google.com/apikey>
2. Create a new API key or copy an existing one
3. From visual studio code's terminal:

``` shell
% python
>>> import keyring
>>> keyring.set_password("aocllm", "google-ai-studio", "YOUR_KEY_HERE")
>>> exit
```

## Running the LLM tester

``` shell
python db_manager.py --init
```
