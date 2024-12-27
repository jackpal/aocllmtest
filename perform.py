import sys
import traceback
import subprocess
import time
import threading
import os

def run(program: str, part: int, input: str, timeout: int) -> tuple[str, str]:
    """
    Executes untrusted python code safely within a sandboxed environment.

    Args:
        program: A string containing Python source code with a 'solve' function.
        part: The 'part' argument to pass to the 'solve' function.
        input: The 'input' argument to pass to the 'solve' function.
        timeout: The maximum execution time in seconds.

    Returns:
        A tuple: (status, result).
        - status: 'success', 'error', or 'timeout'.
        - result: The output of 'solve' (if successful), an error message (if error), or None (if timeout).
    """

    # Create temporary files for the script and communication
    script_file = "temp_script.py"
    result_file = "temp_result.txt"
    error_file = "temp_error.txt"

    # Construct the complete script with solve function call
    full_program = f"""
import sys
import traceback

{program}

if __name__ == '__main__':
    try:
        result = solve({part}, "{input}")
        with open("{result_file}", "w") as f:
            f.write(str(result))
    except Exception as e:
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        with open("{error_file}", "w") as f:
            f.write(error_message)
"""

    # Write the script to a temporary file
    with open(script_file, "w") as f:
        f.write(full_program)

    # Run the script as a separate process
    process = subprocess.Popen([sys.executable, script_file],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    def terminate_process(process):
        if process.poll() is None:
            process.terminate()

    timeout_thread = threading.Timer(timeout, terminate_process, args=[process])
    timeout_thread.start()

    try:
        # Wait for the process to complete and get output
        stdout, stderr = process.communicate()
        timeout_thread.cancel()  # Cancel the timer if process finished before timeout

        if os.path.exists(result_file):
            with open(result_file, "r") as f:
                result = f.read()
            status = "success"
        elif os.path.exists(error_file):
            with open(error_file, "r") as f:
                result = f.read()
            status = "error"
        else:
            result = None
            status = "timeout"

    except subprocess.TimeoutExpired:
        # Timeout occurred
        process.kill()  # Ensure process is killed
        result = None
        status = "timeout"

    finally:
        # Clean up temporary files
        for temp_file in [script_file, result_file, error_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    return status, result