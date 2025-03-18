from sources.utility import pretty_print
from sources.router import AgentRouter
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class Interaction:
    """
    Interaction is a class that handles the interaction between the user and the agents.
    """
    def __init__(self, agents,
                 tts_enabled: bool = True,
                 stt_enabled: bool = True,
                 recover_last_session: bool = False):
        self.tts_enabled = tts_enabled
        self.agents = agents
        self.current_agent = None
        self.router = AgentRouter(self.agents)
        self.is_active = True
        self.last_query = None
        self.last_answer = None
        self.ai_name = self.find_ai_name()
        self.tts_enabled = tts_enabled
        self.stt_enabled = stt_enabled
        if tts_enabled:
            from sources.text_to_speech import Speech
            self.speech = Speech()
            self.speech.speak("Hello, we are online and ready. What can I do for you ?")
        if recover_last_session:
            self.recover_last_session()

        self.transcriber = None
        self.recorder = None
    
    def find_ai_name(self) -> str:
        """Find the name of the default AI. It is required for STT as a trigger word."""
        ai_name = "jarvis"
        for agent in self.agents:
            if agent.role == "talking":
                ai_name = agent.agent_name
                break
        return ai_name
    
    def recover_last_session(self):
        """Recover the last session."""
        for agent in self.agents:
            agent.memory.load_memory()
    
    def save_session(self):
        """Save the current session."""
        for agent in self.agents:
            agent.memory.save_memory()

    def is_active(self) -> bool:
        return self.is_active
    
    def read_stdin(self) -> str:
        """Read the input from the user."""
        buffer = ""

        PROMPT = "\033[1;35m➤➤➤ \033[0m"
        while buffer == "" or buffer.isascii() == False:
            try:
                buffer = input(PROMPT)
            except EOFError:
                return None
            if buffer == "exit" or buffer == "goodbye":
                return None
        return buffer
    
    def transcription_job(self) -> str:
        """Transcribe the audio from the microphone."""
        if self.stt_enabled:
            from sources.speech_to_text import AudioTranscriber, AudioRecorder
            self.recorder = AudioRecorder(verbose=True)
            self.transcriber = AudioTranscriber(self.ai_name, verbose=True)
            self.transcriber.start()
            self.recorder.start()
            self.recorder.join()
            self.transcriber.join()
            query = self.transcriber.get_transcript()
            return query
        else:
            return None

    def get_user(self) -> str:
        """Get the user input from the microphone or the keyboard."""
        query = None
        if self.stt_enabled:
            query = "TTS transcription of user: " + self.transcription_job()
        else:
            query = self.read_stdin()
        if query is None:
            self.is_active = False
            self.last_query = "Goodbye (exit requested by user, dont think, make answer very short)"
            return None
        self.last_query = query
        return query
    
    def think(self) -> None:
        """Request AI agents to process the user input."""
        if self.last_query is None or len(self.last_query) == 0:
            return
        agent = self.router.select_agent(self.last_query)
        if agent is None:
            return
        if self.current_agent != agent:
            self.current_agent = agent
            # get history from previous agent, good ?
            self.current_agent.memory.push('user', self.last_query)
        if self.tts_enabled:
            self.last_answer, _ = agent.process(self.last_query, self.speech)
        else:
            self.last_answer, _ = agent.process(self.last_query, None)
    
    def show_answer(self) -> None:
        """Show the answer to the user."""
        if self.last_query is None:
            return
        self.current_agent.show_answer()
        if self.tts_enabled:
            self.speech.speak(self.last_answer)
