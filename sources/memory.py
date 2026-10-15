import datetime
import json
import math
import os
import sys

from sources.utility import pretty_print, animate_thinking
from sources.logger import Logger
from sources.workspace import runtime_subdir

SUMMARY_MODEL_NAME = "pszemraj/led-base-book-summary"
SUMMARY_MAX_INPUT_TOKENS = 16384  # LED encoder limit
MAX_SUMMARY_PASSES = 3
COMPRESS_MESSAGE_MIN_CHARS = 1024
CHARS_PER_TOKEN = 4  # rough average for English text
BASE_MODEL_SIZE_B = 7
BASE_CONTEXT_TOKENS = 4096
CONTEXT_SCALING_FACTOR = 1.5
MODEL_NAME_SEPARATORS = ":-_/ "


def parse_model_size_billions(model_name: str | None) -> float | None:
    """
    Agents give the model name of their provider, and this function reads the model size from it.
    Memory calls it once, when it starts.
    It finds a part of the name like "14b" or "3.8B" and gives the number before the "b".
    Args:
        model_name (str | None): provider model name, for example "deepseek-r1:14b". None when the agent has no provider.
    Returns:
        float | None: model size in billions of parameters, or None when the name has no size.
    """
    if not model_name:
        return None
    normalized = model_name.lower()
    for separator in MODEL_NAME_SEPARATORS:
        normalized = normalized.replace(separator, " ")
    for part in normalized.split():
        if not part.endswith("b"):
            continue
        try:
            return float(part[:-1])
        except ValueError:
            continue
    return None


def estimate_context_tokens(model_name: str | None) -> int | None:
    """
    Memory uses this estimate to limit the text that it sends to the model. EXPERIMENTAL.
    Memory calls it once, with the provider model name.
    It scales a 4096-token context of a 7B model by the model size and rounds to a power of two.
    Args:
        model_name (str | None): provider model name, for example "qwen2.5:7b". None when the agent has no provider.
    Returns:
        int | None: estimated context size in tokens, or None when the model size is unknown.
    """
    model_size = parse_model_size_billions(model_name)
    if not model_size:
        return None
    context_size = BASE_CONTEXT_TOKENS * (model_size / BASE_MODEL_SIZE_B) ** CONTEXT_SCALING_FACTOR
    return 2 ** round(math.log2(context_size))


def is_valid_history(history) -> bool:
    """
    Memory uses this check before it replaces the conversation with a saved session.
    load_memory calls it with the data that it read from a session file.
    It accepts only a list of messages with a text role and text content, that starts with the system message.
    Args:
        history (Any): data decoded from the JSON session file.
    Returns:
        bool: True when the data is a usable conversation.
    """
    if not isinstance(history, list) or not history:
        return False
    for message in history:
        if not isinstance(message, dict):
            return False
        if not isinstance(message.get('role'), str) or not isinstance(message.get('content'), str):
            return False
    return history[0]['role'] == 'system'


def write_json_atomic(path: str, data) -> None:
    """
    Memory uses this function to save sessions, so that a crash cannot leave a half-written file.
    save_memory calls it with the session file path and the conversation list.
    It writes to a temporary file, then replaces the target file in one step.
    Args:
        path (str): target session file path.
        data (Any): JSON-serializable data to write.
    """
    tmp_path = f"{path}.tmp"
    with open(tmp_path, 'w') as f:
        json.dump(data, f)
    os.replace(tmp_path, path)


