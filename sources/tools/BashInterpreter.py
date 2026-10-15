
import os, sys
import re
from io import StringIO
import subprocess

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sources.tools.tools import Tools
from sources.tools.safety import is_unsafe
from sources.tools.sandbox import subprocess_isolation

class BashInterpreter(Tools):
    """
    This class is a tool to allow agent for bash code execution.
    """
    def __init__(self):
        super().__init__()
        self.tag = "bash"
        self.name = "Bash Interpreter"
        self.description = "This tool allows the agent to execute bash commands."
    
    def language_bash_attempt(self, command: str):
        """
        Detect if AI attempt to run the code using bash.
        If so, return True, otherwise return False.
        Code written by the AI will be executed automatically, so it should not use bash to run it.
        """
        lang_interpreter = ["python", "gcc", "g++", "mvn", "go", "java", "javac", "rustc", "clang", "clang++", "rustc", "rustc++", "rustc++"]
        for word in command.split():
            if any(word.startswith(lang) for lang in lang_interpreter):
                return True
        return False
    
    def execute(self, commands: str, safety=False, timeout=300):
        """
        Execute bash commands in the work directory.
        Commands run through the shell with newlines preserved so multi-line
        blocks work. Each command is killed after `timeout` seconds.
        In safe mode the whole batch is validated up front: if any command
        is unsafe, nothing in the batch executes.
        """
        if safety and input("Execute command? y/n ") != "y":
            return "Command rejected by user."

        if self.safe_mode:
            for command in commands:
                if is_unsafe(command):
                    print(f"Unsafe command rejected: {command}")
                    return f"\nUnsafe command: {command}. Execution aborted. This is beyond allowed capabilities report to user."

        concat_output = ""
        for command in commands:
            if self.language_bash_attempt(command) and self.allow_language_exec_bash == False:
                # "denied" makes execution_failure_check report a failure.
                return (f"Command not run (permission denied): {command}\n"
                        "Starting python, gcc, go, java or another language from bash is not allowed. "
                        "Use another tool instead.")
            try:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=self.work_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    **subprocess_isolation(self.work_dir)
                )
                try:
                    command_output, _ = process.communicate(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    command_output, _ = process.communicate()
                    return f"Command {command} timed out. Output:\n{command_output}"
                if process.returncode != 0:
                    return f"Command {command} failed with return code {process.returncode}:\n{command_output}"
                concat_output += f"Output of {command}:\n{command_output.strip()}\n"
            except Exception as e:
                return f"Command {command} failed:\n{str(e)}"
        return concat_output

    def interpreter_feedback(self, output):
        """
        Provide feedback based on the output of the bash interpreter
        """
        if self.execution_failure_check(output):
            feedback = f"[failure] Error in execution:\n{output}"
        else:
            feedback = "[success] Execution success, code output:\n" + output
        return feedback

    def execution_failure_check(self, feedback):
        """
        check if bash command failed.
        """
        error_patterns = [
            r"expected",
            r"errno",
            r"failed",
            r"invalid",
            r"unrecognized",
            r"exception",
            r"syntax",
            r"segmentation fault",
            r"core dumped",
            r"unexpected",
            r"denied",
            r"not recognized",
            r"not permitted",
            r"not installed",
            r"not found",
            r"aborted",
            r"no such",
            r"too many",
            r"too few",
            r"busy",
            r"broken pipe",
            r"missing",
            r"undefined",
            r"refused",
            r"unreachable",
            r"not known"
        ]
        combined_pattern = "|".join(error_patterns)
        if re.search(combined_pattern, feedback, re.IGNORECASE):
            return True
        return False

if __name__ == "__main__":
    bash = BashInterpreter()
    print(bash.execute(["ls", "pwd", "ip a", "nmap -sC 127.0.0.1"]))
