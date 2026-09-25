
from typing import Tuple, Callable
from abc import abstractmethod
import os
import random
import time

import asyncio
from concurrent.futures import ThreadPoolExecutor

from sources.memory import Memory
from sources.utility import pretty_print
from sources.schemas import executorResult

random.seed(time.time())

class Agent():
    """
    An abstract class for all agents.
    """
    def __init__(self, name: str,
                       prompt_path:str,
                       provider,
                       verbose=False,
                       browser=None) -> None:
        """
        Args:
            name (str): Name of the agent.
            prompt_path (str): Path to the prompt file for the agent.
            provider: The provider for the LLM.
            recover_last_session (bool, optional): Whether to recover the last conversation. 
            verbose (bool, optional): Enable verbose logging if True. Defaults to False.
            browser: The browser class for web navigation (only for browser agent).
        """
            
        self.agent_name = name
        self.browser = browser
        self.role = None
        self.type = None
        self.current_directory = os.getcwd()
        self.llm = provider 
        self.memory = None
        self.tools = {}
        self.blocks_result = []
        self.success = True
        self.last_answer = ""
        self.last_reasoning = ""
        self.status_message = "Haven't started yet"
        self.stop = False
        self.verbose = verbose
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    @property
    def get_agent_name(self) -> str:
        return self.agent_name
    
    @property
    def get_agent_type(self) -> str:
        return self.type
    
    @property
    def get_agent_role(self) -> str:
        return self.role
    
    @property
    def get_last_answer(self) -> str:
        return self.last_answer
    
    @property
    def get_last_reasoning(self) -> str:
        return self.last_reasoning
    
    @property
    def get_blocks(self) -> list:
        return self.blocks_result
    
    @property
    def get_status_message(self) -> str:
        return self.status_message

    @property
    def get_tools(self) -> dict:
        return self.tools
    
    @property
    def get_success(self) -> bool:
        return self.success
    
    def get_blocks_result(self) -> list:
        return self.blocks_result

    def add_tool(self, name: str, tool: Callable) -> None:
        if not callable(tool):
            raise TypeError("Tool must be a callable object (a method)")
        self.tools[name] = tool
    
    def get_tools_name(self) -> list:
        """
        Get the list of tools names.
        """
        return list(self.tools.keys())
    
    def get_tools_description(self) -> str:
        """
        Get the list of tools names and their description.
        """
        description = ""
        for name in self.get_tools_name():
            description += f"{name}: {self.tools[name].description}\n"
        return description
    
    def load_prompt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found at path: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied to read prompt file at path: {file_path}")
        except Exception as e:
            raise e
    
    def request_stop(self) -> None:
        """
        Request the agent to stop.
        """
        self.stop = True
        self.status_message = "Stopped"
    
    @abstractmethod
    def process(self, prompt, speech_module) -> str:
        """
        abstract method, implementation in child class.
        Process the prompt and return the answer of the agent.
        """
        pass

    def remove_reasoning_text(self, text: str) -> None:
        """
        Remove the reasoning block of reasoning model like deepseek.
        """
        if text is None:
            return ""
        end_tag = "</think>"
        end_idx = text.rfind(end_tag)
        if end_idx == -1:
            return text
        return text[end_idx+8:]
    
    def extract_reasoning_text(self, text: str) -> None:
        """
        Extract the reasoning block of a reasoning model like deepseek.
        """
        start_tag = "<think>"
        end_tag = "</think>"
        if text is None:
            return None
        start_idx = text.find(start_tag)
        end_idx = text.rfind(end_tag)+8
        return text[start_idx:end_idx]
    
    async def llm_request(self) -> Tuple[str, str]:
        """
        Asynchronously ask the LLM to process the prompt.
        """
        self.status_message = "Thinking..."
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.sync_llm_request)
    
    def sync_llm_request(self) -> Tuple[str, str]:
        """
        Ask the LLM to process the prompt and return the answer and the reasoning.
        """
        memory = self.memory.get()
        thought = self.llm.respond(memory, self.verbose)

        reasoning = self.extract_reasoning_text(thought)
        answer = self.remove_reasoning_text(thought)
        self.memory.push('assistant', answer)
        return answer, reasoning
    
    async def wait_message(self, speech_module):
        if speech_module is None:
            return
        messages = ["Please be patient, I am working on it.",
                    "Computing... I recommand you have a coffee while I work.",
                    "Hold on, I’m crunching numbers.",
                    "Working on it, please let me think."]
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: speech_module.speak(messages[random.randint(0, len(messages)-1)]))
    
    def get_last_tool_type(self) -> str:
        return self.blocks_result[-1].tool_type if len(self.blocks_result) > 0 else None
    
    def raw_answer_blocks(self, answer: str) -> str:
        """
        Return the answer with all the blocks inserted, as text.
        """
        if self.last_answer is None:
            return
        raw = ""
        lines = self.last_answer.split("\n")
        for line in lines:
            if "block:" in line:
                block_idx = int(line.split(":")[1])
                if block_idx < len(self.blocks_result):
                    raw += self.blocks_result[block_idx].__str__()
            else:
                raw += line + "\n"
        return raw

    def show_answer(self):
        """
        Show the answer in a pretty way.
        Show code blocks and their respective feedback by inserting them in the ressponse.
        """
        if self.last_answer is None:
            return
        lines = self.last_answer.split("\n")
        for line in lines:
            if "block:" in line:
                block_idx = int(line.split(":")[1])
                if block_idx < len(self.blocks_result):
                    self.blocks_result[block_idx].show()
            else:
                pretty_print(line, color="output")

    def remove_blocks(self, text: str) -> str:
        """
        Remove all code/query blocks within a tag from the answer text.
        """
        tag = f'```'
        lines = text.split('\n')
        post_lines = []
        in_block = False
        block_idx = 0
        for line in lines:
            if tag in line and not in_block:
                in_block = True
                continue
            if not in_block:
                post_lines.append(line)
            if tag in line:
                in_block = False
                post_lines.append(f"block:{block_idx}")
                block_idx += 1
        return "\n".join(post_lines)
    
    def show_block(self, block: str) -> None:
        """
        Show the block in a pretty way.
        """
        pretty_print('▂'*64, color="status")
        pretty_print(block, color="code")
        pretty_print('▂'*64, color="status")

    def execute_modules(self, answer: str) -> Tuple[bool, str]:
        """
        Execute all the tools the agent has and return the result.
        """
        feedback = ""
        success = True
        blocks = None
        if answer.startswith("```"):
            answer = "I will execute:\n" + answer # there should always be a text before blocks for the function that display answer

        self.success = True
        for name, tool in self.tools.items():
            feedback = ""
            blocks, save_path = tool.load_exec_block(answer)

            if blocks != None:
                pretty_print(f"Executing {len(blocks)} {name} blocks...", color="status")
                for block in blocks:
                    self.show_block(block)
                    output = tool.execute([block])
                    feedback = tool.interpreter_feedback(output) # tool interpreter feedback
                    success = not tool.execution_failure_check(output)
                    self.blocks_result.append(executorResult(block, feedback, success, name))
                    if not success:
                        self.success = False
                        self.memory.push('user', feedback)
                        return False, feedback
                self.memory.push('user', feedback)
                if save_path != None:
                    tool.save_block(blocks, save_path)
        return True, feedback
