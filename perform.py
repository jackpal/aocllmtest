import subprocess
import sys

def run(program: str, input_str: str, timeout: int) -> tuple[str, str | None]:
    """
    Executes untrusted Python code in a separate process with a timeout.
    """
    try:
        process = subprocess.Popen(
            [sys.executable, '-c', program],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_str, timeout=timeout)
        if process.returncode == 0:
            return 'success', stdout.strip()
        else:
            return 'error', stderr.strip()
    except subprocess.TimeoutExpired:
        process.kill()
        return 'timeout', None
    except Exception as e:
        return 'error', str(e)
