import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

try:
    client = OpenAI()
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

def split_text(text, max_chars=4000):
    """Splits a long text string into smaller chunks safely."""
    chunks = []
    while len(text) > max_chars:
        split_idx = text.rfind('.', 0, max_chars)
        if split_idx == -1:
            split_idx = text.rfind(' ', 0, max_chars)
        if split_idx == -1:
            split_idx = max_chars
        
        chunks.append(text[:split_idx].strip())
        text = text[split_idx:].strip()
    if text:
        chunks.append(text)
    return chunks

async def generate_speech(text: str, voice: str, filename: str) -> bool:
    """Generates speech using OpenAI's TTS API model."""
    if not client:
        logger.error("OpenAI client is not initialized.")
        return False
        
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(filename)
        return True
    except Exception as e:
        logger.error(f"Error calling OpenAI TTS API: {e}")
        return False