class Memory():
    """
    Memory is a class for managing the conversation memory
    It provides a method to compress the memory using summarization model.
    """
    def __init__(self, system_prompt: str,
                 recover_last_session: bool = False,
                 memory_compression: bool = True,
                 model_provider: str | None = "deepseek-r1:14b"):
        """
        Each agent creates one Memory to keep its conversation with the LLM.
        Agents call it with their system prompt and the model name of their provider.
        It makes a conversation with only the system message, and can load the summarization model and the last session.
        Args:
            system_prompt (str): agent system prompt, read from the agent prompt file.
            recover_last_session (bool): True to load the last saved casual_agent session.
            memory_compression (bool): True to load the summarization model and compress long messages.
            model_provider (str | None): provider model name, used to estimate the context size. None when unknown.
        """
        self.system_prompt = system_prompt
        self.memory = [{'role': 'system', 'content': system_prompt}]
        self.logger = Logger("memory.log")
        self.session_time = datetime.datetime.now()
        self.conversation_folder = runtime_subdir("conversations")
        self.session_recovered = False
        self.model = None
        self.tokenizer = None
        self.memory_compression = memory_compression
        self.model_provider = model_provider
        self.ideal_ctx = estimate_context_tokens(model_provider)
        self.max_ctx_chars = self.ideal_ctx * CHARS_PER_TOKEN if self.ideal_ctx else None
        if self.ideal_ctx:
            self.logger.info(f"Estimated context size for {model_provider}: {self.ideal_ctx} tokens.")
        if self.memory_compression:
            self.download_model()
        if recover_last_session:
            self.load_memory()
            self.session_recovered = True

    def download_model(self) -> None:
        """
        Memory compression needs a summarization model.
        __init__ calls it when memory compression is on.
        It imports transformers only now and loads the model on CPU; generation on MPS hangs.
        """
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        animate_thinking("Loading memory compression model...", color="status")
        self.tokenizer = AutoTokenizer.from_pretrained(SUMMARY_MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARY_MODEL_NAME)
        self.logger.info("Memory compression system initialized.")

    def get_filename(self) -> str:
        """
        Each session has one save file.
        save_memory and tests call it.
        It makes the file name from the session start time.
        Returns:
            str: file name, for example "memory_2026-10-14_09-00-00.txt".
        """
        return f"memory_{self.session_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    def save_memory(self, agent_type: str = "casual_agent") -> None:
        """
        The interaction class saves each agent conversation when the session ends.
        Interaction.save_session calls it with the agent type.
        It writes the full conversation, with message times, to the agent session folder.
        Args:
            agent_type (str): agent type, used as the folder name, for example "code_agent".
        """
        save_path = os.path.join(self.conversation_folder, agent_type)
        os.makedirs(save_path, exist_ok=True)
        path = os.path.join(save_path, self.get_filename())
        write_json_atomic(path, self.memory)
        self.logger.info(f"Saved memory json at {path}")

    def find_last_session_path(self, path: str) -> str | None:
        """
        Session recovery needs the most recent session file.
        load_memory calls it with the agent session folder.
        It sorts the session file names; the timestamp format makes this a time order.
        Args:
            path (str): agent session folder.
        Returns:
            str | None: file name of the newest session, or None when there is no session.
        """
        sessions = [name for name in os.listdir(path) if name.startswith('memory_') and name.endswith('.txt')]
        if not sessions:
            return None
        last_session = max(sessions)
        self.logger.info(f"Last session found at {last_session}")
        return last_session

    def load_json_file(self, path: str):
        """
        Session recovery reads saved sessions from JSON files.
        load_memory calls it with a session file path.
        It decodes the file, and gives None when it cannot read or decode it.
        Args:
            path (str): session file path.
        Returns:
            Any | None: decoded JSON data, or None on error.
        """
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (OSError, ValueError) as e:
            self.logger.warning(f"Error loading file {path}: {e}")
            return None

    def load_memory(self, agent_type: str = "casual_agent") -> None:
        """
        The interaction class recovers each agent conversation from the last session.
        Interaction.load_last_session and __init__ call it with the agent type.
        It loads the newest valid session, removes an unanswered last user message, and compresses it.
        Args:
            agent_type (str): agent type, used as the folder name, for example "code_agent".
        """
        if self.session_recovered:
            return
        pretty_print(f"Loading {agent_type} past memories... ", color="status")
        save_path = os.path.join(self.conversation_folder, agent_type)
        filename = self.find_last_session_path(save_path) if os.path.isdir(save_path) else None
        if filename is None:
            pretty_print("No memory to load.", color="success")
            return
        history = self.load_json_file(os.path.join(save_path, filename))
        if not is_valid_history(history):
            self.logger.warning(f"Invalid session file {filename}, keeping current memory.")
            pretty_print("Last session memory is unreadable, starting fresh.", color="warning")
            return
        if history[-1]['role'] == 'user':
            history.pop()
        self.memory = history
        self.compress()
        pretty_print("Session recovered successfully", color="success")

    def reset(self, memory: list | None = None) -> None:
        """
        Callers use it to replace the whole conversation.
        Tests and agents call it with a new message list, or with nothing.
        It copies the given messages, or keeps only the system message when no list is given.
        Args:
            memory (list | None): new list of {'role', 'content'} messages. None to keep only the system message.
        """
        self.logger.info("Memory reset performed.")
        if memory is None:
            self.clear()
            return
        self.memory = [dict(message) for message in memory]

    def push(self, role: str, content: str) -> None:
        """
        Agents add each message of the conversation to memory.
        Agents call it with the message role and text.
        It adds the message with its time, then compresses memory when the message is larger than the model context.
        Args:
            role (str): message role: "user", "assistant" or "system".
            content (str): message text.
        """
        if self.memory and self.memory[-1]['content'] == content:
            pretty_print("Warning: same message have been pushed twice to memory", color="error")
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.memory.append({'role': role, 'content': content, 'time': time_str, 'model_used': self.model_provider})
        if self.memory_compression and self.max_ctx_chars and len(content) > self.max_ctx_chars:
            self.logger.info(f"Compressing memory: Content {len(content)} > {self.max_ctx_chars} chars model context.")
            self.compress()

    def clear(self) -> None:
        """
        Agents use it to start a new exchange with the same system prompt.
        Agents and reset call it.
        It removes all messages except the first message when it is the system message.
        """
        self.logger.info("Memory clear performed.")
        self.memory = [message for message in self.memory[:1] if message['role'] == 'system']

    def get(self) -> list:
        """
        Agents send the conversation to the LLM provider.
        Agent.llm_request calls it.
        It gives a copy of the messages with only the role and content keys, which all providers accept.
        Returns:
            list: list of {'role': str, 'content': str} messages.
        """
        return [{'role': message['role'], 'content': message['content']} for message in self.memory]

    def summarize(self, text: str, min_length: int = 64) -> str:
        """
        Memory compression makes long messages shorter.
        compress and compress_text_to_max_ctx call it with one message text.
        It gives a summary of about half the input tokens, or the same text when it is short or no model is loaded.
        Args:
            text (str): text to summarize.
            min_length (int): minimum summary length, in tokens.
        Returns:
            str: summarized text.
        """
        if self.tokenizer is None or self.model is None:
            self.logger.warning("No tokenizer or model to perform summarization.")
            return text
        input_ids = self.tokenizer(text, return_tensors="pt", max_length=SUMMARY_MAX_INPUT_TOKENS, truncation=True)['input_ids']
        input_tokens = input_ids.shape[-1]
        if input_tokens < min_length * 2:
            return text
        summary_ids = self.model.generate(
            input_ids,
            max_length=input_tokens // 2,
            min_length=min_length,
            length_penalty=1.0,
            num_beams=4,
            early_stopping=True
        )
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True).replace('summary:', '').strip()
        self.logger.info(f"Memory summarized from len {len(text)} to {len(summary)}.")
        return summary

    def compress(self) -> None:
        """
        Memory compression keeps the conversation inside the model context.
        push and load_memory call it.
        It summarizes each non-system message that is longer than 1024 characters.
        """
        if self.tokenizer is None or self.model is None:
            self.logger.warning("No tokenizer or model to perform memory compression.")
            return
        for message in self.memory:
            if message['role'] == 'system':
                continue
            if len(message['content']) > COMPRESS_MESSAGE_MIN_CHARS:
                message['content'] = self.summarize(message['content'])

    def trim_text_to_max_ctx(self, text: str) -> str:
        """
        The browser agent must not send a web page that is larger than the model context.
        BrowserAgent.get_page_text and compress_text_to_max_ctx call it with page text.
        It cuts the text to the estimated context size, converted from tokens to characters.
        Args:
            text (str): text to cut.
        Returns:
            str: text that fits the context, or the same text when the context size is unknown.
        """
        return text[:self.max_ctx_chars] if self.max_ctx_chars else text

    def compress_text_to_max_ctx(self, text: str) -> str:
        """
        The browser agent can summarize a web page instead of cutting it.
        BrowserAgent.get_page_text can call it with page text.
        It summarizes the text at most 3 times, stops when a summary is not shorter, then cuts what is still too long.
        Args:
            text (str): text to compress.
        Returns:
            str: text that fits the context, or the same text when no model or context size is available.
        """
        if self.tokenizer is None or self.model is None or not self.max_ctx_chars:
            self.logger.warning("No model or context size to perform text compression.")
            return text
        for _ in range(MAX_SUMMARY_PASSES):
            if len(text) <= self.max_ctx_chars:
                return text
            summary = self.summarize(text)
            if len(summary) >= len(text):
                break
            text = summary
        return self.trim_text_to_max_ctx(text)

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    memory = Memory("You are a helpful assistant.",
                    recover_last_session=False, memory_compression=True)

    memory.push('user', "hello")
    memory.push('assistant', "how can i help you?")
    memory.push('user', "why do i get this cuda error?")
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
    memory.push('assistant', sample_text)

    print("\n---\nmemory before:", memory.get())
    memory.compress()
    print("\n---\nmemory after:", memory.get())
