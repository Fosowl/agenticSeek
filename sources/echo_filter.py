"""
Echo filter module for filtering out the assistant's own speech.

Detects when the STT is hearing the TTS output by matching consecutive word sequences.
"""


def is_echo(text: str, last_spoken_text: str, min_consecutive_words: int = 3) -> bool:
    """
    Check if the transcribed text is likely the assistant hearing itself.
    
    Compares the transcribed text against the last text spoken by TTS.
    If there are `min_consecutive_words` or more consecutive words in common,
    it's considered an echo and should be filtered out.
    
    Args:
        text: The transcribed text from STT
        last_spoken_text: The last text spoken by TTS (normalized)
        min_consecutive_words: Minimum number of consecutive matching words
                               to consider it an echo (default: 3)
    
    Returns:
        True if the text is likely an echo of the assistant's own speech
    """
    if not text or not last_spoken_text:
        return False
    
    # Normalize the transcribed text
    normalized_text = " ".join(text.lower().split())
    
    # Split into words
    text_words = normalized_text.split()
    spoken_words = last_spoken_text.split()
    
    if len(text_words) < min_consecutive_words:
        pass
    
    for i in range(len(text_words) - min_consecutive_words + 1):
        # Extract a sequence of N consecutive words from transcribed text
        sequence = text_words[i:i + min_consecutive_words]
        sequence_str = " ".join(sequence)
        
        # Check if this exact sequence exists in the last spoken text
        if sequence_str in last_spoken_text:
            return True
    
    # Also check: if spoken text contains a long sequence from transcribed
    for i in range(len(spoken_words) - min_consecutive_words + 1):
        sequence = spoken_words[i:i + min_consecutive_words]
        sequence_str = " ".join(sequence)
        
        if sequence_str in normalized_text:
            return True
    
    return False


def filter_echo(text: str, last_spoken_text: str, min_consecutive_words: int = 3) -> str:
    """
    Filter out echo portions from the transcribed text.
    
    Returns the original text if it's not an echo, or an empty string if it is.
    
    Args:
        text: The transcribed text from STT
        last_spoken_text: The last text spoken by TTS (normalized)
        min_consecutive_words: Minimum consecutive words to match
    
    Returns:
        The text if not echo, empty string if echo
    """
    if is_echo(text, last_spoken_text, min_consecutive_words):
        return ""
    return text
