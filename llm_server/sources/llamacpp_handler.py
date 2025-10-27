from llm_server.utils.generator import BaseGenerator
from llama_cpp import Llama
from llm_server.utils.decorators import timer_decorator, manage_generation_state

class LlamacppLLM(BaseGenerator):

    def __init__(self):
        """
        Handle generation using llama.cpp
        """
        super().__init__()
        self.llm = None
    
    @timer_decorator
    @manage_generation_state
    def generate(self, history):
        if self.llm is None:
            self.logger.info(f"Loading {self.model}...")
            self.llm = Llama.from_pretrained(
                repo_id=self.model,
                filename="*Q8_0.gguf",
                n_ctx=4096,
                verbose=True
            )
        self.logger.info(f"Using {self.model} for generation with Llama.cpp")

        output = self.llm.create_chat_completion(
                messages = history
        )
        with self.state.lock:
            self.state.current_buffer = output['choices'][0]['message']['content']