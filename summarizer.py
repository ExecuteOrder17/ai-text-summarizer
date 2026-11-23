"""The project's original lead-sentence algorithm, independent of the GUI."""
import re

SENTENCE_PATTERN = r"(?<=[.!?])\s+"


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(SENTENCE_PATTERN, text.strip()) if s.strip()]


def summarize(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    sentences = split_sentences(text)
    # Punctuation is already retained by the regex. Add spaces only.
    return text if len(sentences) <= 2 else " ".join(sentences[:2])


def word_count(text: str) -> int:
    return len(text.split())


SAMPLE = (
    "Artificial intelligence helps computers perform tasks that usually require human intelligence. "
    "Text summarization makes long passages shorter by selecting or generating a concise version. "
    "Our project uses Python to split a paragraph into sentences. "
    "It keeps the first two sentences as a simple extractive summary. "
    "The desktop interface makes the process easy to demonstrate. "
    "Everything runs offline, so the text stays on your computer."
)
