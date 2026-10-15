
import sys
import os
import re
import subprocess

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sources.tools.tools import Tools
from sources.tools.sandbox import subprocess_isolation

class PyInterpreter(Tools):
    """
    This class is a tool to allow agent for python code execution.
    """

    INTERACTIVE_PATTERNS = [
        (re.compile(r"^\s*(?:import|from)\s+[^\n]*\bcurses\b", re.MULTILINE), "curses"),
        (re.compile(r"(?<![\w.])(?<!def\s)input\s*\("), "input()"),
    ]

    def __init__(self):
        super().__init__()
        self.tag = "python"
        self.name = "Python Interpreter"
        self.description = "This tool allows the agent to execute python code."

    def refuse_interactive_code(self, code: str) -> str:
        """
        Return a refusal message if `code` needs a terminal, empty string otherwise.
        Code runs headless with stdio attached to pipes, so curses raises
        'cbreak() returned ERR' and input() hits EOF or hangs on every retry;
        refusing upfront gives the agent feedback it can actually act on.
        """
        for pattern, feature in self.INTERACTIVE_PATTERNS:
            if pattern.search(code):
                return (f"code execution failed: {feature} requires an interactive terminal, "
                        "but code runs headless in a sandbox with no terminal attached. "
                        f"Rewrite the code without {feature}: take values from variables in "
                        "the code and print results to stdout.")
        return ""

    def execute(self, codes:str, safety = False, timeout=300) -> str:
        """
        Execute python code in an isolated subprocess.
        The code runs in the work directory and is killed after `timeout`
        seconds, so runaway code cannot freeze the backend.
        Interactive code (curses, input()) is refused upfront: the sandbox
        has no terminal, so it can never work.
        """
        if safety and input("Execute code ? y/n") != "y":
            return "Code rejected by user."
        code = '\n\n'.join(codes)
        refusal = self.refuse_interactive_code(code)
        if refusal:
            self.logger.warning(f"Refused interactive code:\n{code}")
            return refusal
        self.logger.info(f"Executing code:\n{code}")
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                **subprocess_isolation(self.work_dir)
            )
        except subprocess.TimeoutExpired:
            self.logger.error(f"Code execution timed out after {timeout} seconds.")
            return f"code execution failed: timed out after {timeout} seconds."
        except Exception as e:
            self.logger.error(f"Code execution failed: {str(e)}")
            return "code execution failed:" + str(e)
        if result.returncode != 0:
            self.logger.error(f"Code execution failed:\n{result.stderr}")
            return "code execution failed:" + (result.stderr or result.stdout)
        self.logger.info("Code execution finished.")
        return result.stdout

    def interpreter_feedback(self, output:str) -> str:
        """
        Provide feedback based on the output of the code execution
        """
        if self.execution_failure_check(output):
            feedback = f"[failure] Error in execution:\n{output}"
        else:
            feedback = "[success] Execution success, code output:\n" + output
        return feedback

    def execution_failure_check(self, feedback:str) -> bool:
        """
        Check if the code execution failed.
        """
        error_patterns = [
            r"expected", 
            r"errno", 
            r"failed", 
            r"traceback", 
            r"invalid", 
            r"unrecognized", 
            r"exception", 
            r"syntax", 
            r"crash", 
            r"segmentation fault", 
            r"core dumped"
        ]
        combined_pattern = "|".join(error_patterns)
        if re.search(combined_pattern, feedback, re.IGNORECASE):
            self.logger.error(f"Execution failure detected: {feedback}")
            return True
        self.logger.info("No execution success detected.")
        return False

if __name__ == "__main__":
    text = """
For Python, let's also do a quick check:

```python
print("Hello from Python!")
```

If these work, you'll see the outputs in the next message. Let me know if you'd like me to test anything specific! 

here is a save test
```python:tmp.py

def print_hello():
    hello = "Hello World"
    print(hello)

if __name__ == "__main__":
    print_hello()
```
"""
    py = PyInterpreter()
    codes, save_path = py.load_exec_block(text)
    py.save_block(codes, save_path)
    print(py.execute(codes))