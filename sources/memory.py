import time
import datetime
import uuid
import os
import sys
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.utility import timer_decorator

class Memory():
    """
    Memory is a class for managing the conversation memory
    It provides a method to compress the memory (experimental, use with caution).
    """
    def __init__(self, system_prompt: str,
                 recover_last_session: bool = False,
                 memory_compression: bool = True):
        self.memory = []
        self.memory = [{'role': 'user', 'content': system_prompt}]
        
        self.session_time = datetime.datetime.now()
        self.session_id = str(uuid.uuid4())
        self.conversation_folder = f"conversations/"
        if recover_last_session:
            self.load_memory()
        # memory compression system
        self.model = "pszemraj/led-base-book-summary"
        self.device = self.get_cuda_device()
        self.memory_compression = memory_compression
        self.tokenizer = None
        self.model_compressor = None
        if config.getboolean('MAIN', 'is_local') and memory_compression:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            self.tokenizer = AutoTokenizer.from_pretrained(self.model)
            self.model_compressor = AutoModelForSeq2SeqLM.from_pretrained(self.model)
    
    def get_filename(self) -> str:
        return f"memory_{self.session_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    
    def save_memory(self) -> None:
        """Save the session memory to a file."""
        if not os.path.exists(self.conversation_folder):
            os.makedirs(self.conversation_folder)
        filename = self.get_filename()
        path = os.path.join(self.conversation_folder, filename)
        json_memory = json.dumps(self.memory)
        with open(path, 'w') as f:
            f.write(json_memory)
    
    def find_last_session_path(self) -> str:
        """Find the last session path."""
        saved_sessions = []
        for filename in os.listdir(self.conversation_folder):
            if filename.startswith('memory_'):
                date = filename.split('_')[1]
                saved_sessions.append((filename, date))
        saved_sessions.sort(key=lambda x: x[1], reverse=True)
        if len(saved_sessions) > 0:
            return saved_sessions[0][0]
        return None

    def load_memory(self) -> None:
        """Load the memory from the last session."""
        if not os.path.exists(self.conversation_folder):
            return
        filename = self.find_last_session_path()
        if filename is None:
            return
        path = os.path.join(self.conversation_folder, filename)
        with open(path, 'r') as f:
            self.memory = json.load(f)
    
    def reset(self, memory: list) -> None:
        self.memory = memory
    
    def push(self, role: str, content: str) -> None:
        """Push a message to the memory."""
        self.memory.append({'role': role, 'content': content})
        # EXPERIMENTAL
        if self.memory_compression and role == 'assistant':
            self.compress()
    
    def clear(self) -> None:
        self.memory = []
    
    def get(self) -> list:
        return self.memory

    def get_cuda_device(self) -> str:
        if config.getboolean('MAIN', 'is_local'):
            import torch
            if torch.backends.mps.is_available():
                return "mps"
            elif torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        else:
            return "cpu"

    def summarize(self, text: str, min_length: int = 64) -> str:
        """
        Summarize the text using the AI model.
        Args:
            text (str): The text to summarize
            min_length (int, optional): The minimum length of the summary. Defaults to 64.
        Returns:
            str: The summarized text
        """
        if self.tokenizer is None or self.model_compressor is None:
            return text
        max_length = len(text) // 2 if len(text) > min_length*2 else min_length*2
        input_text = "summarize: " + text
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        
        if config["MAIN"]["provider_name"] == "openai":
            from openai import OpenAI
            client = OpenAI(base_url=f"http://{config['MAIN']['provider_server_address']}", api_key="none")
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a summarization expert."},
                        {"role": "user", "content": input_text}
                    ],
                    temperature=0.0
                )
                summary = response.choices[0].message.content.strip()
                summary.replace('summary:', '')
                return summary
            except Exception as e:
                print(f"Error during OpenAI summarization: {e}")
                return text
        else:
            summary_ids = self.model_compressor.generate(
                inputs['input_ids'],
                max_length=max_length,  # Maximum length of the summary
                min_length=min_length,  # Minimum length of the summary
                length_penalty=1.0,  # Adjusts length preference
                num_beams=4,  # Beam search for better quality
                early_stopping=True  # Stop when all beams finish
            )
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summary.replace('summary:', '')
            return summary
    
    @timer_decorator
    def compress(self) -> str:
        """
        Compress the memory using the AI model.
        """
        if not self.memory_compression:
            return
        for i in range(len(self.memory)):
            if i <= 2:
                continue
            if self.memory[i]['role'] == 'assistant':
                self.memory[i]['content'] = self.summarize(self.memory[i]['content'])

if __name__ == "__main__":
    memory = Memory("You are a helpful assistant.",
                    recover_last_session=False, memory_compression=True)
    
    sample_text = """
The error you're encountering:
cuda.cu:52:10: fatal error: helper_functions.h: No such file or directory
 #include <helper_functions.h>
indicates that the compiler cannot find the helper_functions.h file. This is because the #include <helper_functions.h> directive is looking for the file in the system's include paths, but the file is either not in those paths or is located in a different directory.
1. Use #include "helper_functions.h" Instead of #include <helper_functions.h>
Angle brackets (< >) are used for system or standard library headers.
Quotes (" ") are used for local or project-specific headers.
If helper_functions.h is in the same directory as cuda.cu, change the include directive to:
3. Verify the File Exists
Double-check that helper_functions.h exists in the specified location. If the file is missing, you'll need to obtain or recreate it.
4. Use the Correct CUDA Samples Path (if applicable)
If helper_functions.h is part of the CUDA Samples, ensure you have the CUDA Samples installed and include the correct path. For example, on Linux, the CUDA Samples are typically located in /usr/local/cuda/samples/common/inc. You can include this path like so:
Use #include "helper_functions.h" for local files.
Use the -I flag to specify the directory containing helper_functions.h.
Ensure the file exists in the specified location.
    """
    
    memory.push('user', "why do i get this error?")
    memory.push('assistant', sample_text)
    print("\n---\nmemory before:", memory.get())
    memory.compress()
    print("\n---\nmemory after:", memory.get())
    memory.save_memory()
