
from sources.utility import pretty_print
from sources.agent import Agent, executorResult
from sources.tools import PyInterpreter, BashInterpreter, CInterpreter, GoInterpreter

class CoderAgent(Agent):
    """
    The code agent is an agent that can write and execute code.
    """
    def __init__(self, model, name, prompt_path, provider):
        super().__init__(model, name, prompt_path, provider)
        self.tools = {
            "bash": BashInterpreter(),
            "python": PyInterpreter()
        }
        self.role = "coding"

    def process(self, prompt, speech_module) -> str:
        answer = ""
        attempt = 0
        max_attempts = 3
        self.memory.push('user', prompt)

        while attempt < max_attempts:
            pretty_print("Thinking...", color="status")
            self.wait_message(speech_module)
            answer, reasoning = self.llm_request()
            exec_success, _ = self.execute_modules(answer)
            answer = self.remove_blocks(answer)
            self.last_answer = answer
            if exec_success:
                break
            self.show_answer()
            attempt += 1
        return answer, reasoning

if __name__ == "__main__":
    from llm_provider import Provider

    #local_provider = Provider("ollama", "deepseek-r1:14b", None)
    server_provider = Provider("server", "deepseek-r1:14b", "192.168.1.100:5000")
    agent = CoderAgent("deepseek-r1:14b", "jarvis", "prompts/coder_agent.txt", server_provider)
    ans = agent.process("What is the output of 5+5 in python ?")
    print(ans)