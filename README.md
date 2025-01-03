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
% python3
>>> import keyring
>>> keyring.set_password("aocllm", "google-ai-studio", "YOUR_KEY_HERE")
>>> exit
```

## If you're running ollama, to do local testing start the ollama server.

``` shell
caffeinate ollama serve
```


## Running the LLM tester

``` shell
caffeinate python3 experiment_runner.py
```

## Observing progress with a simple web browser

``` shell
python3 web_server.py
```

## Blog post about the process of writing this program

[Using Gemini to write a LLM tester in Python](https://jackpal.github.io/2024/12/27/Writing_a_llm_testing_framework_with_Gemini.html)
