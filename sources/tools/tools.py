"""
define a generic tool class, any tool can be used by the agent.

A tool can be used by a llm like so:
```<tool name>
<code or query to execute>
```

we call these "blocks".

For example:
```python
print("Hello world")
```
This is then executed by the tool with its own class implementation of execute().
A tool is not just for code tool but also API, internet search, MCP, etc..
"""

import sys
import os
import configparser
from abc import abstractmethod

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.logger import Logger

class Tools():
    """
    Abstract class for all tools.
    """
    def __init__(self, work_dir: str = None):
        self.tag = "undefined"
        self.name = "undefined"
        self.description = "undefined"
        self.client = None
        self.messages = []
        self.logger = Logger("tools.log")
        self.config = configparser.ConfigParser()
        self.work_dir = self._initialize_work_dir(work_dir)
        self.excutable_blocks_found = False
        self.safe_mode = False
        self.allow_language_exec_bash = False
    
    def _initialize_work_dir(self, work_dir: str = None) -> str:
        """
        Initialize the working directory for the tool.
        """
        if work_dir:
            path = work_dir
        else:
            path = os.getenv('WORK_DIR')

        if not path:
            if os.path.exists('./config.ini'):
                self.config.read('./config.ini')
                path = self.config.get('MAIN', 'work_dir', fallback=None)

        if not path:
            self.logger.info("No work directory specified, using default.")
            path = "workspace"

        os.makedirs(path, exist_ok=True)
        return path

    def get_work_dir(self):
        return self.work_dir
    
    def set_allow_language_exec_bash(self, value: bool) -> None:
        self.allow_language_exec_bash = value 

    def safe_get_work_dir_path(self):
        path = None
        path = os.getenv('WORK_DIR', path)
        if path is None or path == "":
            path = self.config['MAIN']['work_dir'] if 'MAIN' in self.config and 'work_dir' in self.config['MAIN'] else None
        if path is None or path == "":
            raise Exception("No work dir specified, please specify a work dir in .env file.")
        return path
    
    def config_exists(self):
        """Check if the config file exists."""
        return os.path.exists('./config.ini')

    def create_work_dir(self):
        """Create the work directory if it does not exist."""
        default_path = os.path.dirname(os.getcwd())
        if self.config_exists():
            self.config.read('./config.ini')
            workdir_path = self.safe_get_work_dir_path()
        else:
            workdir_path = default_path
        return workdir_path

    @abstractmethod
    def execute(self, blocks:[str], safety:bool) -> str:
        """
        Abstract method that must be implemented by child classes to execute the tool's functionality.
        Args:
            blocks (List[str]): The codes or queries blocks to execute
            safety (bool): Whenever human intervention is required
        Returns:
            str: The output/result from executing the tool
        """
        pass

    @abstractmethod
    def execution_failure_check(self, output:str) -> bool:
        """
        Abstract method that must be implemented by child classes to check if tool execution failed.
        Args:
            output (str): The output string from the tool execution to analyze
        Returns:
            bool: True if execution failed, False if successful
        """
        pass

    @abstractmethod
    def interpreter_feedback(self, output:str) -> str:
        """
        Abstract method that must be implemented by child classes to provide feedback to the AI from the tool.
        Args:
            output (str): The output string from the tool execution to analyze
        Returns:
            str: The feedback message to the AI
        """
        pass

    def save_block(self, blocks:[str], save_path:str) -> None:
        """
        Save code or query blocks to a file at the specified path.
        Creates the directory path if it doesn't exist.
        Args:
            blocks (List[str]): List of code/query blocks to save
            save_path (str): File path where blocks should be saved
        """
        if save_path is None:
            return
        self.logger.info(f"Saving blocks to {save_path}")
        save_path_dir = os.path.dirname(save_path)
        save_path_file = os.path.basename(save_path)
        directory = os.path.join(self.work_dir, save_path_dir)
        if directory and not os.path.exists(directory):
            self.logger.info(f"Creating directory {directory}")
            os.makedirs(directory)
        for block in blocks:
            with open(os.path.join(directory, save_path_file), 'w') as f:
                f.write(block)
    
    def get_parameter_value(self, block: str, parameter_name: str) -> str:
        """
        Get a parameter name.
        Args:
            block (str): The block of text to search for the parameter
            parameter_name (str): The name of the parameter to retrieve
        Returns:
            str: The value of the parameter
        """
        for param_line in block.split('\n'):
            if parameter_name in param_line:
                param_value = param_line.split('=')[1].strip()
                return param_value
        return None
    
    def found_executable_blocks(self):
        """
        Check if executable blocks were found.
        """
        tmp = self.excutable_blocks_found
        self.excutable_blocks_found = False
        return tmp

    def load_exec_block(self, llm_text: str):
        """
        Extract code/query blocks from LLM-generated text and process them for execution.
        This method parses the text looking for code blocks marked with the tool's tag (e.g. ```python).
        Args:
            llm_text (str): The raw text containing code blocks from the LLM
        Returns:
            tuple[list[str], str | None]: A tuple containing:
                - List of extracted and processed code blocks
                - The path the code blocks was saved to
        """
        assert self.tag != "undefined", "Tag not defined"
        start_tag = f'```{self.tag}' 
        end_tag = '```'
        code_blocks = []
        start_index = 0
        save_path = None

        if start_tag not in llm_text:
            return None, None

        while True:
            start_pos = llm_text.find(start_tag, start_index)
            if start_pos == -1:
                break

            line_start = llm_text.rfind('\n', 0, start_pos)+1
            leading_whitespace = llm_text[line_start:start_pos]

            end_pos = llm_text.find(end_tag, start_pos + len(start_tag))
            if end_pos == -1:
                break
            content = llm_text[start_pos + len(start_tag):end_pos]
            lines = content.split('\n')
            if leading_whitespace:
                processed_lines = []
                for line in lines:
                    if line.startswith(leading_whitespace):
                        processed_lines.append(line[len(leading_whitespace):])
                    else:
                        processed_lines.append(line)
                content = '\n'.join(processed_lines)

            if ':' in content.split('\n')[0]:
                save_path = content.split('\n')[0].split(':')[1]
                content = content[content.find('\n')+1:]
            self.excutable_blocks_found = True
            code_blocks.append(content)
            start_index = end_pos + len(end_tag)
        self.logger.info(f"Found {len(code_blocks)} blocks to execute")
        return code_blocks, save_path
    
if __name__ == "__main__":
    tool = Tools()
    tool.tag = "python"
    rt = tool.load_exec_block("""```python
import os

for file in os.listdir():
    if file.endswith('.py'):
        print(file)
```
goodbye!
    """)
    print(rt)
