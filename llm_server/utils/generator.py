import threading
import logging
from abc import abstractmethod

class GenerationState:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_complete_sentence = ""
        self.current_buffer = ""
        self.is_generating = False
    
    def status(self) -> dict:
        return {
            "sentence": self.current_buffer,
            "is_complete": not self.is_generating,
            "last_complete_sentence": self.last_complete_sentence,
            "is_generating": self.is_generating,
        }

class BaseGenerator():
    def __init__(self):
        self.model = None
        self.state = GenerationState()
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def set_model(self, model: str) -> None:
        self.logger.info(f"Model set to {model}")
        self.model = model
    
    def start(self, history: list) -> bool:
        if self.model is None:
            raise Exception("Model not set")
        with self.state.lock:
            if self.state.is_generating:
                return False
            self.state.is_generating = True
            self.logger.info("Starting generation")
            threading.Thread(target=self.generate, args=(history,)).start()
        return True
    
    def get_status(self) -> dict:
        with self.state.lock:
            return self.state.status()

    @abstractmethod
    def generate(self, history: list) -> None:
        """
        Generate text using the model.
        args:
            history: list of strings
        returns:
            None
        """
        pass

if __name__ == "__main__":
    generator = BaseGenerator()
    generator.get_status()