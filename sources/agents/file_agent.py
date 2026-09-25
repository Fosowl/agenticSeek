import asyncio

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.fileFinder import FileFinder
from sources.tools.BashInterpreter import BashInterpreter
from sources.memory import Memory

class FileAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False):
        """
        The file agent is a special agent for file operations.
        """
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "file_finder": FileFinder(),
            "bash": BashInterpreter()
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.role = "files"
        self.type = "file_agent"
        self.memory = Memory(self.load_prompt(prompt_path),
                        recover_last_session=False, # session recovery in handled by the interaction class
                        memory_compression=False,
                        model_provider=provider.get_model_name())
    
    async def process(self, prompt, speech_module) -> str:
        answer = ""
        reasoning = ""
        attempt = 0
        max_attempts = 5
        prompt += f"\nYou must work in directory: {self.work_dir}"
        self.memory.push('user', prompt)
        self.last_answer = ""
        while not "done" in self.last_answer.lower() and not self.stop:
            exec_success = False
            while exec_success is False and attempt < max_attempts and not self.stop:
                await self.wait_message(speech_module)
                animate_thinking("Thinking...", color="status")
                answer, reasoning = await self.llm_request()
                self.last_reasoning = reasoning
                exec_success, _ = self.execute_modules(answer)
                answer = self.remove_blocks(answer)
                self.last_answer = answer
                attempt += 1
        self.status_message = "Ready"
        return answer, reasoning

if __name__ == "__main__":
    pass