import asyncio

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.fileFinder import FileFinder
from sources.tools.BashInterpreter import BashInterpreter
from sources.memory import Memory

# Each step is one LLM call, plus the tools it asks for.
MAX_STEPS = 10
STEP_LIMIT_MESSAGE = f"I stopped after {MAX_STEPS} steps without finishing the task."

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
    
    async def process(self, prompt, speech_module) -> tuple[str, str]:
        """Do a file task with tool calls until the model gives its final answer.

        Interaction.think calls this with the user query, which can carry
        uploaded file paths in a <files> tag.
        Each step asks the LLM, then runs the tool blocks in its answer; the
        tool output goes back to the LLM. An answer without code blocks is the
        final answer. A block that no tool runs (for example ```python) gets
        feedback that lists the real tools. The loop stops after MAX_STEPS
        steps or on a stop request.

        Args:
            prompt (str): User query, from Interaction.think.
            speech_module (Speech | None): Text-to-speech engine, from Interaction.

        Returns:
            tuple[str, str]: Answer for the user (tool blocks removed), and the LLM reasoning.
        """
        answer = ""
        reasoning = ""
        prompt += f"\nYou must work in directory: {self.work_dir}"
        self.memory.push('user', prompt)
        self.last_answer = ""
        for _ in range(MAX_STEPS):
            if self.stop:
                break
            await self.wait_message(speech_module)
            animate_thinking("Thinking...", color="status")
            answer, reasoning = await self.llm_request()
            self.last_reasoning = reasoning
            has_blocks = "```" in answer
            results_before = len(self.blocks_result)
            self.execute_modules(answer)
            answer = self.remove_blocks(answer)
            self.last_answer = answer
            if not has_blocks:
                break  # plain text: final answer
            if len(self.blocks_result) == results_before:
                self.memory.push('user', self.unknown_block_feedback())
        else:
            answer = f"{answer}\n\n{STEP_LIMIT_MESSAGE}".strip()
        self.status_message = "Ready"
        return answer, reasoning

    def unknown_block_feedback(self) -> str:
        """Tell the LLM that none of its blocks ran, and which tools exist.

        process calls this when an answer has code blocks but no tool ran them,
        for example a ```python block.

        Returns:
            str: Feedback message for the LLM.
        """
        tools = ", ".join(self.tools)
        return (f"[failure] No block ran: you can only use these blocks: {tools}. "
                "To read a file (PDF included), use file_finder with action=read. "
                "When the task is finished, answer without any block.")

if __name__ == "__main__":
    pass