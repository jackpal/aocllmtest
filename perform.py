import sys
import traceback
import time
import multiprocessing
import signal

def execute_program(program, part, input, result_queue):
    """
    Helper function to execute the program in a separate process.
    """
    try:
        # Redirect stdout and stderr to capture output and errors
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_stdout = open("stdout.txt", "w")
        sys.stderr = captured_stderr = open("stderr.txt", "w")

        # Compile and execute the code
        code = compile(program, '<string>', 'exec')
        namespace = {}
        exec(code, namespace)

        # Check for the existence of the 'solve' function
        if 'solve' not in namespace:
            result_queue.put(('error', "The 'solve' function is not defined in the program."))
            return  # Exit early if 'solve' is not found

        # Call the 'solve' function and put the result in the queue
        result = namespace['solve'](part, input)
        result_queue.put(('success', str(result)))

    except Exception as e:
        # Capture any exceptions during execution
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        result_queue.put(('error', error_message))

    finally:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        captured_stdout.close()
        captured_stderr.close()

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
    # Create a queue to store the result from the child process
    result_queue = multiprocessing.Queue()

    # Create a process to execute the program
    process = multiprocessing.Process(target=execute_program, args=(program, part, input, result_queue))
    process.start()

    # Wait for the process to finish or timeout
    process.join(timeout)

    if process.is_alive():
        # If the process is still alive after the timeout, terminate it
        process.terminate()
        # Ensure it is no longer in memory
        process.join()
        return ('timeout', None)
    else:
        # Get the result from the queue
        status, result = result_queue.get()
        return (status, result)

if __name__ == "__main__":
    result, answer = run("def solve(part,input): return input[part]", 1, 'abc', 10)
    assert(result == 'success')
    assert(answer == 'b')

    result, answer = run("print('Hi!')", 1, 'abc', 10)
    assert(result == 'error')
    
    result, answer = run("""import time
time.sleep(1000)""", 1, 'abc', 10)
    assert(result == 'timeout')
