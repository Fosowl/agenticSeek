import os, sys
import shutil
import textwrap
import traceback
from typing import List, Tuple, Type, Dict, Optional
import datetime
import logging

from termcolor import colored

from sources.errors import AgenticSeekError
from sources.utility import stop_animation
from sources.workspace import runtime_subdir

class Logger:
    def __init__(self, log_filename):
        self.folder = runtime_subdir("logs")
        self.create_folder(self.folder)
        self.log_path = os.path.join(self.folder, log_filename)
        self.enabled = True
        self.logger = None
        self.last_log_msg = ""
        if self.enabled:
            self.create_logging(log_filename)

    def create_logging(self, log_filename):
        self.logger = logging.getLogger(log_filename)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        self.logger.propagate = False
        file_handler = logging.FileHandler(self.log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    
    def create_folder(self, path):
        """Create log dir"""
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True) 
            return True
        except Exception as e:
            self.enabled = False
            return False
    
    def log(self, message, level=logging.INFO):
        if self.last_log_msg == message:
            return
        if self.enabled:
            self.last_log_msg = message
            self.logger.log(level, message)

    def info(self, message):
        self.log(message)

    def error(self, message):
        self.log(message, level=logging.ERROR)

    def warning(self, message):
        self.log(message, level=logging.WARN)

class ErrorLogger:
    """
    Shows an AgenticSeekError as a readable panel (error, plausible causes, fixes)
    and writes the full traceback to logs/errors.log.
    """
    MAX_WIDTH = 100

    def __init__(self):
        self.file_logger = Logger("errors.log")

    def report(self, error: AgenticSeekError, original: Optional[BaseException] = None) -> None:
        """
        Args:
            error: The user-facing error to display.
            original: The exception whose traceback should be logged, when `error` merely wraps it.
        """
        source = original or error
        trace = "".join(traceback.format_exception(type(source), source, source.__traceback__))
        self.file_logger.error(f"{error.title}: {error.message}\n{trace}")
        stop_animation()
        sys.stdout.flush()
        try:
            print(self.render(error), file=sys.stderr, flush=True)
        except UnicodeEncodeError:  # console without box-drawing glyphs
            print(error.summary(), file=sys.stderr, flush=True)

    def render(self, error: AgenticSeekError) -> str:
        columns = shutil.get_terminal_size((self.MAX_WIDTH, 24)).columns
        width = max(40, min(columns, self.MAX_WIDTH)) - 4
        bar = colored("│", "red")

        def body(text: str, indent: str = "", hanging: str = "") -> List[str]:
            wrapped = textwrap.wrap(text, width - len(indent), initial_indent=hanging,
                                    subsequent_indent=" " * len(hanging),
                                    break_long_words=False, break_on_hyphens=False)
            return [f"{bar}  {indent}{line}" for line in wrapped or [""]]

        header = colored("╭─ ", "red") + colored(f"✖ {error.title}", "red", attrs=["bold"])
        if error.context:
            header += colored(f" ─ {error.context}", "dark_grey")
        lines = [header, bar]
        for paragraph in error.message.splitlines() or [""]:
            lines += body(paragraph)
        for heading, color, bullet, items in (("Why this might happen", "yellow", "• ", error.causes),
                                              ("How to fix it", "green", "→ ", error.fixes)):
            if not items:
                continue
            lines += [bar, f"{bar}  " + colored(heading, color, attrs=["bold"])]
            for item in items:
                lines += body(item, indent="  ", hanging=bullet)
        lines.append(bar)
        footer = colored("╰─", "red")
        if self.file_logger.enabled:
            footer += " " + colored(f"Full traceback: {self.file_logger.log_path}", "dark_grey")
        lines.append(footer)
        return "\n".join(lines)

_error_logger: Optional[ErrorLogger] = None

def report_error(error: AgenticSeekError, original: Optional[BaseException] = None) -> None:
    """Display a user-facing error and log its traceback (see ErrorLogger.report)."""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    _error_logger.report(error, original)

def install_excepthook() -> None:
    """Show uncaught AgenticSeekErrors as a panel instead of a traceback; other errors are untouched."""
    previous = sys.excepthook
    if getattr(previous, "agenticseek_hook", False):
        return

    def hook(exc_type, exc, tb):
        if isinstance(exc, AgenticSeekError):
            report_error(exc)
        else:
            previous(exc_type, exc, tb)

    hook.agenticseek_hook = True
    sys.excepthook = hook

if __name__ == "__main__":
    lg = Logger("test.log")
    lg.log("hello")
    lg2 = Logger("toto.log")
    lg2.log("yo")