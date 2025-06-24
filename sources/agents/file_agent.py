import asyncio
import os

from sources.utility import pretty_print, animate_thinking, get_os_type, is_running_in_docker
from sources.agents.agent import Agent
from sources.tools.fileFinder import FileFinder
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.WindowsInterpreter import WindowsInterpreter
from sources.memory import Memory

class FileAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False):
        """
        The file agent is a special agent for file operations.
        """
        # Determine the appropriate prompt based on OS
        if get_os_type() == 'windows' and not is_running_in_docker():
            # Check if Windows-specific prompt exists
            windows_prompt_path = prompt_path.replace('file_agent.txt', 'file_agent_windows.txt')
            if os.path.exists(windows_prompt_path):
                prompt_path = windows_prompt_path
                pretty_print(f"Using Windows-specific file agent prompt", color="info")
        
        super().__init__(name, prompt_path, provider, verbose, None)
        
        # Choose the appropriate interpreter based on OS
        if get_os_type() == 'windows' and not is_running_in_docker():
            command_interpreter = WindowsInterpreter()
        else:
            command_interpreter = BashInterpreter()
            
        self.tools = {
            "file_finder": FileFinder(),
            "bash": command_interpreter
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.role = "files"
        self.type = "file_agent"
        self.memory = Memory(self.load_prompt(prompt_path),
                        recover_last_session=False, # session recovery in handled by the interaction class
                        memory_compression=False,
                        model_provider=provider.get_model_name())
    
    async def process(self, prompt, speech_module) -> str:
        exec_success = False
        prompt += f"\nYou must work in directory: {self.work_dir}"
        self.memory.push('user', prompt)
        while exec_success is False and not self.stop:
            await self.wait_message(speech_module)
            animate_thinking("Thinking...", color="status")
            answer, reasoning = await self.llm_request()
            self.last_reasoning = reasoning
            exec_success, _ = self.execute_modules(answer)
            answer = self.remove_blocks(answer)
            self.last_answer = answer
        self.status_message = "Ready"
        return answer, reasoning

if __name__ == "__main__":
    pass