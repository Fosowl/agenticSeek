import readline
from typing import List, Tuple, Type, Dict

from sources.text_to_speech import Speech
from sources.utility import pretty_print, animate_thinking
from sources.router import AgentRouter
from sources.speech_to_text import Speech2Text
import threading

CONFIRMATION_PHRASES = [
    "do it", "go ahead", "execute", "thanks", "thank you",
    "please", "okay", "proceed", "that's all", "that's it", "no more", "stop listening", "end listening", "that's enough",
    "that's good", "all done", "finished", "done", "that's fine", "that's great", "looks good", "sounds good",
    "start", "begin", "get started", "let's go", "let's do it",
]
EXIT_PHRASES = ["exit", "goodbye", "bye", "see you", "quit", "stop", "end", "farewell", "later"]


class Interaction:
    """
    Interaction is a class that handles the interaction between the user and the agents.
    """
    def __init__(self, agents,
                 tts_enabled: bool = True,
                 stt_enabled: bool = True,
                 recover_last_session: bool = False,
                 langs: List[str] = ["en", "zh"]
                ):
        self.is_active = True
        self.current_agent = None
        self.last_query = None
        self.last_answer = None
        self.last_reasoning = None
        self.agents = agents
        self.tts_enabled = tts_enabled
        self.stt_enabled = stt_enabled
        self.recover_last_session = recover_last_session
        self.router = AgentRouter(self.agents, supported_language=langs)
        self.ai_name = self.find_ai_name()
        self.speech = None
        self.stt = None
        self.is_generating = False
        self.languages = langs
        if tts_enabled and not self.in_docker():
            self.initialize_tts()
        if stt_enabled and not self.in_docker():
            self.initialize_stt()
        if recover_last_session:
            self.load_last_session()
        self.emit_status()

    def get_spoken_language(self) -> str:
        """Get the primary TTS language."""
        lang = self.languages[0]
        return lang

    def in_docker(self) -> bool:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("DOCKER_INTERNAL_URL")
        if not url: # running on host
            return False
        return True

    def initialize_tts(self):
        """Initialize TTS, letting the user audition and pick a voice.
        Returns:
            None. Sets self.speech to a ready Speech instance.
        """
        if self.speech:
            return

        animate_thinking("Initializing text-to-speech...", color="status")
        language = self.get_spoken_language()
        voice_idx = self._select_voice_interactively(language)
        self.speech = Speech(enable=self.tts_enabled,
                             language=language,
                             voice_idx=voice_idx)
        self.speech.speak("Voice confirmed. We are online and ready.")


    def _select_voice_interactively(self, language):
        """Let the user audition voices and choose one by index.
        Args:
            language: Spoken language code passed to Speech.
        Returns:
            int: The chosen voice index.
        """
        voice_count = Speech().available_voice_count(language)
        if voice_count <= 1:
            return 0

        SAMPLE_LINE = "Hello, this is how I sound. Should I use this voice?"
        idx = 0
        preview = Speech(enable=True, language=language, voice_idx=idx)
        while True:
            pretty_print(f"Voice {idx + 1}/{voice_count}", color="status")
            preview.set_voice(idx)
            preview.speak(SAMPLE_LINE)
            choice = self._prompt_voice_choice(idx, voice_count)
            if choice == "accept":
                return idx
            idx = self._next_voice_index(choice, idx, voice_count)


    def _prompt_voice_choice(self, current_idx, voice_count):
        """Read and normalize the user's voice-browsing input.

        Args:
            current_idx: Index of the voice just auditioned.
            voice_count: Total number of selectable voices.

        Returns:
            'accept' to keep current_idx, 'next' to advance, or an
            int index to jump to a specific voice.
        """
        pretty_print("[y] keep  [n] next  [number] jump  [q] keep & quit",
                     color="status")
        raw = input().strip().lower()
        if raw in ("y", "yes", "q", ""):
            return "accept"
        if raw in ("n", "no"):
            return "next"
        if raw.isdigit():
            return self._clamp_index(int(raw) - 1, voice_count)
        return "next"


    def _next_voice_index(self, choice, current_idx, voice_count):
        """Resolve the next index from a normalized browsing choice.

        Args:
            choice: 'next' or an explicit int index.
            current_idx: Current voice index.
            voice_count: Total number of selectable voices.

        Returns:
            int: The next voice index, wrapped within range.
        """
        if isinstance(choice, int):
            return choice
        return (current_idx + 1) % voice_count


    @staticmethod
    def _clamp_index(idx, voice_count):
        """Clamp a requested index into the valid voice range."""
        return max(0, min(idx, voice_count - 1))

    def initialize_stt(self):
        """Initialize STT and start listening to the microphone."""
        if self.stt is not None:
            return
        animate_thinking("Initializing speech recognition...", color="status")
        self.stt = Speech2Text(lang="en-us")
        self.stt.start_listening()

    def emit_status(self):
        """Print the current status of agenticSeek."""
        if self.stt_enabled:
            pretty_print("Text-to-speech enabled", color="status")
            pretty_print("Please speak very slowly and clearly for best results.", color="status")
        pretty_print("AgenticSeek is ready.", color="status")

    def find_ai_name(self) -> str:
        """Find the name of the default AI. It is required for STT as a trigger word."""
        ai_name = "jarvis"
        for agent in self.agents:
            if agent.type == "casual_agent":
                ai_name = agent.agent_name
                break
        return ai_name

    def get_last_blocks_result(self) -> List[Dict]:
        """Get the last blocks result."""
        if self.current_agent is None:
            return []
        blks = []
        for agent in self.agents:
            blks.extend(agent.get_blocks_result())
        return blks

    def load_last_session(self):
        """Recover the last session."""
        for agent in self.agents:
            if agent.type == "planner_agent":
                continue
            agent.memory.load_memory(agent.type)

    def save_session(self):
        """Save the current session."""
        for agent in self.agents:
            agent.memory.save_memory(agent.type)

    def read_stdin(self) -> str:
        """Read the input from the user."""
        buffer = ""

        PROMPT = "\033[1;35m➤➤➤ \033[0m"
        while not buffer:
            try:
                buffer = input(PROMPT)
            except EOFError:
                return None
            if buffer == "exit" or buffer == "goodbye":
                return None
        return buffer

    def _last_spoken_text(self) -> str:
        """Return the last text spoken by TTS (for echo filtering)."""
        if self.speech is None:
            return ""
        return getattr(self.speech, "last_spoken_text", "") or ""

    def _has_trigger(self, text: str) -> bool:
        """Check if the AI's wake word appears in the transcript."""
        return self.ai_name.lower() in text.lower()

    def _has_confirmation(self, text: str) -> bool:
        """Check if any confirmation phrase ends the user's turn."""
        lowered = text.lower()
        return any(phrase in lowered for phrase in CONFIRMATION_PHRASES)

    def transcription_job(self) -> str:
        """
        Listen until the wake word is heard, then collect speech until a
        confirmation phrase is detected. Returns the spoken query, or None
        if the user said an exit phrase.
        """
        if self.stt is None:
            self.initialize_stt()

        collected: List[str] = []

        while True:
            result = self.stt.get_result(self._last_spoken_text(), timeout=0.1)
            if not result:
                continue
            text = result.get("text", "").strip()
            if not text:
                continue
            collected.append(text)
            pretty_print(f"Heard: {text}", color="info")

            if self._has_confirmation(text):
                break

        collected.append("\n[User input from Speech to text transcription, may be inaccurate; Guess user intent or ask for clarification.]\n")
        query = " ".join(collected).strip()
        if query.lower() in EXIT_PHRASES:
            return None
        return query

    def get_user(self) -> str:
        """Get the user input from the microphone or the keyboard."""
        if self.stt_enabled:
            query = "TTS transcription of user: " + self.transcription_job()
        else:
            query = self.read_stdin()
        if query is None:
            self.is_active = False
            self.last_query = None
            return None
        self.last_query = query
        return query

    def set_query(self, query: str) -> None:
        """Set the query"""
        self.is_active = True
        self.last_query = query

    async def think(self) -> bool:
        """Request AI agents to process the user input."""
        push_last_agent_memory = False
        if self.last_query is None or len(self.last_query) == 0:
            return False
        agent = self.router.select_agent(self.last_query)
        if agent is None:
            return False
        if self.current_agent != agent and self.last_answer is not None:
            push_last_agent_memory = True
        tmp = self.last_answer
        self.current_agent = agent
        # The stop flag must be reset before each new request. Otherwise, if /stop was used previously, every subsequent request will fail
        agent.stop = False
        self.is_generating = True
        self.last_answer, self.last_reasoning = await agent.process(self.last_query, self.speech)
        self.is_generating = False
        if push_last_agent_memory:
            self.current_agent.memory.push('user', self.last_query)
            self.current_agent.memory.push('assistant', self.last_answer)
        if self.last_answer == tmp:
            self.last_answer = None
        return True

    def speak_answer(self) -> None:
        """Speak the answer to the user in a non-blocking thread."""
        if self.last_query is None:
            return
        if self.tts_enabled and self.last_answer and self.speech:
            def speak_in_thread(speech_instance, text):
                speech_instance.speak(text)
            thread = threading.Thread(target=speak_in_thread, args=(self.speech, self.last_answer))
            thread.start()

    def show_answer(self) -> None:
        """Show the answer to the user."""
        if self.last_query is None:
            return
        if self.current_agent is not None:
            self.current_agent.show_answer()

