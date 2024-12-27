import subprocess
import sys
from typing import List, Tuple

def run(program: str, input: str, args: List[str], timeout: int) -> Tuple[str, str | None]:
    """
    Executes untrusted Python code in a sandboxed environment.

    Args:
        program: A string containing the Python program to execute.
        input: Text to pass on stdin to the program.
        args: A list of strings representing the command-line arguments.
        timeout: The number of seconds to allow the program to run before stopping it.

    Returns:
        A tuple containing:
            - A string indicating the outcome ('success', 'error', or 'timeout').
            - For 'success', the stdout of the program.
            - For 'error', the stderr of the program.
            - For 'timeout', None.
    """
    try:
        process = subprocess.Popen(
            [sys.executable, '-c', program, *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input, timeout=timeout)
        if process.returncode == 0:
            return 'success', stdout
        else:
            return 'error', stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return 'timeout', None
    except Exception as e:
        return 'error', str(e)
